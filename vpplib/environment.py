# -*- coding: utf-8 -*-
"""Environment Module.

This module contains the Environment class, which defines external influences on the
virtual power plant system to be simulated. The Environment class provides weather data,
location information, and regulatory influences for the simulation.

The Environment class handles time-related settings, weather data retrieval and processing,
and provides this data to the components of the virtual power plant for simulation.
"""

import pandas as pd
import os
import zoneinfo
import polars as pl
import datetime
_ = pl.Config.set_tbl_hide_dataframe_shape(True)
from wetterdienst import Wetterdienst, Settings
from pvlib import irradiance
from pvlib.solarposition import get_solarposition
import numpy as np
import logging

# Set up logging
logger = logging.getLogger(__name__)

class Environment(object):
    """Environment class for providing external data to the virtual power plant simulation.
    
    This class handles time-related settings, weather data retrieval and processing,
    and provides this data to the components of the virtual power plant for simulation.
    
    Attributes
    ----------
    timebase : str or None
        The time base for the simulation.
    timezone : str
        The timezone for the simulation (default: 'Europe/Berlin').
    start : datetime.datetime
        Start time of the simulation.
    end : datetime.datetime
        End time of the simulation.
    year : int or None
        The year for the simulation.
    time_freq : str
        Time frequency for the simulation (default: '15 min').
    mean_temp_days : list
        List of mean temperatures by day.
    mean_temp_hours : list
        List of mean temperatures by hour.
    mean_temp_quarter_hours : list
        List of mean temperatures by quarter hour.
    pv_data : pandas.DataFrame
        Photovoltaic-related weather data.
    wind_data : pandas.DataFrame
        Wind-related weather data.
    temp_data : pandas.DataFrame
        Temperature data.
    surpress_output_globally : bool
        Whether to suppress output globally.
    force_end_time : bool
        Whether to force the end time.
    use_timezone_aware_time_index : bool
        Whether to use timezone-aware time index.
    """
    
    def __init__(
        self,
        timebase=None,
        timezone="Europe/Berlin",
        start=None,
        end=None,
        year=None, 
        time_freq="15 min",
        mean_temp_days=[],
        mean_temp_hours=[],
        mean_temp_quarter_hours = [],
        pv_data=[],
        wind_data=[],
        temp_data=[],
        surpress_output_globally = True,
        force_end_time = False,
        use_timezone_aware_time_index = False,
    ):
        """Initialize an Environment object.
        
        Parameters
        ----------
        timebase : str or None, optional
            The time base for the simulation.
        timezone : str, optional
            The timezone for the simulation (default: 'Europe/Berlin').
        start : datetime.datetime or str, optional
            Start time of the simulation.
        end : datetime.datetime or str, optional
            End time of the simulation.
        year : int, optional
            The year for the simulation.
        time_freq : str, optional
            Time frequency for the simulation (default: '15 min').
        mean_temp_days : list, optional
            List of mean temperatures by day.
        mean_temp_hours : list, optional
            List of mean temperatures by hour.
        mean_temp_quarter_hours : list, optional
            List of mean temperatures by quarter hour.
        pv_data : pandas.DataFrame or list, optional
            Photovoltaic-related weather data.
        wind_data : pandas.DataFrame or list, optional
            Wind-related weather data.
        temp_data : pandas.DataFrame or list, optional
            Temperature data.
        surpress_output_globally : bool, optional
            Whether to suppress output globally (default: True).
        force_end_time : bool, optional
            Whether to force the end time (default: False).
        use_timezone_aware_time_index : bool, optional
            Whether to use timezone-aware time index (default: False).
        """
        self.timebase = timebase
        self.timezone = zoneinfo.ZoneInfo(timezone)
        self.start = start
        self.end = end
        self.year = year
        self.time_freq = time_freq
        self.mean_temp_days = mean_temp_days
        self.mean_temp_hours = mean_temp_hours
        self.mean_temp_quarter_hours = mean_temp_quarter_hours
        self.pv_data = pv_data
        self.wind_data = wind_data
        self.temp_data = temp_data
        self.__surpress_output_globally = surpress_output_globally
        self.__force_end_time = force_end_time
        self.__use_timezone_aware_time_index = use_timezone_aware_time_index
        if not start is None and not end is None:
            
            if type(self.start) == str:
                self.__internal_start_datetime_with_class_timezone    =   datetime.datetime.strptime(
                    self.start, '%Y-%m-%d %H:%M:%S'
                    ).replace(tzinfo = self.timezone)
            else:
                self.__internal_start_datetime_with_class_timezone    =   self.start.astimezone(self.timezone)

            if type(self.end) == str:
                self.__internal_end_datetime_with_class_timezone      =   datetime.datetime.strptime(
                    self.end  , '%Y-%m-%d %H:%M:%S'
                    ).replace(tzinfo = self.timezone)
            else:
                self.__internal_end_datetime_with_class_timezone      =   self.end.astimezone(self.timezone)

            self.__internal_start_datetime_utc = (
                self.__internal_start_datetime_with_class_timezone - self.__internal_start_datetime_with_class_timezone.utcoffset()
                ).replace(tzinfo = zoneinfo.ZoneInfo(key='UTC'), microsecond = 0)
            self.__internal_end_datetime_utc   = (
                self.__internal_end_datetime_with_class_timezone - self.__internal_end_datetime_with_class_timezone.utcoffset()
                ).replace(tzinfo = zoneinfo.ZoneInfo(key='UTC'), microsecond = 0)
            self.__temp_station_metadata = 0 
            
            if self.__internal_start_datetime_utc > self.__internal_end_datetime_utc:
                raise ValueError("End date must be greater than start date")
            if self.__internal_start_datetime_utc + datetime.timedelta(hours=1) > self.__internal_end_datetime_utc:
                raise ValueError("End date must be at least one hour later than the start date")

    @property
    def __start_dt_utc(self):
        return self.__internal_start_datetime_utc

    @__start_dt_utc.setter
    def __start_dt_utc(self, new___start_dt_utc):
        if new___start_dt_utc.tzinfo != zoneinfo.ZoneInfo(key='UTC'):
            raise ValueError('@__start_dt_utc.setter: new time not given in utc')
        new___start_dt_utc = new___start_dt_utc.replace(microsecond = 0)
        self.__internal_start_datetime_utc = new___start_dt_utc
        time_wo_offset = new___start_dt_utc.replace(tzinfo = self.timezone)
        self.__internal_start_datetime_with_class_timezone = time_wo_offset + time_wo_offset.utcoffset()
        self.start = str(self.__internal_start_datetime_with_class_timezone.replace(tzinfo = None))
        print("Setted new start time to: ", self.__internal_end_datetime_with_class_timezone) and not self.__surpress_output_globally
    
    @property
    def __end_dt_utc(self):
        return self.__internal_end_datetime_utc

    @__end_dt_utc.setter
    def __end_dt_utc(self, new___end_dt_utc):
        if new___end_dt_utc.tzinfo != zoneinfo.ZoneInfo(key='UTC'):
            raise ValueError('@__end_dt_utc.setter: new time not given in utc')
        new___end_dt_utc = new___end_dt_utc.replace(microsecond=0)
        self.__internal_end_datetime_utc = new___end_dt_utc
        time_wo_offset = new___end_dt_utc.replace(tzinfo = self.timezone)
        self.__internal_end_datetime_with_class_timezone = time_wo_offset + time_wo_offset.utcoffset()
        self.end = str(self.__internal_end_datetime_with_class_timezone.replace(tzinfo = None))
        print("Setted new end time to: ", self.__internal_end_datetime_with_class_timezone)  and not self.__surpress_output_globally
        
    @property
    def __start_dt_target_tz(self):
        return self.__internal_start_datetime_with_class_timezone

    @__start_dt_target_tz.setter
    def __start_dt_target_tz(self, new_start_dt):
        if new_start_dt.tzinfo != self.timezone:
            raise ValueError('@__start_dt_target_tz.setter: new time not given in target timezone')
        new_start_dt = new_start_dt.replace(microsecond = 0)
        self.__internal_start_datetime_with_class_timezone = new_start_dt  
        self.__internal_start_datetime_utc = (new_start_dt - new_start_dt.utcoffset()).replace(tzinf = zoneinfo.ZoneInfo(key='UTC'))
        self.start = str(self.__internal_start_datetime_with_class_timezone.replace(tzinfo = None))
        print("Setted new start time to: ", self.__internal_start_datetime_with_class_timezone)  and not self.__surpress_output_globally
        
    @property
    def __end_dt_target_tz(self):
        return self.__internal_end_datetime_with_class_timezone

    @__end_dt_target_tz.setter
    def __end_dt_target_tz(self, new_end_dt):
        if new_end_dt.tzinfo != self.timezone:
            raise ValueError('@__end_dt_target_tz.setter: new time not given in target timezone')
        new_end_dt = new_end_dt.replace(microsecond=0)
        self.__internal_end_datetime_with_class_timezone = new_end_dt
        self.__internal_end_datetime_utc = (new_end_dt - new_end_dt.utcoffset()).replace(tzinfo = zoneinfo.ZoneInfo(key='UTC'))
        self.end = str(self.__internal_end_datetime_with_class_timezone.replace(tzinfo = None))
        print("Setted new end time to: ", self.__internal_end_datetime_with_class_timezone)  and not self.__surpress_output_globally



    def get_pv_data(self, file):

        self.pv_data = pd.read_csv(file, index_col="time")
        self.pv_data.index = pd.to_datetime(self.pv_data.index)

        return self.pv_data

    def get_mean_temp_days(self, file):

        self.mean_temp_days = pd.read_csv(file, index_col="time")

        return self.mean_temp_days

    def get_mean_temp_hours(self, file):

        self.mean_temp_hours = pd.read_csv(file, index_col="time")

        return self.mean_temp_hours

    def get_wind_data(self, file, utc=False):

        r"""
        Imports weather data from a file.
    
        The data include wind speed at two different heights in m/s, air
        temperature in two different heights in K, surface roughness length in m
        and air pressure in Pa. The file is located in the example folder of the
        windpowerlib. The height in m for which the data applies is specified in
        the second row.
    
        Parameters
        ----------
        file : string
            Filename of the weather data file. Default: 'dwd_wind_data_2015.csv'.
            
        utc : boolean
            Decide, weather to use utc conversion or not
    
        Returns
        -------
        weather_df : pandas.DataFrame
                DataFrame with time series for wind speed `wind_speed` in m/s,
                temperature `temperature` in K, roughness length `roughness_length`
                in m, and pressure `pressure` in Pa.
                The columns of the DataFrame are a MultiIndex where the first level
                contains the variable name as string (e.g. 'wind_speed') and the
                second level contains the height as integer at which it applies
                (e.g. 10, if it was measured at a height of 10 m).
    
        """
        try:
            # Try to read the file with MultiIndex columns
            if utc == True:
                df = pd.read_csv(
                    file,
                    index_col=0,
                    header=[0, 1],
                    date_parser=lambda idx: pd.to_datetime(idx, utc=True),
                )
                # change type of index to datetime and set time zone
                df.index = pd.to_datetime(df.index).tz_convert(self.timezone)
            else:
                df = pd.read_csv(file, index_col=0, header=[0, 1])
                df.index = pd.to_datetime(df.index)

            # change type of height from str to int by resetting columns
            l0 = [_[0] for _ in df.columns]
            l1 = [int(_[1]) for _ in df.columns]
            df.columns = pd.MultiIndex.from_tuples(list(zip(l0, l1)), names=['variable', 'height'])
        except Exception as e:
            # If the file doesn't have MultiIndex columns, try to read it as a regular CSV
            # and create the MultiIndex manually
            try:
                # Skip the first 2 rows which contain headers
                df = pd.read_csv(file, skiprows=2)
                
                # Set the index to the Time column and convert to datetime
                df.set_index('Time', inplace=True)
                df.index = pd.to_datetime(df.index)
                
                # Rename the columns to match the expected names
                df.columns = ['wind_speed', 'pressure', 'temperature', 'roughness_length']
                
                # Create a new DataFrame with MultiIndex columns
                columns = pd.MultiIndex.from_tuples([
                    ('wind_speed', 10),
                    ('pressure', 0),
                    ('temperature', 2),
                    ('roughness_length', 0)
                ], names=['variable', 'height'])
                
                # Create the new DataFrame with the MultiIndex columns
                df = pd.DataFrame(
                    df.values,
                    index=df.index,
                    columns=columns
                )
                
                if utc == True:
                    # Convert to timezone-aware datetime
                    df.index = pd.to_datetime(df.index, utc=True).tz_convert(self.timezone)
            except Exception as inner_e:
                raise ValueError(f"Failed to read wind data file: {e}. Inner error: {inner_e}")
                
        self.wind_data = df
        return self.wind_data

    def get_time_from_dwd(self):
        """Get current time in UTC timezone.
        
        Returns
        -------
        datetime.datetime
            Current time in UTC timezone with seconds and microseconds set to 0.
        """
        # Use the current time in UTC timezone
        return datetime.datetime.now(tz=datetime.timezone.utc).replace(second=0, microsecond=0)
        
    def __get_solar_parameter (self, date, ghi, lat, lon, height, temperature = None, pressure = None, dew_point = None, methode = 'disc', use_methode_name_in_columns = False, extended_solar_data = False,):
        """
            Calculates solar parameters based on the given method by using pvlib estimation modells.

            Parameters
            ----------
            date : pandas.DatetimeIndex
                date assumet in UTC if no tz given
            ghi : list or series
                Global Irradiance       [W/m2]
            lat : float
                Latitude of the location.
            lon : float
                Longitude of the location.
            height : float
                Altitude or height of the location. [m]
            temperature : list or series, optional
                temperature at height   [C]
            drew_pint : list or series, optional
                 drew point             [C]
            pressure : list or series, optional
                pressure at height      [Pa]
            method : str, optional
                Method for solar parameter calculation (default is 'disc').
                Options: 'disc', 'erbs', 'dirint', 'boland'.
            use_method_name_in_columns : bool, optional
                If True, method name is included in the column names of the output DataFrame (default is False).
            extended_solar_data : bool
                If True, additional solar parameters are included in the output DataFrame (default is False).

            Returns
            -------
            out_df : pandas.DataFrame
                DataFrame with calculated solar parameters.
                Columns include 'dni', 'dhi'. Includes 'bh', 'zenith', 'apparent_zenith' when extended_solar_data is True.
                The DataFrame has the same index as the input_df.

            Notes
            -----
            - Solar zenith angles and other solar position parameters are calculated using the get_solarposition function.
            - The method parameter determines the algorithm used for solar parameter calculation.
            - Examples:
                https://pvlib-python.readthedocs.io/en/stable/gallery/irradiance-decomposition/plot_diffuse_fraction.html#sphx-glr-gallery-irradiance-decomposition-plot-diffuse-fraction-py
        """
        
        """
        https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.solarposition.get_solarposition.html#pvlib.solarposition.get_solarposition
        """
        
        #Calculate solar position parameters
        #Shift by -30 min to get the solar position for the middle of the time intervall
        #The index has to be converted to a list, to aviod index alignment of the series pressure and temperature with the shifted date index
        solpos = get_solarposition(
                    list(date.shift(freq = '-30min')), 
                    latitude    = lat,
                    longitude   = lon, 
                    altitude    = height,
                    pressure    = pressure,
                    temperature = temperature if temperature is not None else 12
                    )
        #Shift back after calculation
        solpos.index = date
            
        if methode == 'disc':
            out_disc = irradiance.disc(
                        ghi             = ghi, 
                        solar_zenith    = solpos.zenith, 
                        datetime_or_doy = date, 
                        pressure        = pressure,
                        )
        
            df_disc = irradiance.complete_irradiance(
                        solar_zenith = solpos.apparent_zenith, 
                        ghi          = ghi, 
                        dni          = out_disc.dni,
                        dhi          = None
                        )
            out_disc['dhi'] = df_disc.dhi
            out_df = out_disc.drop(['kt', 'airmass'],axis = 1)
            
            
        elif methode == 'erbs':
            out_erbs = irradiance.erbs(
                        ghi             = ghi,
                        zenith          = solpos.zenith, 
                        datetime_or_doy = date
                        )
            out_df = out_erbs.drop(['kt'],axis = 1)
            
        elif methode == 'dirint':
            dni_dirint = irradiance.dirint(
                            ghi          = ghi, 
                            solar_zenith = solpos.zenith, 
                            times        = date, 
                            pressure     = pressure,
                            temp_dew     = dew_point
                            )
        
            df_dirint = irradiance.complete_irradiance(
                            solar_zenith = solpos.apparent_zenith,
                            ghi          = ghi, 
                            dni          = dni_dirint,
                            dhi          = None
                            )
            out_dirint = pd.DataFrame(
                            {'dni': dni_dirint, 'dhi': df_dirint.dhi}, index = date
                            )
            out_df = out_dirint.fillna(0)
            
        elif methode == 'boland':
            out_boland = irradiance.boland(
                            ghi             = ghi,
                            solar_zenith    = solpos.zenith,
                            datetime_or_doy = date, 
                            a_coeff         = 8.645, 
                            b_coeff         = 0.613, 
                            min_cos_zenith  = 0.065, 
                            max_zenith      = 87
                            )
            out_df = out_boland.drop(['kt'], axis = 1)

        if extended_solar_data:
            out_df['bh'] = ghi - out_df['dhi']
            out_df['zenith'] = solpos.zenith
            if temperature is not None:
                out_df['apparent_zenith'] = solpos.apparent_zenith
        
        
        #Add methode to column name of the parameters
        if use_methode_name_in_columns: out_df.columns = [str(col) + '_' + methode for col in out_df.columns]
        
        #Delete values in out_df, when ghi is NaN.
        out_df.where(cond=(np.isnan(ghi) != True), other=None, inplace=True)

        return out_df

    def __get_solar_power_from_energy(self, df, query_type):
        """
            Calculates solar power from solar energy data.

            Parameters
            ----------
            df : pandas.DataFrame
                DataFrame containing solar energy data.
            query_type : str
                Type of data query ('MOSMIX' or 'OBSERVATION').

            Returns
            -------
            df_power : pandas.DataFrame
                DataFrame with calculated solar power data.
                Columns include 'ghi' when using mosmix; 'ghi' and 'bh' when using observation query type.
                The DataFrame has the same index as the input df.

            Notes
            -----
            - The input DataFrame (df) has to contain 'ghi' in columns. Additionaly there can be 'dhi' in columns.
            - The Units for all irradiance parameter are:
            [kJ/m^2/resolution] for MOSMIX
            [J/cm^2/resolution] for OBSERVATION
            - The query_type parameter specifies the type of data query, either 'MOSMIX' or 'OBSERVATION'.
            - The calculated solar power is returned in units of [W/m^2].
        """
        
        df_power = pd.DataFrame(index=df.index)
        df_power['ghi'] = 0
        if 'dhi' in df.columns:
            df_power['dhi'] = 0
        
        resolution = (df.index[1]-df.index[0]).seconds
        if query_type == 'MOSMIX':
            for column in df_power.columns:
                df_power[column] = df[column] * 1000 / resolution #kJ/m2 -> J/m2 -> W/m2
        elif query_type == 'OBSERVATION':
            for column in df_power.columns:
                df_power[column] = df[column] * 10e3 / resolution #/J/cm2 -> J/m2 -> W/m2

        return df_power
    
    def __get_station_pressure_from_reduced_pressure(self, height, pressure_reduced, temperature):
        """
        Calculates station pressure from reduced pressure using the barometric height formula.

        Parameters
        ----------
        height : float
            Height [m] of the station above sea level.
        pressure_reduced : float or pandas.Series
            Reduced pressure [Pa] at the station.
        temperature : float or pandas.Series
            Temperature [K] at the station.

        Returns
        -------
        float
            Calculated station pressure [Pa].

        Notes
        -----
        - The calculation is based on the barometric height formula.
        - The provided height should be in meters.
        - The temperature is expected to be in degrees Celsius.
        - The calculated station pressure is returned as a float.
        - The formula used is from the Wikipedia link provided.
        - https://de.wikipedia.org/wiki/Barometrische_Höhenformel
        """
        pressure_station = (
            pressure_reduced * ( 1 - ( 0.0065  * height) / temperature) ** ((9.81 * 0.02897) / (8.314 * 0.0065))
            )
        return pressure_station
     
    def __resample_data(self, df, time_freq = None):
        """
            Resamples and interpolates weather data.

            Parameters
            ----------
            df : pandas.DataFrame
                DataFrame containing weather data.
            time_freq : str, optional
                Time frequency for resampling, e.g., '60min' for hourly. If not provided,
                the time frequency from the class instance is used.

            Returns
            -------
            resampled_df : pandas.DataFrame
                DataFrame with resampled and interpolated weather data.
                The DataFrame has the same columns as the input df.

            Notes
            -----
            - If time_freq is not provided, the time frequency from the class instance is used.
            - The input DataFrame (df) is expected to have a datetime index.
            - Missing data between vaild data is filled by using linear interpolation.
            - The resampling is done using the specified time frequency when given. Otherwhise Class-time-freq is used
            - Missing data at the end of the dataframe is not replaced -> NaN
            - The resulting DataFrame is truncated to match the target end datetime if necessary.
            - The columns are sorted alphabetically and rounded to two decimal places.
            - The resulting DataFrame contains timestamps with timezoneinfo in class timezone when __use_timezone_aware_time_index == True
                Otherwise timezoneinfo is not given but times are in class timezone
        """
        if time_freq is None:
            time_freq =  self.time_freq
        
        #Convert UTC timestamps to class timezone
        if df.index[0].tzinfo != None:
            timezone_aware_date_list = list()
            for time in df.index:
                timezone_aware_date_list.append(
                    time.tz_convert(self.timezone)
                    )     
            df['time_tz'] = timezone_aware_date_list
            df.set_index('time_tz',inplace = True)
            df.index.rename("time", inplace = True)
        
            
        #Missing dwd data is marked with -999. Replace by NaN
        df.where(cond=(df[df.columns] != -999), other=None, inplace=True)
        
        #Fill NaN - if force_end_time == True keep the missing values at the end
        df.interpolate(
            inplace=True, 
            limit_area = 'inside' if self.__force_end_time else None)
        
        #Resample to given resulotion and interpolate over missing values
        #if force_end_time == True keep the missing values at the end
        df = df.resample(time_freq).mean().interpolate(
            method = 'linear', 
            limit_area = 'inside' if self.__force_end_time else None)
        
        #Remove timestamps which are not needed
        #For timezone aware timestamps:
        if df.index[0].tzinfo != None:
            if df.index[-1] > self.__end_dt_target_tz:
                df = df[df.index[0]:self.__end_dt_target_tz]
        #For timezone unaware timestamps:
        else:
            if df.index[-1] > self.__end_dt_target_tz.replace(tzinfo=None):
                df = df[df.index[0]:self.__end_dt_target_tz.replace(tzinfo=None)]
                
        #Remove timezone info    
        if not self.__use_timezone_aware_time_index and df.index[0].tzinfo != None:
            timezone_unaware_date_list = list()
            for time in df.index:
                timezone_unaware_date_list.append(
                    time.replace(tzinfo = None)
                    )
            df['time_wo_tz'] = timezone_unaware_date_list
            df.set_index('time_wo_tz',inplace = True)
            df.index.rename("time", inplace = True)
            
        df = df.reindex(sorted(df.columns), axis=1)
        df = round(df,2)
        return df
    
    
    def __get_multi_index_for_windpowerlib (self, columns):
        """
       Creates a MultiIndex DataFrame for wind-related parameters.
    
       Parameters
       ----------
       columns : list
           List of column names for the DataFrame.
    
       Returns
       -------
       multi_index : pandas.MultiIndex
           MultiIndex containing parameter names and corresponding heights.
    
       Notes
       -----
       - The function initializes a DataFrame with the provided column names.
       - It then creates a dictionary, `rename_dict`, mapping each parameter to a specific height.
       - For each column in the DataFrame, the function assigns a tuple with the parameter name
         and the corresponding height from `rename_dict`.
       - The final MultiIndex is set for the DataFrame with levels 'Parameter' and 'Height'.
       """
        rename_dict = {
            'wind_speed'       : 10,
            'pressure'         : 0,
            'temperature'      : 2,
            'roughness_length' : 0,
            }
        df = pd.DataFrame(columns = columns)
        for act_column in df.columns:
            for key in rename_dict.keys():
                if key == act_column:
                    df[act_column] = (act_column, rename_dict[key])
                    break       
        df.columns = pd.MultiIndex.from_arrays([df.iloc[0], df.iloc[1]], names=['Parameter', 'Height'])
        return df.columns
    
    
    def __process_observation_parameter (self, pd_sorted_data_for_station, dataset, pd_station_metadata = None, extended_solar_data = False):
        """
            Processes observation parameters based on the dataset.

            Parameters
            ----------
            pd_sorted_data_for_station : pandas.DataFrame
                DataFrame containing weather data for a station in 10min resolution.
                Input units:
                solar: ghi, dhi [J/cm^2]
                air:   temperature [C]
                wind:  wind_speed [m/s], pressure [hPa], temperature [C]
            pd_station_metadata : pandas.DataFrame, optional for wind and temperature dataset, necessary for solar dataset
                DataFrame containing station metadata.
                lat, lon
                height [m]
            dataset : str
                Type of weather dataset, either 'solar', 'air' or 'wind'.
            extended_solar_data : bool, optional
                If True, additional solar parameters are included in the output DataFrame (default is False).

            Returns
            -------
            resampled_data : pandas.DataFrame
                Resampled and processed weather data in class time resolution.
                Output units:
                solar: ghi, dhi, dni [W/m^2]. Includes bh [W/m^2] and zenith when extended_solar_data is True.
                air:   temperature [°C]
                wind:  wind_speed [m/s], pressure [Pa], temperature [K]


            Notes
            -----
            - If the dataset is 'solar', the function updates the DataFrame with solar power calculated from energy.
            It then calculates solar zenith angle from time, lat, lon, and height to calculate direct normal irradiance (DNI) afterwards.
            - If the dataset is 'wind', the function prepares data for Windpowerlib using the
            __get_multi_index_for_windpowerlib method and resamples the data.
            - Because the air parameter does not need to be processed, the function does not change them.
        """
        if dataset == 'solar': 
            
            #Calculate power from irradiance
            pd_sorted_data_for_station.update(self.__get_solar_power_from_energy(pd_sorted_data_for_station,'OBSERVATION'), overwrite=True)
            pd_sorted_data_for_station['bh'] = pd_sorted_data_for_station.ghi - pd_sorted_data_for_station.dhi
            
            #Calculate solar zenith angle from time, lat, lon, and height
            #Temperature (positinonal argument) is not needed for zenit. Nessessary for apperent_zenith --> set to 0
            #Zenith angle is calculatet for the middle of the time intervall
            #Shift back after calculation to align with observation data
            pd_sorted_data_for_station['zenith'] = get_solarposition(
                        list(pd_sorted_data_for_station.index.shift(freq = '-5min')), 
                        latitude    = pd_station_metadata['latitude' ].values[0],
                        longitude   = pd_station_metadata['longitude'].values[0], 
                        altitude    = pd_station_metadata['height'   ].values[0],
                        temperature = 0
                        ).zenith.shift(freq = '5min')
            
            #Calculate Direct Normal Irradiance (DNI) from GHI and DHI
            pd_sorted_data_for_station['dni'] = irradiance.dni(
                ghi = pd_sorted_data_for_station.ghi,
                dhi = pd_sorted_data_for_station.dhi,
                zenith = pd_sorted_data_for_station.zenith
                )
            #Remove sign error for -0.0 values
            pd_sorted_data_for_station['dni'] = pd_sorted_data_for_station['dni'].replace(-0.0, 0.0)
            
            if extended_solar_data:
                pd_sorted_data_for_station.drop(['zenith', 'bh'], axis = 1, inplace = True)
        
        elif dataset == 'wind':
            pd_sorted_data_for_station.pressure    = pd_sorted_data_for_station.pressure * 100       # hPa to Pa
            pd_sorted_data_for_station.temperature = pd_sorted_data_for_station.temperature + 273.15 #°C to K
            pd_sorted_data_for_station['roughness_length'] = 0.15
            pd_sorted_data_for_station.columns = self.__get_multi_index_for_windpowerlib(
                pd_sorted_data_for_station.columns)
            
        return self.__resample_data(pd_sorted_data_for_station)
        
        
    def __process_mosmix_parameter (
            self, pd_sorted_data_for_station, dataset, estimation_methode_lst = ['disc'], pd_station_metadata = None, extended_solar_data = False
            ):
        """
            Processes MOSMIX parameters based on the dataset.

            Parameters
            ----------
            pd_sorted_data_for_station : pandas.DataFrame
                DataFrame containing weather data for a station in hourly resolution.
                Input units:
                solar: ghi [kJ/m^2], temperature [K], dew_point [K], pressure at sea level [hPa]
                air:   temperature [K]
                wind:  wind_speed [m/s], pressure at sea level [hPa], temperature [K]
            dataset : str
                Type of weather dataset, either 'solar', 'air', or 'wind'.
            pd_station_metadata : pandas.DataFrame, optional for temperature dataset, necessary for solar and wind dataset
                DataFrame containing station metadata.
                lat, lon
                height [m]
            estimation_methode_lst : list, optional
                List of estimation methode names, which where used for calculating missing parameters such as dhi dni, by default ['disc'].
            extended_solar_data : bool, optional
                If True, additional solar parameters are included in the output DataFrame (default is False).
            Returns
            -------
            resampled_data : pandas.DataFrame
                Resampled and processed weather data in class time resolution.
                Output units:
                solar: ghi, dhi, dni [W/m^2]. Includes bh [W/m^2], zenith, apparent_zenith when extended_solar_data is True.
                air:   temperature [°C]
                wind:  wind_speed [m/s], pressure [Pa], temperature at station height [K]

            Notes
            -----
            - If the dataset is 'solar', the function updates the DataFrame with solar power
            calculated from energy. It then calculates solar parameters using the
            __get_solar_parameter method and merges them into the DataFrame.
            - If the dataset is 'air', the function converts temperature from Kelvin to Celsius.
            - If the dataset is 'wind', the function adjusts pressure using the barometric
            height formula and prepares data for Windpowerlib.
            - The observation data describes the value for the last timestep. MOSMIX forecasts
            the value for the next timestep, so the DataFrame is shifted by -1 to align MOSMIX
            with observation.
        """
        if dataset == 'solar':
            pd_sorted_data_for_station.update( self.__get_solar_power_from_energy(pd_sorted_data_for_station, 'MOSMIX'), overwrite=True)
            if 'pressure' in pd_sorted_data_for_station.columns:
                pd_sorted_data_for_station.pressure = self.__get_station_pressure_from_reduced_pressure(
                    height = pd_station_metadata['height'].values[0], 
                    pressure_reduced = pd_sorted_data_for_station.pressure, 
                    temperature = pd_sorted_data_for_station.temperature)
            """
            Available methods for solar parameter calculation:
             ['disc','erbs','dirint','boland']
            """
            for methode in estimation_methode_lst:
                calculated_solar_parameter = self.__get_solar_parameter(
                        date        = pd_sorted_data_for_station.index, 
                        ghi         = pd_sorted_data_for_station.ghi, 
                        temperature = pd_sorted_data_for_station.temperature - 273.15 if 'temperature' in pd_sorted_data_for_station.columns else None, 
                        pressure    = pd_sorted_data_for_station.pressure             if 'pressure'    in pd_sorted_data_for_station.columns else None, 
                        dew_point  = pd_sorted_data_for_station.dew_point - 273.15    if 'dew_point'   in pd_sorted_data_for_station.columns else None,
                        lat         = pd_station_metadata['latitude' ].values[0], 
                        lon         = pd_station_metadata['longitude'].values[0],
                        height      = pd_station_metadata['height'   ].values[0],
                        methode     = methode,
                        use_methode_name_in_columns = (len(estimation_methode_lst) > 1),
                        extended_solar_data = extended_solar_data)
                pd_sorted_data_for_station = pd_sorted_data_for_station.merge(right = calculated_solar_parameter, left_index = True, right_index = True)
            if not extended_solar_data:
                for additional_parameter in ['temperature','dew_point','pressure']:
                    if additional_parameter in pd_sorted_data_for_station.columns:
                        pd_sorted_data_for_station.drop(additional_parameter, axis = 1, inplace = True)
        elif dataset == 'air':
            pd_sorted_data_for_station.temperature = pd_sorted_data_for_station.temperature - 273.15  # K to °C
        elif dataset == 'wind':
            pd_sorted_data_for_station.pressure = self.__get_station_pressure_from_reduced_pressure(
                height = pd_station_metadata['height'].values[0], 
                pressure_reduced = pd_sorted_data_for_station.pressure, 
                temperature = pd_sorted_data_for_station.temperature)
            
            pd_sorted_data_for_station['roughness_length'] = 0.15
            pd_sorted_data_for_station.columns = self.__get_multi_index_for_windpowerlib(
                pd_sorted_data_for_station.columns)
            
        #Observation data discribes the value for the last timestep. MOSMIX forecasts the value for the next timestep
        #Shift by -1 to aling MOSMIX to Observation
        pd_sorted_data_for_station = pd_sorted_data_for_station.shift(-1)
        pd_sorted_data_for_station.drop(pd_sorted_data_for_station.tail(1).index, inplace = True) 
        
        return self.__resample_data(pd_sorted_data_for_station)
    
    
    def __get_dwd_data(
        self, dataset, lat = None, lon = None, user_station_id = None, distance = 30, min_quality_per_parameter = 80, use_mosmix = False
        ):
        """
            Retrieves weather data from the DWD database.

            Parameters
            ----------
            dataset : str
                Type of weather dataset, either 'solar', 'air', or 'wind'.
            lat : float, optional
                Latitude, by default None.
            lon : float, optional
                Longitude, by default None.
            user_station_id : str, optional
                Station ID specified by the user, by default None.
            distance : int, optional
                Search radius [m] for stations, by default 30.
            min_quality_per_parameter : int, optional
                Minimum percentage of valid data required for each parameter, by default 80.
        
            Returns
            -------
            pd_sorted_data_for_station : pandas.DataFrame
                raw dwd data for the selected station
            station_metadata : pandas.DataFrame
                Metadata of the selected weather station.

            Raises
            ------
            ValueError
                If no location or station ID is given.
            ValueError
                If the forecast start time is too far in the future
            ValueError
                If no station is found within the specified distance.
            Exception
                If datatype of query result is not pandas or polars
            Exception
                If there is no station with valid datasets

            Notes
            -----
            - The function checks whether to use the DWD observation or MOSMIX database based on the current time.
            - It retrieves weather data for the specified dataset from the DWD database.
            - The function filters stations based on the user-specified station ID or location.
            - It checks the validity of the query result for each station based on the percentage of valid data for each parameter.
            - If a station with valid data is found, the function preturns the raw dwd data
         """
        activate_output = not self.__surpress_output_globally

        if  self.start is None or self.end is None:
            raise ValueError("Class instance does not contain start or end time!")
        if (lat is None or lon is None) and user_station_id is None:
            raise ValueError("No location or station-ID given!")
        
        dataset_dict = {
            'solar'       : ['ghi', 'dhi' ],
            'air'         : ['temperature'],
            'wind'        : ['wind_speed', 'pressure', 'temperature'],
            'solar_est'   : ['pressure', 'temperature', 'dew_point'],
            'wind_speed'  : ['wind_speed'],
            'pressure'    : ['pressure'],
            'temperature' : ['temperature']
            }

        # Parameter mapping for the new API
        # In the new API, parameters are specified differently for observation and mosmix
        available_parameter_dict = {
            "ghi"         : "radiation_global", 
            "dhi"         : "radiation_sky", 
            "pressure"    : "air_pressure", 
            "temperature" : "temperature_air", 
            "wind_speed"  : "wind_speed", 
            "dew_point"   : "temperature_dew_point",
            }
        
        # Create a dictionary with the parameters to query
        req_parameter_dict = {param: available_parameter_dict[param] for param in dataset_dict[dataset]}
        
        time_now = self.get_time_from_dwd()
        # Create settings with the appropriate parameters for the API
        settings = Settings(
            ts_shape="wide",
            ts_humanize=True
        )
        
        #observation database is updated every full hour
        observation_end_date = time_now.replace(minute = 0 , second = 0, microsecond = 0)

        # Check if we should use MOSMIX based on the use_mosmix parameter or time
        if not use_mosmix and (self.__start_dt_utc < observation_end_date - datetime.timedelta(hours = 1) or (
            self.__start_dt_utc == observation_end_date - datetime.timedelta(hours = 1) and self.__end_dt_utc <= observation_end_date)):
            if activate_output:
                print("Using observation database.") 
            if self.__end_dt_utc > observation_end_date and not self.__force_end_time:
                if activate_output:
                    print("End date is in the future.")
                self.__end_dt_utc = observation_end_date

            # Get weather data for your location from DWD observation database
            # Initialize the API with the provider and network using the new API structure
            api = Wetterdienst.resolve('dwd', 'observation')
            
            # Create separate requests for each parameter type with the appropriate resolution
            wd_query_results = []
            
            # Map parameters to the appropriate resolution and parameter group
            # In the new API, parameters are specified as tuples (resolution, parameter_group)
            parameter_mapping = {
                "radiation_global": ("10_minutes", "solar"),
                "radiation_sky": ("10_minutes", "solar"),
                "wind_speed": ("hourly", "wind"),
                "air_pressure": ("hourly", "pressure"),
                "temperature_air": ("hourly", "temperature_air"),
                "temperature_dew_point": ("hourly", "dew_point")
            }
            
            # Group parameters by resolution and parameter group
            parameter_groups = {}
            for param_key, param_value in req_parameter_dict.items():
                if param_value in parameter_mapping:
                    resolution, group = parameter_mapping[param_value]
                    if (resolution, group) not in parameter_groups:
                        parameter_groups[(resolution, group)] = []
                    parameter_groups[(resolution, group)].append(param_key)
            
            # Create requests for each resolution and parameter group
            try:
                for (resolution, group), params in parameter_groups.items():
                    logger.info(f"Creating request for resolution={resolution}, group={group}, params={params}")
                    
                    # Create the parameter tuple for the API
                    # Format: [(resolution, group)]
                    parameter_tuple = [(resolution, group)]
                    
                    # Create the request
                    request = api(
                        parameters=parameter_tuple,
                        start_date=self.__start_dt_utc,
                        end_date=self.__end_dt_utc,
                        settings=settings
                    )
                    wd_query_results.append(request)
                
                # If we have any results, use the first one for station filtering
                if wd_query_results:
                    wd_query_result = wd_query_results[0]
                else:
                    raise ValueError("No parameters to query")
                    
            except Exception as e:
                print(f"Error creating observation request: {e}")
                raise
        else:
            if self.__start_dt_utc > time_now + datetime.timedelta(hours = 239):
                raise ValueError("No forecast data avaliable for this time")
            if (self.__end_dt_utc > time_now.replace(
                minute = 0 , 
                second = 0, 
                microsecond = 0
                ) + datetime.timedelta(hours = 240)) and not self.__force_end_time:
                self.__end_dt_utc = time_now.replace(
                    minute = 0, 
                    second = 0, 
                    microsecond = 0
                    ) + datetime.timedelta(hours = 240)
            if activate_output:  
                print("Using mosmix database.")
                
            if dataset == 'solar':
                #dhi is not available for MOSMIX
                if "dhi" in req_parameter_dict:
                    req_parameter_dict.pop("dhi")
                
            # Initialize the API with the provider and network using the new API structure
            api = Wetterdienst.resolve('dwd', 'mosmix')
            
            # In the new API, MOSMIX parameters are specified as tuples (hourly, small/large, parameter_name)
            # Map our parameters to MOSMIX parameters
            mosmix_parameter_mapping = {
                "radiation_global": "radiation_global",
                "air_pressure": "pressure_air_site_reduced",
                "temperature_air": "temperature_air_mean_2m",
                "wind_speed": "wind_speed",
                "temperature_dew_point": "temperature_dew_point_mean_2m"
            }
            
            # Create the parameter tuples for the API
            parameter_tuples = []
            for param_value in req_parameter_dict.values():
                if param_value in mosmix_parameter_mapping:
                    # Format: (hourly, small, parameter_name)
                    parameter_tuples.append(('hourly', 'small', mosmix_parameter_mapping[param_value]))
            
            # Create the request with parameters
            try:
                logger.info(f"Creating MOSMIX request with parameters: {parameter_tuples}")
                
                # Create the request using the new API
                wd_query_result = api(
                    parameters=parameter_tuples,
                    start_date=self.__start_dt_utc,
                    end_date=self.__end_dt_utc + datetime.timedelta(hours=1),
                    settings=settings
                )
            except Exception as e:
                print(f"Error creating MOSMIX request: {e}")
                raise

        if user_station_id is not None:
            wd_nearby_stations = wd_query_result.filter_by_station_id(
                station_id = user_station_id
                )
        else:
            wd_nearby_stations = wd_query_result.filter_by_distance(
                latlon = (lat, lon), 
                distance = distance
                )

        if isinstance(wd_nearby_stations.df,pd.core.frame.DataFrame):
            empty = wd_nearby_stations.df.empty
            if not empty:
                pd_nearby_stations = wd_nearby_stations.df
        elif isinstance(wd_nearby_stations.df,pl.DataFrame):
            empty = wd_nearby_stations.df.is_empty()
            if not empty:
                pd_nearby_stations = wd_nearby_stations.df.to_pandas()
        else:
            empty = True
        if empty:
            raise ValueError("No station found! Increase search radius or change location or station-ID")

        valid_station_data = False
        #Check query result for the stations within the defined distance
        for station_id in pd_nearby_stations["station_id"].values:
            station_name  = pd_nearby_stations.loc[pd_nearby_stations['station_id'] == station_id]['name'].values[0]
            if activate_output:
                print('Checking query result for station ' + station_name, station_id + " ...")
            
            #Get query result for the actual station
            pd_unsorted_data_for_station_list = []
            
            if not use_mosmix:
                # For observation data, we need to get data for each resolution separately
                # and then combine them
                try:
                    # Process the first query result (which we already have)
                    station_data = wd_query_result.filter_by_station_id(station_id=station_id).values.all().df
                    
                    # Check if the DataFrame is empty
                    if hasattr(station_data, 'is_empty') and station_data.is_empty():
                        print(f"No data available for station {station_id} in first query")
                        continue
                        
                    # Convert to pandas if needed
                    if isinstance(station_data, pd.core.frame.DataFrame):
                        pd_station_data = station_data
                    elif isinstance(station_data, pl.DataFrame):
                        pd_station_data = station_data.to_pandas()
                    else:
                        print(f"Unexpected data type for station {station_id}")
                        continue
                        
                    pd_unsorted_data_for_station_list.append(pd_station_data)
                    
                    # If we have more than one query result, process the others
                    if len(wd_query_results) > 1:
                        for i in range(1, len(wd_query_results)):
                            try:
                                # Get data for this station from this query
                                query = wd_query_results[i]
                                
                                # Get data for this station from this query
                                station_data = query.filter_by_station_id(station_id=station_id).values.all().df
                                
                                # Check if the DataFrame is empty
                                if hasattr(station_data, 'is_empty') and station_data.is_empty():
                                    continue
                                    
                                # Convert to pandas if needed
                                if isinstance(station_data, pd.core.frame.DataFrame):
                                    pd_station_data = station_data
                                elif isinstance(station_data, pl.DataFrame):
                                    pd_station_data = station_data.to_pandas()
                                else:
                                    continue
                                    
                                pd_unsorted_data_for_station_list.append(pd_station_data)
                            except Exception as e:
                                print(f"Error getting data for station {station_id} from query {i}: {e}")
                                continue
                    
                    # If we have no data from any query, skip this station
                    if not pd_unsorted_data_for_station_list:
                        print(f"No data available for station {station_id}")
                        continue
                        
                    # Combine all data frames
                    pd_unsorted_data_for_station = pd.concat(pd_unsorted_data_for_station_list, axis=0)
                except ValueError as ve:
                    if "cannot concat empty list" in str(ve):
                        print(f"No data available for station {station_id}")
                        continue
                    else:
                        raise ve
                except Exception as e:
                    print(f"Error getting data for station {station_id}: {e}")
                    continue
            else:
                # For MOSMIX data, we can use the single query result
                try:
                    station_data = wd_query_result.filter_by_station_id(station_id=station_id).values.all().df
                    
                    # Check if the DataFrame is empty
                    if hasattr(station_data, 'is_empty') and station_data.is_empty():
                        print("No data available for this station.")
                        continue
                        
                    # Convert to pandas if needed
                    if isinstance(station_data, pd.core.frame.DataFrame):
                        pd_unsorted_data_for_station = station_data
                    elif isinstance(station_data, pl.DataFrame):
                        pd_unsorted_data_for_station = station_data.to_pandas()
                    else:
                        print(f"Data type incorrect for station {station_id}")
                        continue
                except ValueError as ve:
                    if "cannot concat empty list" in str(ve):
                        print("No data available for this station.")
                        continue
                    else:
                        raise ve
                except Exception as e:
                    print(f"Error getting data for station {station_id}: {e}")
                    continue
                
            # Check if the DataFrame is empty or doesn't have the expected columns
            if pd_unsorted_data_for_station.empty or 'date' not in pd_unsorted_data_for_station.columns:
                print(f"No data available or unexpected data format for station {station_id}")
                continue
                
            pd_sorted_data_for_station = pd.DataFrame()
            pd_unsorted_data_for_station.set_index('date', inplace=True)

            #Format data to get a df with one column for each parameter
            for key in req_parameter_dict.keys():
                pd_sorted_data_for_station[key] = pd_unsorted_data_for_station.loc[pd_unsorted_data_for_station['parameter'] == req_parameter_dict[key]]['value']

            #Fill missing values with NaN, if end time is forced    
            # Check if this is a mosmix request based on the use_mosmix flag
            if not pd_sorted_data_for_station.empty and pd_sorted_data_for_station.index[-1] < self.__end_dt_utc and self.__force_end_time and use_mosmix:
                pd_missing_dates = pd.DataFrame(index = pd.date_range(
                    start = pd_sorted_data_for_station.index[-1] + datetime.timedelta(hours = 1),
                    end   = self.__end_dt_utc.replace(minute = 0)+ datetime.timedelta(hours = 2),
                    freq  = 'H'
                    ))
                pd_sorted_data_for_station = pd.concat([pd_sorted_data_for_station, pd_missing_dates])
            
            quality                         = pd.DataFrame()
            quality.index                   = [True,False,'quality']
            quality[list(req_parameter_dict.keys())] = ""
        
            #Counting the amound of valid and invalid data per parameter
            for column in pd_sorted_data_for_station.columns:
                count           = pd_sorted_data_for_station.isna()[column].value_counts()
                quality[column] = count
                quality         = quality.fillna(0)
            
            #Calculate the percentage of valid data per parameter    
            quality.loc['quality'] = round((quality.loc[0]/(quality.loc[0]+quality.loc[1]))*100,1)
            
            #Prevent console to print name of the variable 
            quality.loc['quality'].name = None
            if activate_output:
                print("Quality of the data set:")
                print(quality.loc['quality'].to_string(header = False))
            
            #If quality is good enough
            if quality.loc['quality'].min() >= min_quality_per_parameter:
                valid_station_data  = True
                if activate_output:
                    print("Query result valid!")
                    print("Station " + station_id + " " + station_name + " used")
                    if user_station_id is None:
                        distance            = str(round(pd_nearby_stations.loc[pd_nearby_stations['station_id'] == station_id]['distance'].values[0]))
                        print("Distance to location: " + distance + " km")
                break
        if not valid_station_data:
            raise Exception("No station with vaild data found!")
        if activate_output:
            print("Query successful!")
            
        station_metadata = (pd_nearby_stations.loc[pd_nearby_stations['station_id'] == station_id])
        # Check if this is an observation or mosmix request based on the network used
        station_metadata['station_type'] = 'OBSERVATION' if not use_mosmix else 'MOSMIX'
        station_metadata['distance_itaration'] = station_metadata.index
        station_metadata['Index'] = range(len(station_metadata))
        station_metadata = station_metadata.set_index('Index')
        
        return (
            pd_sorted_data_for_station,
            station_metadata)
       
    def get_dwd_pv_data(
        self, lat = None, lon = None, station_id = None, distance = 30, min_quality_per_parameter = 80, estimation_methode_lst = ['disc'], extended_solar_data = False, use_mosmix = False
        ):
        """
        Retrieves solar weather data from the DWD database and processes it.
        Solar weather data are:
        - Global Horizontal Irradiance (GHI)  [W/m^2]
        - Direct Normal Irradiance (DNI)      [W/m^2]
        - Diffuse Horizontal Irradiance (DHI) [W/m^2]

        Parameters
        ----------
        lat : float, optional
            Latitude, by default None.
        lon : float, optional
            Longitude, by default None.
        station_id : str, optional
            Station ID specified by the user, by default None.
        distance : int, optional
            Search radius [m] for stations, by default 30.
        min_quality_per_parameter : int, optional
            Minimum percentage of valid data required for each parameter, by default 80.
        estimation_methode_lst : list, optional
            List of estimation methode names, which where used for calculating missing parameters such as dhi dni, by default ['disc'].
        extended_solar_data : bool, optional
            If True, additional solar parameters are included in the output DataFrame (default is False).
        
        Returns
        -------
        station_metadata : pandas.DataFrame
            Metadata of the selected weather station.
        Notes
            -----
            - The query result is saved in class variable pv_data  
            - Station metadate is not saved in class      
    """
        dataset = 'solar'
        raw_dwd_data, station_metadata = self.__get_dwd_data(
            dataset = dataset,
            lat = lat, 
            lon = lon, 
            user_station_id = station_id,
            distance = distance, 
            min_quality_per_parameter = min_quality_per_parameter,
            use_mosmix = use_mosmix
            )   
        if station_metadata.station_type.iloc[0] == 'OBSERVATION':
            self.pv_data = self.__process_observation_parameter(
                 pd_sorted_data_for_station = raw_dwd_data, 
                 pd_station_metadata = station_metadata,
                 dataset = dataset,
                extended_solar_data = extended_solar_data
                 )
        elif station_metadata.station_type.iloc[0] == 'MOSMIX':
            if 'disc' in estimation_methode_lst or 'dirint' in estimation_methode_lst:
                # Skip the solar_est part as it's not needed with the new API
                # The MOSMIX data already contains all necessary parameters
                raw_dwd_data_buf = pd.DataFrame()
                station_metadata_buf = station_metadata.copy()
                if station_metadata_buf.station_type.iloc[0] != 'MOSMIX':
                    raise Exception("Station type error while dataset splitting. Please check times!")
                raw_dwd_data = pd.concat([raw_dwd_data,raw_dwd_data_buf], axis = 1)
            
            self.pv_data = self.__process_mosmix_parameter(
                 pd_sorted_data_for_station = raw_dwd_data, 
                 pd_station_metadata = station_metadata,
                 dataset = dataset,
                 estimation_methode_lst = estimation_methode_lst,
                 extended_solar_data = extended_solar_data
                 )
            
        return station_metadata

    def get_dwd_wind_data(
        self, lat = None, lon = None, station_id = None, distance = 30, min_quality_per_parameter = 80, station_splitting = False, use_mosmix = False
        ):
        """
        Retrieves wind weather data from the DWD database and processes it.
        Wind weather data are:
        - Wind speed [m/s]
        - Pressure at station height[Pa]
        - Temperature at 2 m height[°C]
        The resulting DataFrame contains a MultiIndex with the parameter names and heights.

        Parameters
        ----------
        lat : float, optional
            Latitude, by default None.
        lon : float, optional
            Longitude, by default None.
        station_id : str, optional
            Station ID specified by the user, by default None.
        distance : int, optional
            Search radius [m] for stations, by default 30.
        min_quality_per_parameter : int, optional
            Minimum percentage of valid data required for each parameter, by default 80.
        station_splitting : bool, optional
            if enabled, the function retrieves wind, temperature and pressure data separately (may be not the same station) and combines them afterwards, by default False
       
        Returns
        -------
        station_metadata : pandas.DataFrame
            Metadata of the selected weather station.
        Notes
            -----
            - The query result is saved in class variable wind_data  
            - Station meta data is not saved in class      
        """

        dataset = 'wind'
        if not station_splitting:
            raw_dwd_data, station_metadata = self.__get_dwd_data(
                dataset = dataset, 
                lat = lat, 
                lon = lon, 
                user_station_id = station_id,
                distance = distance, 
                min_quality_per_parameter = min_quality_per_parameter,
                use_mosmix = use_mosmix
                )
        else:
            raw_dwd_data = pd.DataFrame()
            station_metadata = pd.DataFrame()
            for parameter in ['wind_speed', 'temperature', 'pressure']:
                raw_dwd_data_buf, station_metadata_buf = self.__get_dwd_data(
                    dataset = parameter, 
                    lat = lat, 
                    lon = lon, 
                    user_station_id = station_id,
                    distance = distance, 
                    min_quality_per_parameter = min_quality_per_parameter,
                    use_mosmix = use_mosmix
                    )
                station_metadata = pd.concat([station_metadata,station_metadata_buf], axis = 0)
                raw_dwd_data = pd.concat([raw_dwd_data,raw_dwd_data_buf], axis = 1)
                
            if station_metadata.station_type.nunique() != 1:
                raise Exception("Station type error while dataset splitting. Please check times!")
            if station_metadata.station_id.nunique() != 1:
                print ("Warning! Used different stations for one dataset.")
        
        if station_metadata.station_type.iloc[0] == 'OBSERVATION': 
            self.wind_data = self.__process_observation_parameter(
                 pd_sorted_data_for_station = raw_dwd_data,
                 dataset = dataset
                 )
        elif station_metadata.station_type.iloc[0] == 'MOSMIX': 
            self.wind_data = self.__process_mosmix_parameter(
                 pd_sorted_data_for_station = raw_dwd_data,
                 pd_station_metadata = station_metadata,
                 dataset = dataset
                 )
        return station_metadata

    def get_dwd_temp_data(
        self, lat = None, lon = None, station_id = None, distance = 30, min_quality_per_parameter = 80
        ):
        """
        Retrieves temperature weather data from the DWD database and processes it.
        Temperature weather data are:
        - Temperature at 2 m height [°C]

        Parameters
        ----------
        lat : float, optional
            Latitude, by default None.
        lon : float, optional
            Longitude, by default None.
        station_id : str, optional
            Station ID specified by the user, by default None.
        distance : int, optional
            Search radius [m] for stations, by default 30.
        min_quality_per_parameter : int, optional
            Minimum percentage of valid data required for each parameter, by default 80.
        
        Returns
        -------
        station_metadata : pandas.DataFrame
            Metadata of the selected weather station.
        Notes
            -----
            - The query result is saved in class variable temp_data  
            - Station meta data is saved in class variable __temp_station_metadata 
            for usage in get_dwd_mean_temp_hours / get_dwd_mean_temp_days / get_dwd_mean_quarter_hours
        """
        dataset = 'air'
        raw_dwd_data, station_metadata = self.__get_dwd_data(
            dataset = dataset, 
            lat = lat, 
            lon = lon, 
            user_station_id = station_id,
            distance = distance, 
            min_quality_per_parameter = min_quality_per_parameter
            )    
        if station_metadata.station_type.iloc[0] == 'OBSERVATION':
            self.temp_data = self.__process_observation_parameter(
                 pd_sorted_data_for_station = raw_dwd_data, 
                 dataset = dataset
                 )
        elif station_metadata.station_type.iloc[0] == 'MOSMIX': 
            self.temp_data = self.__process_mosmix_parameter(
                 pd_sorted_data_for_station = raw_dwd_data,
                 dataset = dataset
                 )
        return self.__temp_station_metadata
    
    def get_dwd_mean_temp_hours(
        self, lat = None, lon = None, station_id = None, distance = 30, min_quality_per_parameter = 80
        ):
        """
        Resamples temperature data to horly resulution. 
        If there are no temperature data in temp_data, it retrieves temperature weather data from the DWD database and processes it.

        Parameters
        ----------
        lat : float, optional
            Latitude, by default None.
        lon : float, optional
            Longitude, by default None.
        station_id : str, optional
            Station ID specified by the user, by default None.
        distance : int, optional
            Search radius [m] for stations, by default 30.
        min_quality_per_parameter : int, optional
            Minimum percentage of valid data required for each parameter, by default 80.
       
        Returns
        -------
        station_metadata : pandas.DataFrame
            Metadata of the selected weather station.
        Notes
            -----
            - The query result is saved in class variable mean_temp_hours  
            - Station meta data is not saved in class      
        """
        if len(self.temp_data) == 0:
            self.get_dwd_temp_data(
                lat = lat,
                lon = lon,
                station_id = station_id,
                distance = distance, 
                min_quality_per_parameter = min_quality_per_parameter
                )
        self.mean_temp_hours = self.__resample_data(self.temp_data,'60 min')
        return self.__temp_station_metadata
    
    def get_dwd_mean_temp_days(
        self, lat = None, lon = None, station_id = None, distance = 30, min_quality_per_parameter = 80
        ):
        """
        Resamples temperature data to daily resulution. 
        If there are no temperature data in temp_data, it retrieves temperature weather data from the DWD database and processes is.

        Parameters
        ----------
        lat : float, optional
            Latitude, by default None.
        lon : float, optional
            Longitude, by default None.
        station_id : str, optional
            Station ID specified by the user, by default None.
        distance : int, optional
            Search radius [m] for stations, by default 30.
        min_quality_per_parameter : int, optional
            Minimum percentage of valid data required for each parameter, by default 80.
       
        Returns
        -------
        station_metadata : pandas.DataFrame
            Metadata of the selected weather station.
        Notes
            -----
            - The query result is saved in class variable mean_temp_hours  
            - Station meta data is not saved in class      
        """
        if len(self.temp_data) == 0:
            self.get_dwd_temp_data(
                lat = lat,
                lon = lon,
                station_id = station_id,
                distance = distance, 
                min_quality_per_parameter = min_quality_per_parameter
                )
        self.mean_temp_days = self.__resample_data(self.temp_data,'1440 min')
        return self.__temp_station_metadata
    
    def get_dwd_mean_quarter_hours(
        self, lat = None, lon = None, station_id = None, distance = 30, min_quality_per_parameter = 80
        ):
        """
        Resamples temperature data to quarter hour resulution. 
        If there are no temperature data in temp_data, it retrieves temperature weather data from the DWD database and processes it.

        Parameters
        ----------
        lat : float, optional
            Latitude, by default None.
        lon : float, optional
            Longitude, by default None.
        station_id : str, optional
            Station ID specified by the user, by default None.
        distance : int, optional
            Search radius [m] for stations, by default 30.
        min_quality_per_parameter : int, optional
            Minimum percentage of valid data required for each parameter, by default 80.
       
        Returns
        -------
        station_metadata : pandas.DataFrame
            Metadata of the selected weather station.
        Notes
            -----
            - The query result is saved in class variable mean_temp_hours  
            - Station meta data is not saved in class      
        """
        if len(self.temp_data) == 0:
            self.get_dwd_temp_data(
                lat = lat,
                lon = lon,
                station_id = station_id,
                distance = distance, 
                min_quality_per_parameter = min_quality_per_parameter
                )
        self.mean_temp_quarter_hours = self.__resample_data(self.temp_data,'15 min')
        return self.__temp_station_metadata