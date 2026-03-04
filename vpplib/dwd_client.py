"""
DWD Direct Data Client for vpplib Environment class.

This module provides direct access to DWD Open Data portal without the wetterdienst library,
which has breaking changes and compatibility issues. It implements observation data fetching
and MOSMIX forecast retrieval with intelligent station selection.

Key features:
- Direct DWD Open Data API access (no wetterdienst dependency)
- Observation data: historical & recent measurements
- MOSMIX forecasts: up to 10-day weather forecasts
- Quality-based station selection
- Multi-station data merging
- Intelligent caching with expiration
"""

import io
import os
import re
import json
import time
import math
import shutil
import hashlib
import zipfile
import requests
from pathlib import Path
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Callable, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from lxml import etree
import pandas as pd
import numpy as np
import pytz


# =============================================================================
# Configuration
# =============================================================================

class WeightingStrategy(Enum):
    """Strategy for combining data from multiple stations."""
    INVERSE_DISTANCE = "inverse_distance"
    SIMPLE_AVERAGE = "simple_average"
    NEAREST_ONLY = "nearest_only"
    DATA_COMPLETENESS = "data_completeness"


class DWDConfig:
    """Configuration settings for DWD data fetching."""
    
    # Base URLs
    BASE_URL = "https://opendata.dwd.de"
    CDC_BASE = f"{BASE_URL}/climate_environment/CDC"
    WEATHER_BASE = f"{BASE_URL}/weather"
    
    # Observation data paths
    OBS_BASE = f"{CDC_BASE}/observations_germany/climate"
    OBS_HOURLY = f"{OBS_BASE}/hourly"
    OBS_DAILY = f"{OBS_BASE}/daily"
    OBS_10MIN = f"{OBS_BASE}/10_minutes"
    
    # Forecast data paths
    MOSMIX_BASE = f"{WEATHER_BASE}/local_forecasts/mos"
    MOSMIX_S = f"{MOSMIX_BASE}/MOSMIX_S/all_stations/kml"
    
    # Metadata and documentation
    HELP_URL = f"{CDC_BASE}/help"
    MET_ELEMENT_DEF_URL = f"{WEATHER_BASE}/lib/MetElementDefinition.xml"
    
    # Parameter directory names (DWD naming)
    PARAM_DIRS = {
        'solar': 'solar',
        'wind': 'wind',
        'temperature': 'air_temperature',
        'pressure': 'pressure',
    }
    
    # Parameter codes for observations
    OBS_PARAM_CODES = {
        'solar': 'ST',
        'wind': 'FF',
        'temperature': 'TU',
        'pressure': 'P0',
    }
    
    # MOSMIX parameter codes
    MOSMIX_PARAM_CODES = {
        'temperature': 'TTT',       # Temperature 2m (K)
        'wind_speed': 'FF',         # Wind speed (m/s)
        'wind_direction': 'DD',     # Wind direction (degrees)
        'pressure': 'PPPP',         # Pressure reduced (Pa)
        'radiation_global': 'Rad1h', # Global radiation (kJ/m²)
        'dew_point': 'Td',          # Dew point temperature (K)
    }
    
    # Cache settings
    DEFAULT_CACHE_DIR = ".dwd_cache"
    DEFAULT_CACHE_EXPIRY_HOURS = 24
    MISSING_VALUE_INDICATOR = -999
    
    # MOSMIX files
    MOSMIX_LATEST_FILE = "MOSMIX_S_LATEST_240.kmz"
    
    @classmethod
    def get_obs_url(cls, parameter: str, resolution: str = "10_minutes") -> str:
        """Get observation data URL for a parameter."""
        if parameter == 'pressure' and resolution == '10_minutes':
            param_dir = 'air_temperature'
        else:
            param_dir = cls.PARAM_DIRS.get(parameter)
            if not param_dir:
                raise ValueError(f"Unknown parameter: {parameter}")
        
        if resolution == "hourly":
            base = cls.OBS_HOURLY
        elif resolution == "daily":
            base = cls.OBS_DAILY
        elif resolution == "10_minutes":
            base = cls.OBS_10MIN
        else:
            raise ValueError(f"Unknown resolution: {resolution}")
        
        return f"{base}/{param_dir}"
    
    @classmethod
    def get_station_description_filename(cls, parameter: str, resolution: str = "hourly") -> str:
        """Get station description filename for a parameter."""
        if resolution == '10_minutes':
            special_codes = {
                'solar': 'sd',
                'wind': 'fx',
                'temperature': 'tu',
                'pressure': 'tu'
            }
            if parameter in special_codes:
                return f"zehn_min_{special_codes[parameter]}_Beschreibung_Stationen.txt"
        
        param_to_code = {
            'solar': 'ST',
            'wind': 'FF',
            'temperature': 'TU',
            'pressure': 'P0'
        }
        
        code = param_to_code.get(parameter, parameter.upper())
        
        if resolution == "hourly":
            time_str = "Stundenwerte"
        elif resolution == "daily":
            time_str = "Tageswerte"
        else:
            time_str = "Stundenwerte"
        
        return f"{code}_{time_str}_Beschreibung_Stationen.txt"
    
    @classmethod
    def get_param_code(cls, parameter: str, resolution: str) -> str:
        """Get the parameter code for data files."""
        if parameter == 'pressure' and resolution == '10_minutes':
            return 'TU'
        return cls.OBS_PARAM_CODES.get(parameter, parameter.upper())


# =============================================================================
# Cache Manager
# =============================================================================

class CacheManager:
    """Manages local file cache with expiration."""
    
    def __init__(self, cache_dir: str = ".dwd_cache", default_expiry_hours: float = 24):
        self.cache_dir = Path(cache_dir)
        self.default_expiry_hours = default_expiry_hours
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_metadata(self):
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except IOError:
            pass
    
    def _get_cache_key(self, url: str, params: Optional[Dict] = None) -> str:
        key_string = url
        if params:
            key_string += json.dumps(params, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str, extension: str = "") -> Path:
        return self.cache_dir / f"{cache_key}{extension}"
    
    def is_valid(self, cache_key: str, expiry_hours: Optional[float] = None) -> bool:
        if cache_key not in self.metadata:
            return False
        
        metadata = self.metadata[cache_key]
        cached_time = metadata.get('timestamp', 0)
        
        cache_path = self._get_cache_path(cache_key, metadata.get('extension', ''))
        if not cache_path.exists():
            return False
        
        if expiry_hours is None:
            expiry_hours = self.default_expiry_hours
        
        if expiry_hours <= 0:
            return True
        
        age_hours = (time.time() - cached_time) / 3600
        return age_hours < expiry_hours
    
    def get(self, url: str, params: Optional[Dict] = None,
            expiry_hours: Optional[float] = None, binary: bool = False) -> Optional[Any]:
        cache_key = self._get_cache_key(url, params)
        
        if not self.is_valid(cache_key, expiry_hours):
            return None
        
        metadata = self.metadata[cache_key]
        cache_path = self._get_cache_path(cache_key, metadata.get('extension', ''))
        
        try:
            mode = 'rb' if binary else 'r'
            encoding = None if binary else 'utf-8'
            with open(cache_path, mode, encoding=encoding) as f:
                return f.read()
        except IOError:
            return None
    
    def set(self, url: str, content: Any, params: Optional[Dict] = None,
            extension: str = "", binary: bool = False):
        cache_key = self._get_cache_key(url, params)
        cache_path = self._get_cache_path(cache_key, extension)
        
        try:
            mode = 'wb' if binary else 'w'
            encoding = None if binary else 'utf-8'
            with open(cache_path, mode, encoding=encoding) as f:
                f.write(content)
            
            self.metadata[cache_key] = {
                'url': url,
                'params': params,
                'timestamp': time.time(),
                'extension': extension,
                'size': len(content) if isinstance(content, (str, bytes)) else 0
            }
            self._save_metadata()
        except IOError:
            pass
    
    def get_or_fetch(self, url: str, fetch_func: Callable,
                     params: Optional[Dict] = None,
                     expiry_hours: Optional[float] = None,
                     extension: str = "", binary: bool = False,
                     force_refresh: bool = False) -> Any:
        if not force_refresh:
            cached = self.get(url, params, expiry_hours, binary)
            if cached is not None:
                return cached
        
        content = fetch_func()
        self.set(url, content, params, extension, binary)
        return content
    
    def clear_all(self, confirm: bool = False):
        if not confirm:
            raise ValueError("Must set confirm=True to clear entire cache")
        
        try:
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.metadata = {}
            self._save_metadata()
        except OSError:
            pass


# =============================================================================
# Downloader
# =============================================================================

class Downloader:
    """Handles HTTP downloads with retry logic and caching."""
    
    def __init__(self, cache_manager: Optional[CacheManager] = None,
                 timeout: int = 30, max_retries: int = 3, retry_delay: float = 1.0):
        self.cache_manager = cache_manager or CacheManager()
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def download(self, url: str, binary: bool = True, force_refresh: bool = False,
                expiry_hours: Optional[float] = None) -> bytes:
        extension = Path(url).suffix
        
        if not force_refresh:
            cached = self.cache_manager.get(url, expiry_hours=expiry_hours, binary=binary)
            if cached is not None:
                return cached
        
        content = self._download_with_retry(url, binary)
        self.cache_manager.set(url, content, extension=extension, binary=binary)
        return content
    
    def _download_with_retry(self, url: str, binary: bool = True) -> bytes:
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, timeout=self.timeout, stream=True)
                response.raise_for_status()
                
                chunks = []
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        chunks.append(chunk)
                
                content = b''.join(chunks)
                
                if not binary:
                    try:
                        return content.decode('utf-8')
                    except UnicodeDecodeError:
                        return content.decode('latin-1')
                
                return content
                
            except requests.RequestException as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
        
        raise RuntimeError(f"Failed to download {url} after {self.max_retries} attempts: {last_error}")
    
    def list_directory(self, url: str) -> list:
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            content = response.text
            files = []
            pattern = r'<a href="([^"]+)"'
            matches = re.findall(pattern, content)
            
            for match in matches:
                if match.startswith('..') or match.startswith('/') or '://' in match:
                    continue
                files.append(match)
            
            return files
            
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to list directory {url}: {e}")
    
    def check_file_exists(self, url: str) -> bool:
        for attempt in range(self.max_retries):
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                return response.status_code == 200
            except requests.RequestException:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return False
        return False


# =============================================================================
# Station Management
# =============================================================================

@dataclass
class Station:
    """Represents a DWD weather station."""
    station_id: str
    name: str
    latitude: float
    longitude: float
    elevation: float
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    parameter: str
    distance_km: Optional[float] = None
    quality_score: Optional[float] = None
    combined_score: Optional[float] = None
    
    def is_active(self, date: Optional[datetime] = None) -> bool:
        if date is None:
            date = datetime.now()
        if self.start_date and date < self.start_date:
            return False
        if self.end_date and date > self.end_date:
            return False
        return True
    
    def __hash__(self) -> int:
        return hash((self.station_id, self.parameter))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Station):
            return False
        return self.station_id == other.station_id and self.parameter == other.parameter


class StationManager:
    """Manages DWD station metadata and search functionality."""
    
    def __init__(self, cache_manager: Optional[CacheManager] = None, downloader=None):
        self.cache_manager = cache_manager or CacheManager()
        self.downloader = downloader
        self.stations: Dict[str, Dict[str, Station]] = {}
        self._loaded_parameters: Set[str] = set()
    
    def load_stations(self, parameter: str, resolution: str = "hourly",
                     force_refresh: bool = False) -> Dict[str, Station]:
        cache_key = f"{parameter}_{resolution}"
        
        if cache_key in self._loaded_parameters and not force_refresh:
            return self.stations.get(parameter, {})
        
        base_url = DWDConfig.get_obs_url(parameter, resolution)
        filename = DWDConfig.get_station_description_filename(parameter, resolution)
        
        urls_to_try = [
            f"{base_url}/{filename}",
            f"{base_url}/recent/{filename}",
            f"{base_url}/historical/{filename}",
            f"{DWDConfig.HELP_URL}/{filename}",
        ]
        
        content = None
        last_error = None
        
        for url in urls_to_try:
            try:
                content = self.cache_manager.get_or_fetch(
                    url=url,
                    fetch_func=lambda u=url: self._fetch_station_file(u),
                    expiry_hours=24 * 7,
                    extension=".txt",
                    binary=False,
                    force_refresh=force_refresh
                )
                break
            except Exception as e:
                last_error = e
                continue
        
        if content is None:
            raise RuntimeError(f"Failed to fetch station file for {parameter}: {last_error}")
        
        stations = self._parse_station_file(content, parameter)
        
        if parameter not in self.stations:
            self.stations[parameter] = {}
        
        self.stations[parameter] = stations
        self._loaded_parameters.add(cache_key)
        
        return stations
    
    def _fetch_station_file(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content.decode('latin-1')
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch station file from {url}: {e}")
    
    def _parse_station_file(self, content: str, parameter: str) -> Dict[str, Station]:
        stations = {}
        lines = content.strip().split('\n')
        
        data_start = 2
        for i, line in enumerate(lines):
            if line.strip().startswith('---'):
                data_start = i + 1
                break
        
        for line in lines[data_start:]:
            line = line.strip()
            if not line:
                continue
            
            try:
                parts = [p for p in line.split() if p]
                
                if len(parts) < 7:
                    continue
                
                station_id = parts[0].strip()
                date_from_str = parts[1].strip()
                date_to_str = parts[2].strip()
                elevation = float(parts[3])
                latitude = float(parts[4])
                longitude = float(parts[5])
                name_parts = ' '.join(parts[6:]).rsplit(maxsplit=1)
                name = name_parts[0].strip() if len(name_parts) > 1 else ' '.join(parts[6:])
                
                start_date = None
                end_date = None
                
                try:
                    if date_from_str and date_from_str.isdigit() and len(date_from_str) == 8:
                        start_date = datetime.strptime(date_from_str, '%Y%m%d')
                except ValueError:
                    pass
                
                try:
                    if date_to_str and date_to_str.isdigit() and len(date_to_str) == 8:
                        end_date = datetime.strptime(date_to_str, '%Y%m%d')
                except ValueError:
                    pass
                
                station = Station(
                    station_id=station_id,
                    name=name,
                    latitude=latitude,
                    longitude=longitude,
                    elevation=elevation,
                    start_date=start_date,
                    end_date=end_date,
                    parameter=parameter
                )
                
                stations[station_id] = station
                
            except (ValueError, IndexError):
                continue
        
        return stations
    
    def find_nearest_stations(self, latitude: float, longitude: float,
                             parameter: str, n: int = 5,
                             max_distance_km: Optional[float] = None,
                             resolution: str = "hourly",
                             active_only: bool = False,
                             date: Optional[datetime] = None) -> List[Station]:
        if parameter not in self.stations:
            self.load_stations(parameter, resolution)
        
        stations_list = list(self.stations[parameter].values())
        
        if active_only:
            stations_list = [s for s in stations_list if s.is_active(date)]
        
        for station in stations_list:
            station.distance_km = self._haversine_distance(
                latitude, longitude, station.latitude, station.longitude
            )
        
        stations_list.sort(key=lambda s: s.distance_km)
        
        if max_distance_km is not None:
            stations_list = [s for s in stations_list if s.distance_km <= max_distance_km]
        
        return stations_list[:n]
    
    def get_station_by_id(self, station_id: str, parameter: str,
                         resolution: str = "hourly") -> Optional[Station]:
        if parameter not in self.stations:
            self.load_stations(parameter, resolution)
        return self.stations[parameter].get(station_id)
    
    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c


# =============================================================================
# Observation Parser
# =============================================================================

class ObservationParser:
    """Parses DWD observation data from ZIP archives."""
    
    def __init__(self, downloader: Optional[Downloader] = None):
        self.downloader = downloader or Downloader()
    
    def fetch_observations(self, station_id: str, parameter: str,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          resolution: str = "10_minutes",
                          force_refresh: bool = False) -> Tuple[pd.DataFrame, Dict]:
        base_url = DWDConfig.get_obs_url(parameter, resolution)
        param_code = DWDConfig.get_param_code(parameter, resolution)
        
        metadata = {
            'station_id': station_id,
            'parameter': parameter,
            'sources': [],
            'warnings': []
        }
        
        dfs = []
        
        # Try recent data
        recent_df = None
        try:
            recent_df = self._fetch_recent_data(base_url, station_id, param_code, parameter, resolution, force_refresh)
            if recent_df is not None and not recent_df.empty:
                dfs.append(recent_df)
                metadata['sources'].append('recent')
                metadata['recent_start'] = recent_df.index.min()
                metadata['recent_end'] = recent_df.index.max()
        except Exception as e:
            metadata['warnings'].append(f"Could not fetch recent data: {e}")
        
        # Determine if historical needed
        need_historical = False
        if start_date is not None and recent_df is not None and not recent_df.empty:
            if start_date < recent_df.index.min():
                need_historical = True
        elif start_date is not None and (recent_df is None or recent_df.empty):
            need_historical = True
        
        # Fetch historical if needed
        if need_historical:
            try:
                historical_df = self._fetch_historical_data(base_url, station_id, param_code, parameter, resolution, force_refresh)
                if historical_df is not None and not historical_df.empty:
                    dfs.append(historical_df)
                    metadata['sources'].append('historical')
                    metadata['historical_start'] = historical_df.index.min()
                    metadata['historical_end'] = historical_df.index.max()
            except Exception as e:
                metadata['warnings'].append(f"Could not fetch historical data: {e}")
        
        if not dfs:
            return pd.DataFrame(), metadata
        
        if len(dfs) == 1:
            combined = dfs[0]
        else:
            combined = pd.concat(dfs)
            combined = combined[~combined.index.duplicated(keep='first')]
            combined = combined.sort_index()
            if 'recent_start' in metadata and 'historical_end' in metadata:
                metadata['boundary_date'] = metadata['recent_start']
        
        if not combined.empty:
            metadata['available_start'] = combined.index.min()
            metadata['available_end'] = combined.index.max()
        
        # Filter by date range
        if start_date is not None:
            # Ensure timezone compatibility
            if combined.index.tz is not None and start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=pytz.UTC)
            elif combined.index.tz is None and start_date.tzinfo is not None:
                start_date = start_date.replace(tzinfo=None)
            combined = combined[combined.index >= start_date]
        if end_date is not None:
            if combined.index.tz is not None and end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=pytz.UTC)
            elif combined.index.tz is None and end_date.tzinfo is not None:
                end_date = end_date.replace(tzinfo=None)
            combined = combined[combined.index <= end_date]
        
        return combined, metadata
    
    def _fetch_recent_data(self, base_url: str, station_id: str,
                          param_code: str, parameter: str, resolution: str,
                          force_refresh: bool = False) -> Optional[pd.DataFrame]:
        if resolution == "10_minutes":
            if param_code == "ST":
                filename = f"10minutenwerte_SOLAR_{station_id:0>5}_akt.zip"
            elif param_code == "FF":
                filename = f"10minutenwerte_wind_{station_id:0>5}_akt.zip"
            else:
                filename = f"10minutenwerte_{param_code}_{station_id:0>5}_akt.zip"
        else:
            if resolution == "hourly":
                time_str = "stundenwerte"
            elif resolution == "daily":
                time_str = "tageswerte"
            else:
                time_str = "stundenwerte"
            filename = f"{time_str}_{param_code}_{station_id:0>5}_akt.zip"
        
        url = f"{base_url}/recent/{filename}"
        
        try:
            zip_content = self.downloader.download(url, binary=True, force_refresh=force_refresh)
            return self._parse_zip_data(zip_content, param_code, parameter)
        except Exception as e:
            return None
    
    def _fetch_historical_data(self, base_url: str, station_id: str,
                              param_code: str, parameter: str, resolution: str,
                              force_refresh: bool = False) -> Optional[pd.DataFrame]:
        try:
            files = self.downloader.list_directory(f"{base_url}/historical/")
        except Exception:
            return None
        
        if resolution == "10_minutes":
            if param_code == "ST":
                pattern = f"10minutenwerte_SOLAR_{station_id:0>5}_.*_hist\\.zip"
            elif param_code == "FF":
                pattern = f"10minutenwerte_wind_{station_id:0>5}_.*_hist\\.zip"
            else:
                pattern = f"10minutenwerte_{param_code}_{station_id:0>5}_.*_hist\\.zip"
        else:
            if resolution == "hourly":
                time_str = "stundenwerte"
            elif resolution == "daily":
                time_str = "tageswerte"
            else:
                time_str = "stundenwerte"
            pattern = f"{time_str}_{param_code}_{station_id:0>5}_.*_hist\\.zip"
        
        matching_files = [f for f in files if re.match(pattern, f)]
        
        if not matching_files:
            return None
        
        filename = matching_files[0]
        url = f"{base_url}/historical/{filename}"
        
        try:
            zip_content = self.downloader.download(url, binary=True, force_refresh=force_refresh)
            return self._parse_zip_data(zip_content, param_code, parameter)
        except Exception:
            return None
    
    def _parse_zip_data(self, zip_content: bytes, param_code: str, parameter: str) -> pd.DataFrame:
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
            data_files = [f for f in zf.namelist() if f.startswith('produkt_')]
            
            if not data_files:
                raise ValueError("No data file found in ZIP archive")
            
            with zf.open(data_files[0]) as f:
                df = pd.read_csv(
                    f,
                    sep=';',
                    encoding='latin-1',
                    na_values=['-999', -999, '-999.0'],
                    skipinitialspace=True
                )
        
        # Parse timestamp
        if 'MESS_DATUM' in df.columns:
            df['datetime'] = pd.to_datetime(df['MESS_DATUM'], format='%Y%m%d%H%M', errors='coerce')
            if df['datetime'].isna().all():
                df['datetime'] = pd.to_datetime(df['MESS_DATUM'], format='%Y%m%d%H', errors='coerce')
            df.set_index('datetime', inplace=True)
            df.drop('MESS_DATUM', axis=1, inplace=True, errors='ignore')
        elif 'MESS_DATUM_BEGINN' in df.columns:
            df['datetime'] = pd.to_datetime(df['MESS_DATUM_BEGINN'], format='%Y%m%d%H%M', errors='coerce')
            if df['datetime'].isna().all():
                df['datetime'] = pd.to_datetime(df['MESS_DATUM_BEGINN'], format='%Y%m%d%H', errors='coerce')
            df.set_index('datetime', inplace=True)
            df.drop('MESS_DATUM_BEGINN', axis=1, inplace=True, errors='ignore')
        
        # Clean up
        meta_cols = ['STATIONS_ID', 'eor', 'MESS_DATUM_ENDE']
        df.drop(meta_cols, axis=1, inplace=True, errors='ignore')
        
        # Rename QN columns
        qn_cols = [col for col in df.columns if col.startswith('QN')]
        if qn_cols:
            rename_dict = {col: f"{col}_{parameter}" for col in qn_cols}
            df.rename(columns=rename_dict, inplace=True)
        
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.columns = df.columns.str.strip()
        
        return df


# =============================================================================
# Forecast Parser (MOSMIX)
# =============================================================================

class ForecastParser:
    """Parses MOSMIX forecast data from KMZ/KML files."""
    
    def __init__(self, downloader: Optional[Downloader] = None):
        self.downloader = downloader or Downloader()
    
    def fetch_forecast(self, station_ids: Optional[List[str]] = None,
                      parameters: Optional[List[str]] = None,
                      force_refresh: bool = False) -> pd.DataFrame:
        url = f"{DWDConfig.MOSMIX_S}/{DWDConfig.MOSMIX_LATEST_FILE}"
        
        kmz_content = self.downloader.download(url, binary=True, force_refresh=force_refresh, expiry_hours=1)
        kml_root = self._extract_kml_from_kmz(kmz_content)
        
        if parameters is None:
            parameters = list(DWDConfig.MOSMIX_PARAM_CODES.values())
        
        forecast_data = self._parse_kml_forecast(kml_root, station_ids, parameters)
        return forecast_data
    
    def _extract_kml_from_kmz(self, kmz_content: bytes) -> etree._Element:
        with zipfile.ZipFile(io.BytesIO(kmz_content)) as kmz:
            kml_files = [f for f in kmz.namelist() if f.endswith('.kml')]
            
            if not kml_files:
                raise ValueError("No KML file found in KMZ archive")
            
            with kmz.open(kml_files[0]) as kml_file:
                kml_content = kml_file.read()
        
        root = etree.fromstring(kml_content)
        return root
    
    def _parse_kml_forecast(self, kml_root: etree._Element,
                           station_ids: Optional[List[str]],
                           parameters: List[str]) -> pd.DataFrame:
        namespaces = {
            'kml': 'http://www.opengis.net/kml/2.2',
            'dwd': 'https://opendata.dwd.de/weather/lib/pointforecast_dwd_extension_V1_0.xsd'
        }
        
        timestamps = self._extract_timestamps(kml_root, namespaces)
        placemarks = kml_root.findall('.//kml:Placemark', namespaces)
        
        all_data = []
        
        for placemark in placemarks:
            station_name = placemark.find('.//kml:name', namespaces)
            if station_name is None:
                continue
            
            station_id = station_name.text.strip()
            
            if station_ids and station_id not in station_ids:
                continue
            
            coords_elem = placemark.find('.//kml:coordinates', namespaces)
            coordinates = None
            if coords_elem is not None and coords_elem.text:
                coord_parts = coords_elem.text.strip().split(',')
                if len(coord_parts) >= 2:
                    coordinates = {
                        'longitude': float(coord_parts[0]),
                        'latitude': float(coord_parts[1])
                    }
            
            extended_data = placemark.find('.//kml:ExtendedData', namespaces)
            if extended_data is None:
                continue
            
            station_data = self._extract_station_forecast(extended_data, namespaces, parameters, timestamps)
            
            for record in station_data:
                record['station_id'] = station_id
                if coordinates:
                    record.update(coordinates)
            
            all_data.extend(station_data)
        
        if not all_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(all_data)
        
        if 'datetime' in df.columns:
            df.set_index('datetime', inplace=True)
        
        return df
    
    def _extract_timestamps(self, kml_root: etree._Element, namespaces: Dict[str, str]) -> List[datetime]:
        timestamps = []
        timesteps_elem = kml_root.find('.//dwd:ForecastTimeSteps', namespaces)
        
        if timesteps_elem is not None and timesteps_elem.text:
            time_strings = timesteps_elem.text.strip().split()
            for ts in time_strings:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    timestamps.append(dt)
                except ValueError:
                    continue
        
        return timestamps
    
    def _extract_station_forecast(self, extended_data: etree._Element,
                                  namespaces: Dict[str, str],
                                  parameters: List[str],
                                  timestamps: List[datetime]) -> List[Dict]:
        records = []
        forecasts = extended_data.findall('.//dwd:Forecast', namespaces)
        
        for forecast in forecasts:
            param_elem = forecast.get(f"{{{namespaces['dwd']}}}elementName")
            if param_elem is None:
                param_elem_node = forecast.find('.//dwd:elementName', namespaces)
                if param_elem_node is not None:
                    param_elem = param_elem_node.text
            
            if not param_elem or param_elem not in parameters:
                continue
            
            values_elem = forecast.find('.//dwd:value', namespaces)
            if values_elem is None or not values_elem.text:
                continue
            
            values = []
            for v in values_elem.text.strip().split():
                try:
                    values.append(float(v))
                except ValueError:
                    values.append(None)
            
            for timestamp, value in zip(timestamps, values):
                record = None
                for r in records:
                    if r.get('datetime') == timestamp:
                        record = r
                        break
                
                if record is None:
                    record = {'datetime': timestamp}
                    records.append(record)
                
                record[param_elem] = value
        
        return records
    
    def get_forecast_for_location(self, latitude: float, longitude: float,
                                  parameters: Optional[List[str]] = None,
                                  force_refresh: bool = False) -> pd.DataFrame:
        df = self.fetch_forecast(parameters=parameters, force_refresh=force_refresh)
        
        if df.empty:
            return df
        
        if 'latitude' in df.columns and 'longitude' in df.columns:
            min_distance = float('inf')
            nearest_station = None
            
            for station_id in df['station_id'].unique():
                station_data = df[df['station_id'] == station_id].iloc[0]
                station_lat = station_data['latitude']
                station_lon = station_data['longitude']
                
                distance = StationManager._haversine_distance(latitude, longitude, station_lat, station_lon)
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_station = station_id
            
            return df[df['station_id'] == nearest_station].copy()
        
        return df


# =============================================================================
# Main DWD Client
# =============================================================================

class DWDClient:
    """
    Main client for fetching DWD meteorological data.
    
    This replaces the wetterdienst library with direct DWD Open Data access.
    """
    
    def __init__(self, cache_dir: str = ".dwd_cache",
                 cache_expiry_hours: float = 24,
                 timezone: str = "Europe/Berlin"):
        self.cache_manager = CacheManager(cache_dir, cache_expiry_hours)
        self.downloader = Downloader(self.cache_manager)
        self.station_manager = StationManager(self.cache_manager, self.downloader)
        self.obs_parser = ObservationParser(self.downloader)
        self.forecast_parser = ForecastParser(self.downloader)
        self.timezone = timezone
    
    def get_observations(self, latitude: float, longitude: float,
                        parameters: List[str],
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        resolution: str = "10_minutes",
                        max_distance_km: float = 50,
                        n_stations: int = 5,
                        station_id: Optional[str] = None,
                        min_quality_per_parameter: int = 80,
                        force_refresh: bool = False) -> Tuple[pd.DataFrame, Dict]:
        """
        Get observation data for a location.
        
        Parameters
        ----------
        latitude, longitude : float
            Location coordinates
        parameters : List[str]
            List of parameters ('solar', 'wind', 'temperature', 'pressure')
        start_date, end_date : datetime, optional
            Date range
        resolution : str
            Time resolution ('10_minutes', 'hourly', 'daily')
        max_distance_km : float
            Maximum station distance
        n_stations : int
            Number of stations to try per parameter
        station_id : str, optional
            Specific station ID to use
        min_quality_per_parameter : int
            Minimum percentage of valid data required
        force_refresh : bool
            Force re-download
            
        Returns
        -------
        Tuple[pd.DataFrame, Dict]
            DataFrame with data, metadata dict with station info
        """
        metadata = {
            'location': {'latitude': latitude, 'longitude': longitude},
            'parameters': parameters,
            'stations_used': {},
            'warnings': [],
            'station_type': 'OBSERVATION'
        }
        
        # Parameter mappings for vpplib
        param_to_dwd_columns = {
            'solar': {
                'ghi': ['GS_10', 'FG_LBERG', 'ATMO_STRAHL'],
                'dhi': ['DS_10', 'DIFFUS_HIMMEL_KW_J'],
            },
            'temperature': {
                'temperature': ['TT_10', 'TT_TU', 'TTT'],
            },
            'pressure': {
                'pressure': ['PP_10', 'P0', 'P', 'PPPP'],
            },
            'wind': {
                'wind_speed': ['FF_10', 'FF', 'F'],
            }
        }
        
        combined_data = {}
        valid_station_found = False
        selected_station_metadata = None
        
        for param in parameters:
            # Find stations
            if station_id:
                stations = []
                station = self.station_manager.get_station_by_id(station_id, param, resolution)
                if station:
                    station.distance_km = StationManager._haversine_distance(
                        latitude, longitude, station.latitude, station.longitude
                    )
                    stations = [station]
            else:
                stations = self.station_manager.find_nearest_stations(
                    latitude, longitude, param,
                    n=n_stations,
                    max_distance_km=max_distance_km,
                    resolution=resolution,
                    active_only=False
                )
            
            if not stations:
                metadata['warnings'].append(f"No stations found for parameter '{param}'")
                continue
            
            # Try stations until we find one with valid data
            for station in stations:
                try:
                    df, obs_meta = self.obs_parser.fetch_observations(
                        station.station_id, param,
                        start_date, end_date,
                        resolution, force_refresh=force_refresh
                    )
                    
                    if obs_meta.get('warnings'):
                        metadata['warnings'].extend(obs_meta['warnings'])
                    
                    if df.empty:
                        continue
                    
                    # Calculate quality
                    valid_count = df.notna().sum().sum()
                    total_count = len(df) * len(df.columns)
                    quality = (valid_count / total_count * 100) if total_count > 0 else 0
                    
                    if quality >= min_quality_per_parameter:
                        # Rename columns to expected names
                        if param in param_to_dwd_columns:
                            for target_col, source_cols in param_to_dwd_columns[param].items():
                                for src_col in source_cols:
                                    if src_col in df.columns:
                                        combined_data[target_col] = df[src_col]
                                        break
                        else:
                            for col in df.columns:
                                if not col.startswith('QN'):
                                    combined_data[col] = df[col]
                        
                        metadata['stations_used'][param] = {
                            'station_id': station.station_id,
                            'name': station.name,
                            'distance_km': station.distance_km,
                            'latitude': station.latitude,
                            'longitude': station.longitude,
                            'height': station.elevation,
                            'quality': round(quality, 1)
                        }
                        
                        if selected_station_metadata is None:
                            selected_station_metadata = {
                                'station_id': station.station_id,
                                'name': station.name,
                                'latitude': station.latitude,
                                'longitude': station.longitude,
                                'height': station.elevation,
                                'distance': station.distance_km
                            }
                        
                        valid_station_found = True
                        break
                        
                except Exception as e:
                    metadata['warnings'].append(f"Failed to fetch {param} from station {station.station_id}: {e}")
        
        if not combined_data:
            raise ValueError("No valid station data found!")
        
        # Create combined DataFrame
        result_df = pd.DataFrame(combined_data)
        
        # Add station metadata
        if selected_station_metadata:
            metadata['selected_station'] = selected_station_metadata
        
        return result_df, metadata
    
    def get_forecast(self, latitude: float, longitude: float,
                    parameters: List[str],
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None,
                    station_id: Optional[str] = None,
                    force_refresh: bool = False) -> Tuple[pd.DataFrame, Dict]:
        """
        Get MOSMIX forecast data for a location.
        
        Parameters
        ----------
        latitude, longitude : float
            Location coordinates
        parameters : List[str]
            List of parameters ('solar', 'wind', 'temperature', 'pressure')
        start_date, end_date : datetime, optional
            Date range (for filtering)
        station_id : str, optional
            Specific MOSMIX station ID
        force_refresh : bool
            Force re-download
            
        Returns
        -------
        Tuple[pd.DataFrame, Dict]
            DataFrame with forecast, metadata dict
        """
        metadata = {
            'location': {'latitude': latitude, 'longitude': longitude},
            'parameters': parameters,
            'warnings': [],
            'station_type': 'MOSMIX'
        }
        
        # Map vpplib parameters to MOSMIX codes
        mosmix_params = []
        param_mapping = {
            'solar': ['Rad1h'],  # GHI in kJ/m²
            'temperature': ['TTT'],  # Temperature in K
            'pressure': ['PPPP'],  # Pressure in Pa
            'wind': ['FF'],  # Wind speed in m/s
            'dew_point': ['Td'],  # Dew point in K
        }
        
        for param in parameters:
            if param in param_mapping:
                mosmix_params.extend(param_mapping[param])
            else:
                mosmix_params.append(param)
        
        # Fetch forecast
        try:
            if station_id:
                df = self.forecast_parser.fetch_forecast(
                    station_ids=[station_id],
                    parameters=mosmix_params,
                    force_refresh=force_refresh
                )
            else:
                df = self.forecast_parser.get_forecast_for_location(
                    latitude, longitude,
                    parameters=mosmix_params,
                    force_refresh=force_refresh
                )
        except Exception as e:
            metadata['warnings'].append(f"Failed to fetch forecast: {e}")
            return pd.DataFrame(), metadata
        
        if df.empty:
            metadata['warnings'].append("No forecast data available")
            return df, metadata
        
        # Record station info
        if 'station_id' in df.columns:
            metadata['station_id'] = df['station_id'].iloc[0]
            metadata['selected_station'] = {
                'station_id': metadata['station_id'],
                'latitude': df['latitude'].iloc[0] if 'latitude' in df.columns else latitude,
                'longitude': df['longitude'].iloc[0] if 'longitude' in df.columns else longitude,
            }
        
        # Rename columns to expected format
        rename_map = {
            'Rad1h': 'ghi',
            'TTT': 'temperature',
            'PPPP': 'pressure',
            'FF': 'wind_speed',
            'Td': 'dew_point',
        }
        
        df = df.rename(columns=rename_map)
        
        # Drop non-data columns
        drop_cols = ['station_id', 'latitude', 'longitude']
        df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore')
        
        # Filter by date range
        if start_date is not None:
            if df.index.tz is not None and start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=pytz.UTC)
            df = df[df.index >= start_date]
        if end_date is not None:
            if df.index.tz is not None and end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=pytz.UTC)
            df = df[df.index <= end_date]
        
        return df, metadata
    
    def clear_cache(self, confirm: bool = False):
        """Clear all cached data."""
        self.cache_manager.clear_all(confirm=confirm)
