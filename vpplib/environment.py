# -*- coding: utf-8 -*-
"""
Info
----
This file contains the basic functionalities of the Environment class.
The object "Environment" defines external influences on the system to be simulated.
In addition to weather and location, this also includes regulatory influences.

TODO: Add regulatory influences e. g. photovoltaik maximum power at the grid connection point

"""

import pandas as pd
import os
import zoneinfo
import polars as pl
import  datetime
_ = pl.Config.set_tbl_hide_dataframe_shape(True)
from wetterdienst.provider.dwd.observation import (
    DwdObservationPeriod,
    DwdObservationRequest,
    DwdObservationResolution,
    DwdObservationParameter
)
from wetterdienst.provider.dwd.mosmix import DwdMosmixRequest, DwdMosmixType
import pvlib
from wetterdienst import Settings
from pvlib import irradiance
from pvlib.solarposition import get_solarposition
import matplotlib.pyplot as plt

class Environment(object):
    def __init__(
        self,
        timebase=None,
        timezone=zoneinfo.ZoneInfo("Europe/Berlin"),
        #timezone=("Europe/Berlin"),
        start=None,
        end=None,
        year=None, 
        time_freq="15 min",
        mean_temp_days=[],
        mean_temp_hours=[],
        pv_data=[],
        wind_data=[],
    ):

        """
        Info
        ----
        ...
        
        Parameters
        ----------
        
        ...
        	
        Attributes
        ----------
        
        ...
        
        Notes
        -----
        
        ...
        
        References
        ----------
        
        ...
        
        Returns
        -------
        
        ...
        
        """

        # Configure attribues
        self.timebase = timebase
        self.timezone = timezone
        self.start = start
        self.end = end
        self.year = year
        self.time_freq = time_freq
        self.mean_temp_days = mean_temp_days
        self.mean_temp_hours = mean_temp_hours
        self.pv_data = pv_data
        self.wind_data = wind_data

    def get_pv_data(
        self, file=os.path.join(os.path.dirname(__file__),"../input/pv/dwd_pv_data_2015.csv")
        # self, file="./input/pv/dwd_pv_data_2015.csv"
        ):

        self.pv_data = pd.read_csv(file, index_col="time")
        self.pv_data.index = pd.to_datetime(self.pv_data.index)

        return self.pv_data

    def get_mean_temp_days(
        self, file=os.path.join(os.path.dirname(__file__),"../input/thermal/dwd_temp_days_2015.csv")
        # self, file="./input/thermal/dwd_temp_days_2015.csv"
    ):

        self.mean_temp_days = pd.read_csv(file, index_col="time")

        return self.mean_temp_days

    def get_mean_temp_hours(
        self, file=os.path.join(os.path.dirname(__file__),"../input/thermal/dwd_temp_hours_2015.csv"),
        # self, file="./input/thermal/dwd_temp_hours_2015.csv"
    ):

        self.mean_temp_hours = pd.read_csv(file, index_col="time")

        return self.mean_temp_hours

    def get_wind_data(
        self, file=os.path.join(os.path.dirname(__file__),"../input/wind/dwd_wind_data_2015.csv"), utc=False
        # self, file="./input/wind/dwd_wind_data_2015.csv", utc=False
    ):

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
        df.columns = [l0, l1]
        self.wind_data = df

        return self.wind_data
    
    def __dwd_process(self, df, end_datetime_self_tz):
        """
        Datensatzbeschreibung:
        SOLAR:
            OBSERVATION:
                dni: 10min-Summe der diffusen solaren Strahlung [J/cm^2]
                ghi: 10min-Summe der  Globalstrahlung           [J/cm^2]
            MOSMIX:
                ghi: (Stundensumme?)  Globalstrahlung           [kJ/m^2]
        TEMPERATUR:
            OBSERVATION:
                temperatur: Lufttemperatur in 2 m Höhe        [°C]
                pressure: Luftdruck in Stationshoehe          [hPa]
            MOSMIX:
                temperatur: Temperatur 2m über der Oberfläche [Kelvin]
                pressure:   Luftdruck, reduziert              [Pa]
                
        WIND:
            OBSERVATION:
                
            MOSMIX:
                wind_speed : Windgeschwindigkeit [m/s]
        vpp_lib:
            K
            Pa
            W/m2
            m/s
        """
        df.reset_index(inplace=True)
        timezone_aware_date_list = list()
        for date in df.date:
            timezone_aware_date_list.append(
                date.tz_convert(self.timezone)
                )
                
        df['date_tz'] = timezone_aware_date_list
        df.set_index('date_tz',inplace=True)
        df = df.drop('date', axis = 1)
            
        #Missing data is marked with -999. Replace by NaN
        df.where(cond=(df[df.columns] != -999), other=None, inplace=True)
        #Fill NaN
        df.interpolate(inplace=True)
        
        #Resample to given resulotion and interpolate between missing values
        df = df.resample(self.time_freq).mean().interpolate(method = 'linear')
            
            
        df.index.rename("time", inplace=True)
        if df.index[-1] > end_datetime_self_tz:
            df = df[df.index[0]:end_datetime_self_tz]
        return df

    def __get_solar_parameter (self, input_df, lat, lon, height, methode = 'disc'):
        df             = input_df.copy()
        df.temperature = df.temperature - 273.15
        df.drew_point    = df.drew_point - 273.15
        
        """
        PVLIB EINHEITEN
        pressure   : Pa
        ghi        : W/m2
        temperaure : °C
        
        MOSMIX:
        pressure   : Pa
        ghi        : kJ/m2
        temperature: K  
        
        vpp_lib:
            K
            Pa
            W/m2
            m/s
        """
        solpos = get_solarposition(
                    df.index.shift(freq="-30T"), 
                    latitude    = lat,
                    longitude   = lon, 
                    altitude    = height,
                    pressure    = df.pressure,
                    temperature = df.temperature
                    )
        solpos.index = df.index
        
        if methode == 'disc':
            """
            DISC Algorytmus
            """
            out_disc = irradiance.disc(
                        ghi             = df.ghi, 
                        solar_zenith    = solpos.zenith, 
                        datetime_or_doy = df.index, 
                        pressure        = df.pressure
                        )
        
            df_disc = irradiance.complete_irradiance(
                        solar_zenith = solpos.apparent_zenith, 
                        ghi          = df.ghi, 
                        dni          = out_disc.dni,
                        dhi          = None
                        )
            out_disc['dhi'] = df_disc.dhi
            out_df = out_disc.drop(['kt', 'airmass'],axis = 1)
            
        elif methode == 'erbs':
            """
            erbs
            """
            out_erbs = irradiance.erbs(
                        ghi             = df.ghi,
                        zenith          = solpos.zenith, 
                        datetime_or_doy = df.index
                        )
            out_df = out_erbs.drop(['kt'],axis = 1)
            
        elif methode == 'dirint':
            """
            dirint
            """
            dni_dirint = irradiance.dirint(
                            ghi          = df.ghi, 
                            solar_zenith = solpos.zenith, 
                            times        = df.index, 
                            pressure     = df.pressure,
                            temp_dew     = df.drew_point
                            )
        
            df_dirint = irradiance.complete_irradiance(
                            solar_zenith = solpos.apparent_zenith,
                            ghi          = df.ghi, 
                            dni          = dni_dirint,
                            dhi          = None
                            )
            out_dirint = pd.DataFrame(
                            {'dni': dni_dirint, 'dhi': df_dirint.dhi}, index=df.index
                            )
            out_df = out_dirint
            
        elif methode == 'boland':
            """
            boland
            """
            out_boland = irradiance.boland(
                            ghi             = df.ghi,
                            solar_zenith    = solpos.zenith,
                            datetime_or_doy = df.index, 
                            a_coeff         = 8.645, 
                            b_coeff         = 0.613, 
                            min_cos_zenith  = 0.065, 
                            max_zenith      = 87
                            )
            out_df = out_boland.drop(['kt'], axis = 1)

        return out_df

    def __calc_solar_power(self, df, query_type):
        df_power = pd.DataFrame(index=df.index)
        
        df_power['ghi'] = 0
        if 'dni' in df.columns:
            df_power['dni'] = 0
        if 'dhi' in df.columns:
            df_power['dhi'] = 0
        
        resulution = (df.index[1]-df.index[0]).seconds
        if query_type == 'MOSMIX':
            'Input: [kJ/m^2/resulution]'
            for column in df_power.columns:
                df_power[column] = df[column] * 1000 / resulution #kJ/m2 -> J/m2 -> W/m2
        elif query_type == 'OBSERVATION':
            'Input: [J/cm^2/resulution]'
            for column in df_power.columns:
                df_power[column] = df[column] * 10e3 / resulution #/J/cm2 -> J/m2 -> W/m2
        
        'Output: [W/m^2]'
        return df_power
    
    def __get_dwd_data(self, dataset, lat, lon, min_quality_per_parameter = 60, distance = 30):
        roughness_length = 0.15
        
        start_datetime_self_tz = datetime.datetime.strptime(self.start, '%Y-%m-%d %H:%M:%S')  .replace(tzinfo=self.timezone)
        end_datetime_self_tz   = datetime.datetime.strptime(self.end  , '%Y-%m-%d %H:%M:%S')  .replace(tzinfo=self.timezone)
        start_datetime_utc     = (start_datetime_self_tz - start_datetime_self_tz.utcoffset()).replace(tzinfo = datetime.timezone.utc)
        end_datetime_utc       = (end_datetime_self_tz   - end_datetime_self_tz.utcoffset()  ).replace(tzinfo = datetime.timezone.utc)

        dataset_dict = {
            'solar' : ['ghi', 'dhi'],
            'air'   : ['pressure' , 'temperature'],
            'wind'  : ['wind_speed']
            }

        avalible_parameter_dict = {
            "ghi"         : "radiation_global", 
            "dhi"         : "radiation_sky_short_wave_diffuse",
            "pressure"    : "pressure_air_site", 
            "temperature" : "temperature_air_mean_200",
            "wind_speed"  : "wind_speed", 
            "drew_point"    : "temperature_dew_point_mean_200"
                                }
        
        #Create a dictionsry with the parameters to query
        req_parameter_dict = {param: avalible_parameter_dict[param] for param in dataset_dict[dataset]}
        
        #Get time from dwd server
        wd_time_result = DwdObservationRequest(
            parameter  = "wind_speed",
            resolution = DwdObservationResolution.HOURLY,
        )

        settings = Settings.default()
        settings.ts_si_units = False

        if start_datetime_utc <= wd_time_result.now - datetime.timedelta(hours = 1):
            #Observation database
            if end_datetime_utc > wd_time_result.now - datetime.timedelta(hours = 1):
                print("End date is in the future.")
                end_datetime_utc = wd_time_result.now - datetime.timedelta(hours = 1)
                print("Changed end time to:", end_datetime_utc)

            #Get weather data for your location from dwd observation database
            wd_query_result = DwdObservationRequest(
                parameter  = list(req_parameter_dict.values()),
                resolution = DwdObservationResolution.MINUTE_10,
                start_date = start_datetime_utc,
                settings   = settings,
                end_date   = end_datetime_utc + datetime.timedelta(hours = 1),
            )
        elif start_datetime_utc > wd_time_result.now - datetime.timedelta(hours = 1):
            #MOSMIX database is updated every hour
            if dataset == 'solar':
                #dhi not available for mosmix
                req_parameter_dict.pop("dhi")
                #get additional parameter for calculating dhi with pvlib
                additional_parameter_lst = ["pressure", "temperature", "drew_point"]
                for additional_parameter in additional_parameter_lst:
                    req_parameter_dict.update({additional_parameter : avalible_parameter_dict[additional_parameter]}) 
            #pressure is called pressure_air_site_reduced in mosmix
            if "pressure" in req_parameter_dict:
                req_parameter_dict.update({"pressure" : "pressure_air_site_reduced"})
            
            #Get weather data for your location from dwd MOSMIX database
            wd_query_result = DwdMosmixRequest(
                parameter   = list(req_parameter_dict.values()), 
                mosmix_type = DwdMosmixType.LARGE,
                settings    =  settings
                )

        wd_available_stations = wd_query_result.filter_by_distance(latlon = (lat, lon), distance = distance)

        if isinstance(wd_available_stations.df,pd.core.frame.DataFrame):
            empty = wd_available_stations.df.empty
            if not empty:
                pd_available_stations = wd_available_stations.df
        elif isinstance(wd_available_stations.df,pl.DataFrame):
            empty = wd_available_stations.df.is_empty()
            if not empty:
                pd_available_stations = wd_available_stations.df.to_pandas()
        else:
            empty = True
        if empty:
            print("No station found!")
            return

        valid_station_data = False
        #Check query result for the stations within the defined distance
        for station_id in pd_available_stations["station_id"].values:
            station_name  = pd_available_stations.loc[pd_available_stations['station_id'] == station_id]['name'].values[0]
            print('Checking query result for station ' + station_name, station_id + " ...")
            
            #Get query result for the actual station
            wd_data_for_station = wd_query_result.filter_by_station_id(station_id=station_id).values.all().df

            if isinstance(wd_data_for_station,pd.core.frame.DataFrame):
                pd_data_for_station = wd_data_for_station
            elif isinstance(wd_data_for_station,pl.DataFrame):
                pd_data_for_station = wd_data_for_station.to_pandas()
            else:
                print("Data type incorrect")
                return
                
            dwd_result_processed        = pd.DataFrame()
            pd_data_for_station.set_index('date', inplace=True)

            #Format data to get a df with one column for each parameter
            for key in req_parameter_dict.keys():
                dwd_result_processed[key] = pd_data_for_station.loc[pd_data_for_station['parameter'] == req_parameter_dict[key]]['value']
                
            quality                         = pd.DataFrame()
            quality.index                   = [True,False,'quality']
            quality[list(req_parameter_dict.keys())] = ""
        
            #Counting the amound of valid and invalid data per parameter
            for column in dwd_result_processed.columns:
                count           = dwd_result_processed.isna()[column].value_counts()
                quality[column] = count
                quality         = quality.fillna(0)
            
            #Calculate the percentage of valid data per parameter    
            quality.loc['quality'] = round((quality.loc[0]/(quality.loc[0]+quality.loc[1]))*100,1)
            print("Quality of the data set:",quality.loc['quality'].values)
            
            #If quality is good enough
            if quality.loc['quality'].min() >= min_quality_per_parameter:
                distance            = str(round(pd_available_stations.loc[pd_available_stations['station_id'] == station_id]['distance'].values[0]))
                valid_station_data  = True
                print("Query result valid!")
                print("Station " + station_id + " " + station_name + " used")
                print("Distance to location: " + distance + " km")
                break
        if not valid_station_data:
            print("No station found")
            return
        print("Query successful!")

        if isinstance(wd_query_result,DwdObservationRequest):
            if dataset == 'solar': 
                #Calculate dni if df is PV data
                dwd_result_processed['dni'] = dwd_result_processed.ghi - dwd_result_processed.dhi
                #Calculate power from irradiance
                dwd_result_processed.update(self.__calc_solar_power(dwd_result_processed,'OBSERVATION'), overwrite=True)
            elif dataset == 'air':
                dwd_result_processed.pressure    = dwd_result_processed.pressure * 100
                dwd_result_processed.temperature = dwd_result_processed.temperature + 273.15
            elif dataset == 'wind':
                dwd_result_processed["roughness_length"] = roughness_length
            
        if isinstance(wd_query_result,DwdMosmixRequest):
            if dataset == 'solar':
                dwd_result_processed.update( self.__calc_solar_power(dwd_result_processed, 'MOSMIX'), overwrite=True)
                #lst_methodes = ['disc','erbs','dirint','boland']
                #for methode in lst_methodes:
                calculated_solar_parameter = self.__get_solar_parameter(
                        input_df = dwd_result_processed, 
                        lat      = pd_available_stations.loc[pd_available_stations['station_id'] == station_id]['latitude' ].values[0], 
                        lon      = pd_available_stations.loc[pd_available_stations['station_id'] == station_id]['longitude'].values[0],
                        height   = pd_available_stations.loc[pd_available_stations['station_id'] == station_id]['height'   ].values[0])
                
                dwd_result_processed = dwd_result_processed.merge(right = calculated_solar_parameter, left_index = True, right_index = True)
                dwd_result_processed.drop(additional_parameter_lst, axis = 1, inplace = True)

            elif dataset == 'air':
                """boarometrische höhenformel"""
                height = pd_available_stations.loc[pd_available_stations['station_id'] == station_id]['height'].values[0]
                """ var chatgpt """
                dwd_result_processed['pressure'] = (
                    dwd_result_processed.pressure * ( 1 - ( -0.0065  * height) / dwd_result_processed.temperature) ** ((9.81 * 0.02897) / (8.314 * -0.0065))
                    )
                """var dwd
                import math
                h1 = height
                T0 = 288.15
                y = -0.0065
                dwd_result_processed['druck_neu_dwd'] = (
                dwd_result_processed.pressure / (
                    math.e ** (
                        h1/(29.27*(T0 + y * (h1/2)))
                        )
                    ))
                """
            elif dataset == 'wind':
                dwd_result_processed["roughness_length"] = roughness_length
            #Observation data discribes the value for the last timestep. Mosmix forecasts the value for the next timestep
            #Shift by -1 to aling MOSMIX to Observation
            dwd_result_processed = dwd_result_processed.shift(-1)
             
        
        return self.__dwd_process(dwd_result_processed, end_datetime_self_tz)
    
    def get_dwd_pv_data(self,lat,lon,distance = 30):
        self.pv_data = self.__get_dwd_data('solar', lat, lon)
        return self.pv_data

    def get_dwd_wind_data(self,lat,lon,distance = 30):
        self.wind_data = self.__get_dwd_data('wind', lat, lon)
        return self.wind_data 

    def get_dwd_temp_data(self,lat,lon,distance = 30):
        self.mean_temp_hours = self.__get_dwd_data('air', lat, lon)
        return self.mean_temp_hours 




