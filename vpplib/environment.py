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
    DwdObservationRequest,
    DwdObservationResolution,
)
from wetterdienst.provider.dwd.mosmix import DwdMosmixRequest, DwdMosmixType
from wetterdienst import Settings
from pvlib import irradiance
from pvlib.solarposition import get_solarposition
import numpy as np
import collections

class Environment(object):
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
        pv_data=[],
        wind_data=[],
        temp_data=[],
        surpress_output_globally = False
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

        # Configure attributes
        self.timebase = timebase
        self.timezone = zoneinfo.ZoneInfo(timezone)
        self.start = start
        self.end = end
        self.year = year
        self.time_freq = time_freq
        self.mean_temp_days = mean_temp_days
        self.mean_temp_hours = mean_temp_hours
        self.pv_data = pv_data
        self.wind_data = wind_data
        self.temp_data = temp_data
        self.surpress_output_globally = surpress_output_globally
        self.__internal_start_datetime_with_class_timezone    =   datetime.datetime.strptime(self.start, '%Y-%m-%d %H:%M:%S').replace(tzinfo = self.timezone)
        self.__internal_end_datetime_with_class_timezone      =   datetime.datetime.strptime(self.end  , '%Y-%m-%d %H:%M:%S').replace(tzinfo = self.timezone)
        self.__internal_start_datetime_utc = (self.__internal_start_datetime_with_class_timezone - self.__internal_start_datetime_with_class_timezone.utcoffset()).replace(tzinfo = datetime.timezone.utc, microsecond = 0)
        self.__internal_end_datetime_utc   = (self.__internal_end_datetime_with_class_timezone - self.__internal_end_datetime_with_class_timezone.utcoffset()    ).replace(tzinfo = datetime.timezone.utc, microsecond = 0)
          
        if self.__internal_start_datetime_utc > self.__internal_end_datetime_utc:
            raise ValueError("End date must be greater than start date")
        if self.__internal_start_datetime_utc + datetime.timedelta(hours=1) > self.__internal_end_datetime_utc:
            raise ValueError("End date must be at least one hour longer than the start date")

    @property
    def __start_dt_utc(self):
        return self.__internal_start_datetime_utc

    @__start_dt_utc.setter
    def __start_dt_utc(self, new___start_dt_utc):
        if new___start_dt_utc.tzinfo != datetime.timezone.utc:
            raise ValueError('@__start_dt_utc.setter: new time not given in utc')
        new___start_dt_utc = new___start_dt_utc.replace(microsecond = 0)
        self.__internal_start_datetime_utc = new___start_dt_utc
        time_wo_offset = new___start_dt_utc.replace(tzinfo = self.timezone)
        self.__internal_start_datetime_with_class_timezone = time_wo_offset + time_wo_offset.utcoffset()
        self.start = str(self.__internal_start_datetime_with_class_timezone.replace(tzinfo = None))
        print("Setted new start time to: ", self.__internal_end_datetime_with_class_timezone) and not self.surpress_output_globally
    
    @property
    def __end_dt_utc(self):
        return self.__internal_end_datetime_utc

    @__end_dt_utc.setter
    def __end_dt_utc(self, new___end_dt_utc):
        if new___end_dt_utc.tzinfo != datetime.timezone.utc:
            raise ValueError('@__end_dt_utc.setter: new time not given in utc')
        new___end_dt_utc = new___end_dt_utc.replace(microsecond=0)
        self.__internal_end_datetime_utc = new___end_dt_utc
        time_wo_offset = new___end_dt_utc.replace(tzinfo = self.timezone)
        self.__internal_end_datetime_with_class_timezone = time_wo_offset + time_wo_offset.utcoffset()
        self.end = str(self.__internal_end_datetime_with_class_timezone.replace(tzinfo = None))
        print("Setted new end time to: ", self.__internal_end_datetime_with_class_timezone)  and not self.surpress_output_globally
        
    @property
    def __start_dt_target_tz(self):
        return self.__internal_start_datetime_with_class_timezone

    @__start_dt_target_tz.setter
    def __start_dt_target_tz(self, new_start_dt):
        if new_start_dt.tzinfo != self.timezone:
            raise ValueError('@__start_dt_target_tz.setter: new time not given in target timezone')
        new_start_dt = new_start_dt.replace(microsecond = 0)
        self.__internal_start_datetime_with_class_timezone = new_start_dt  
        self.__internal_start_datetime_utc = (new_start_dt - new_start_dt.utcoffset()).replace(tzinf = datetime.timezone.utc)
        self.start = str(self.__internal_start_datetime_with_class_timezone.replace(tzinfo = None))
        print("Setted new start time to: ", self.__internal_start_datetime_with_class_timezone)  and not self.surpress_output_globally
        
    @property
    def __end_dt_target_tz(self):
        return self.__internal_end_datetime_with_class_timezone

    @__end_dt_target_tz.setter
    def __end_dt_target_tz(self, new_end_dt):
        if new_end_dt.tzinfo != self.timezone:
            raise ValueError('@__end_dt_target_tz.setter: new time not given in target timezone')
        new_end_dt = new_end_dt.replace(microsecond=0)
        self.__internal_end_datetime_with_class_timezone = new_end_dt
        self.__internal_end_datetime_utc = (new_end_dt - new_end_dt.utcoffset()).replace(tzinfo = datetime.timezone.utc)
        self.end = str(self.__internal_end_datetime_with_class_timezone.replace(tzinfo = None))
        print("Setted new end time to: ", self.__internal_end_datetime_with_class_timezone)  and not self.surpress_output_globally



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

    def get_time_from_dwd(self):
        #Get time from dwd server
        wd_time_result = DwdObservationRequest(
            parameter  = "wind_speed",
            resolution = DwdObservationResolution.HOURLY,
        )
        return wd_time_result.now.replace(second=0,microsecond=0)
        
    def __get_solar_parameter (self, input_df, lat, lon, height, methode = 'disc', use_methode_name_in_columns = False):
        df             = input_df.copy()
        df.temperature = df.temperature - 273.15
        df.drew_point  = df.drew_point - 273.15
        
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
            out_erbs = irradiance.erbs(
                        ghi             = df.ghi,
                        zenith          = solpos.zenith, 
                        datetime_or_doy = df.index
                        )
            out_df = out_erbs.drop(['kt'],axis = 1)
            
        elif methode == 'dirint':
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
        
        if use_methode_name_in_columns: out_df.columns = [str(col) + '_' + methode for col in out_df.columns]

        return out_df

    def __get_solar_power_from_energy(self, df, query_type):
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
   
     
    def __resample_data(self, df, time_freq = None):
        #df = df.copy()
        if time_freq is None:
            time_freq =  self.time_freq
        df.index.rename("time", inplace=True)
        
        df.reset_index(inplace=True)
        timezone_aware_date_list = list()
        for time in df.time:
            timezone_aware_date_list.append(
                time.tz_convert(self.timezone)
                )
                
        df['time_tz'] = timezone_aware_date_list
        df.set_index('time_tz',inplace = True)
        df.drop('time', axis = 1, inplace = True)
        df.index.rename("time", inplace = True)
        
            
        #Missing data is marked with -999. Replace by NaN
        df.where(cond=(df[df.columns] != -999), other=None, inplace=True)
        #Fill NaN
        df.interpolate(inplace=True)
        
        #Resample to given resulotion and interpolate over missing values
        df = df.resample(time_freq).mean().interpolate(method = 'linear')
        
        if df.index[-1] > self.__end_dt_target_tz:
            df = df[df.index[0]:self.__end_dt_target_tz]
        
        df = df.reindex(sorted(df.columns), axis=1)
        df = round(df,2)
        return df
    
    
    def __prepare_data_for_windpowerlib (self, pd_weather_data_for_station, pd_station_metadata, query_type):
        pd_weather_data_for_station["roughness_length"] = 0.15
        
        """
        TODO: Insert values for station height correctly --> Consult / compare with Windpower lib
        
        rename_dict = {
            'wind_speed'       : pd_station_metadata['height'].values[0],
            'pressure'         : pd_station_metadata['height'].values[0],
            'temperature'      : pd_station_metadata['height'].values[0] + 2,
            'roughness_length' : pd_station_metadata['height'].values[0],
            }
        """
        rename_dict = {
            'wind_speed'       : 10,
            'pressure'         : 0,
            'temperature'      : 2,
            'roughness_length' : 0,
            }
        od = collections.OrderedDict(sorted(rename_dict.items()))
        pd_weather_data_for_station = pd_weather_data_for_station.reindex(sorted(pd_weather_data_for_station.columns), axis=1)
        height = list()
        for value in od.values():
            height.append(value)
        pd_weather_data_for_station.columns = [pd_weather_data_for_station.columns, np.array(height)]
        if query_type == 'OBSERVATION':
            pd_weather_data_for_station.pressure = pd_weather_data_for_station.pressure * 100 # hPa to Pa
            pd_weather_data_for_station.temperature = pd_weather_data_for_station.temperature + 274.15  # °C to K
        return pd_weather_data_for_station
    
    
    def __process_observation_parameter (self, pd_weather_data_for_station, pd_station_metadata, dataset):
        """
        Datensatzbeschreibung OBSERVATION:
        SOLAR:
            dni: 10min-Summe der diffusen solaren Strahlung [J/cm^2]
            ghi: 10min-Summe der  Globalstrahlung           [J/cm^2]
        TEMPERATUR:
            temperatur: Lufttemperatur in 2 m Höhe  [°C]
            pressure: Luftdruck in Stationshoehe    [hPa]       
        WIND:
            wind_speed : Windgeschwindigkeit [m/s]
        """
        if dataset == 'solar': 
            pd_weather_data_for_station['dni'] = pd_weather_data_for_station.ghi - pd_weather_data_for_station.dhi
            #Calculate power from irradiance
            pd_weather_data_for_station.update(self.__get_solar_power_from_energy(pd_weather_data_for_station,'OBSERVATION'), overwrite=True)
        elif dataset == 'wind':
            pd_weather_data_for_station = self.__prepare_data_for_windpowerlib(pd_weather_data_for_station=pd_weather_data_for_station,query_type='OBSERVATION',pd_station_metadata = pd_station_metadata)
        return self.__resample_data(pd_weather_data_for_station)
        
        
    def __process_mosmix_parameter (self, pd_weather_data_for_station, dataset, pd_station_metadata, station_id = None, additional_parameter_lst= None):
        """
        Datensatzbeschreibung MOSMIX:
        SOLAR:
                ghi: (Stundensumme?)  Globalstrahlung           [kJ/m^2]
        TEMPERATUR:
                temperatur: Temperatur 2m über der Oberfläche [Kelvin]
                pressure:   Luftdruck, reduziert              [Pa]
        WIND:
                wind_speed : Windgeschwindigkeit [m/s]
        """
        if dataset == 'solar':
            pd_weather_data_for_station.update( self.__get_solar_power_from_energy(pd_weather_data_for_station, 'MOSMIX'), overwrite=True)
            #lst_methodes = ['disc','erbs','dirint','boland']
            #for methode in lst_methodes:
            calculated_solar_parameter = self.__get_solar_parameter(
                    input_df = pd_weather_data_for_station, 
                    lat      = pd_station_metadata['latitude' ].values[0], 
                    lon      = pd_station_metadata['longitude'].values[0],
                    height   = pd_station_metadata['height'   ].values[0])
                    #methode  = methode)
            
            pd_weather_data_for_station = pd_weather_data_for_station.merge(right = calculated_solar_parameter, left_index = True, right_index = True)
            pd_weather_data_for_station.drop(additional_parameter_lst, axis = 1, inplace = True)
        elif dataset == 'air':
            pd_weather_data_for_station.temperature = pd_weather_data_for_station.temperature - 273.15  # °K to C
        elif dataset == 'wind':
            height = pd_station_metadata['height'].values[0]
            """ https://de.wikipedia.org/wiki/Barometrische_Höhenformel """
            pd_weather_data_for_station['pressure'] = (
                pd_weather_data_for_station.pressure * ( 1 - ( -0.0065  * height) / pd_weather_data_for_station.temperature) ** ((9.81 * 0.02897) / (8.314 * -0.0065))
                )
            pd_weather_data_for_station = self.__prepare_data_for_windpowerlib(pd_weather_data_for_station=pd_weather_data_for_station,query_type='MOSMIX',pd_station_metadata=pd_station_metadata)
        #Observation data discribes the value for the last timestep. MOSMIX forecasts the value for the next timestep
        #Shift by -1 to aling MOSMIX to Observation
        pd_weather_data_for_station = pd_weather_data_for_station.shift(-1)
        return self.__resample_data(pd_weather_data_for_station)
    
    
    def __get_dwd_data(self, dataset, lat, lon, distance = 30, min_quality_per_parameter = 80):
        activate_output = not self.surpress_output_globally

        dataset_dict = {
            'solar' : ['ghi', 'dhi'],
            'air'   : ['temperature'],
            'wind'  : ['wind_speed', 'pressure', 'temperature']
            }

        avalible_parameter_dict = {
            "ghi"         : "radiation_global", 
            "dhi"         : "radiation_sky_short_wave_diffuse",
            "pressure"    : "pressure_air_site", 
            "temperature" : "temperature_air_mean_200",
            "wind_speed"  : "wind_speed", 
            "drew_point"  : "temperature_dew_point_mean_200"
            }
        
        #Create a dictionsry with the parameters to query
        req_parameter_dict = {param: avalible_parameter_dict[param] for param in dataset_dict[dataset]}
        
        time_now = self.get_time_from_dwd()
        settings = Settings.default()
        settings.ts_si_units = False
        
        #observation data is updated every full hour
        observation_end_date = time_now.replace(minute = 0 , second = 0, microsecond = 0)

        if self.__start_dt_utc <= observation_end_date - datetime.timedelta(hours = 1):
            print("Using observation database.") and activate_output
            if self.__end_dt_utc > observation_end_date:
                print("End date is in the future.") and activate_output
                self.__end_dt_utc = observation_end_date

            #Get weather data for your location from dwd observation database
            wd_query_result = DwdObservationRequest(
                parameter  = list(req_parameter_dict.values()),
                resolution = DwdObservationResolution.MINUTE_10,
                start_date = self.__start_dt_utc,
                end_date   = self.__end_dt_utc,
                settings   = settings,
            )
        else:
            if self.__start_dt_utc > time_now + datetime.timedelta(hours = 240):
                raise ValueError("No forecast data avaliable for this time")
            if self.__end_dt_utc >  time_now.replace(minute = 0 , second = 0, microsecond = 0) + datetime.timedelta(hours = 240):
                self.__end_dt_utc = time_now.replace(minute = 0 , second = 0, microsecond = 0) + datetime.timedelta(hours = 240)
            print("Using momsix database.") and activate_output
            if dataset == 'solar':
                #dhi is not available for MOSMIX
                req_parameter_dict.pop("dhi")
                #get additional parameter for calculating dhi with pvlib
                additional_parameter_lst = ["pressure", "temperature", "drew_point"]
                req_parameter_dict.update({param: avalible_parameter_dict[param] for param in additional_parameter_lst})
            #pressure is called pressure_air_site_reduced in MOSMIX
            if "pressure" in req_parameter_dict:
                req_parameter_dict.update({"pressure" : "pressure_air_site_reduced"})
            
            #Get weather data for your location from dwd MOSMIX database
            wd_query_result = DwdMosmixRequest(
                parameter   = list(req_parameter_dict.values()), 
                mosmix_type = DwdMosmixType.LARGE,
                settings    =  settings,
                start_date  = self.__start_dt_utc,
                end_date    = self.__end_dt_utc
                )

        wd_nearby_stations = wd_query_result.filter_by_distance(latlon = (lat, lon), distance = distance)

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
            raise ValueError("No station found! Increase search radius or change location")

        valid_station_data = False
        #Check query result for the stations within the defined distance
        for station_id in pd_nearby_stations["station_id"].values:
            station_name  = pd_nearby_stations.loc[pd_nearby_stations['station_id'] == station_id]['name'].values[0]
            print('Checking query result for station ' + station_name, station_id + " ...") and activate_output
            
            #Get query result for the actual station
            wd_data_for_station = wd_query_result.filter_by_station_id(station_id=station_id).values.all().df

            if isinstance(wd_data_for_station,pd.core.frame.DataFrame):
                pd_data_for_all_stations = wd_data_for_station
            elif isinstance(wd_data_for_station,pl.DataFrame):
                pd_data_for_all_stations = wd_data_for_station.to_pandas()
            else:
                raise Exception("Data type incorrect")
                
            pd_weather_data_for_station = pd.DataFrame()
            pd_data_for_all_stations.set_index('date', inplace=True)

            #Format data to get a df with one column for each parameter
            for key in req_parameter_dict.keys():
                pd_weather_data_for_station[key] = pd_data_for_all_stations.loc[pd_data_for_all_stations['parameter'] == req_parameter_dict[key]]['value']
                
            """
            Not yet implemented: The MOSMIX database provided data for !UP TO! 240 hours. 
            The resulting data set does not consist of index 0-240 but 0-querying
            TODO: Add variable in function call, depending on which the result is extended to 240 hours. 
                  The end time must then also be adjusted
            
            if pd_weather_data_for_station.index[-1] < self.__end_dt_utc:
                pd_missing_dates = pd.DataFrame(index = pd.date_range(
                    start = pd_weather_data_for_station.index[-1] + datetime.timedelta(hours = 1),
                    end   = self.__end_dt_utc,
                    freq  = 'H'
                    ))
                pd_weather_data_for_station = pd.concat([pd_weather_data_for_station, pd_missing_dates])
            """
 
            quality                         = pd.DataFrame()
            quality.index                   = [True,False,'quality']
            quality[list(req_parameter_dict.keys())] = ""
        
            #Counting the amound of valid and invalid data per parameter
            for column in pd_weather_data_for_station.columns:
                count           = pd_weather_data_for_station.isna()[column].value_counts()
                quality[column] = count
                quality         = quality.fillna(0)
            
            #Calculate the percentage of valid data per parameter    
            quality.loc['quality'] = round((quality.loc[0]/(quality.loc[0]+quality.loc[1]))*100,1)
            
            quality.loc['quality'].name = None
            if activate_output:
                print("Quality of the data set:")
                print(quality.loc['quality'].to_string(header = False))
            
            #If quality is good enough
            if quality.loc['quality'].min() >= min_quality_per_parameter:
                distance            = str(round(pd_nearby_stations.loc[pd_nearby_stations['station_id'] == station_id]['distance'].values[0]))
                valid_station_data  = True
                if activate_output:
                    print("Query result valid!")
                    print("Station " + station_id + " " + station_name + " used")
                    print("Distance to location: " + distance + " km")
                break
        if not valid_station_data:
            raise Exception("No station with vaild data found!")
        print("Query successful!") and activate_output
        

        if isinstance(wd_query_result,DwdObservationRequest):
           return self.__process_observation_parameter(
                pd_weather_data_for_station, 
                pd_station_metadata = pd_nearby_stations.loc[pd_nearby_stations['station_id'] == station_id],
                dataset = dataset
                )
        if isinstance(wd_query_result,DwdMosmixRequest):
           return self.__process_mosmix_parameter(
                pd_weather_data_for_station = pd_weather_data_for_station, 
                dataset = dataset, 
                pd_station_metadata = pd_nearby_stations.loc[pd_nearby_stations['station_id'] == station_id],
                additional_parameter_lst = additional_parameter_lst if 'additional_parameter_lst' in locals() else None
                )
    
    def get_dwd_pv_data(self, lat, lon, distance = 30, min_quality_per_parameter = 80):
        self.pv_data = self.__get_dwd_data(
            dataset = 'solar', 
            lat = lat, 
            lon = lon, 
            distance = distance, 
            min_quality_per_parameter = min_quality_per_parameter
            )
        return self.pv_data

    def get_dwd_wind_data(self, lat, lon, distance = 30, min_quality_per_parameter = 80):
        self.wind_data = self.__get_dwd_data(
            dataset = 'wind', 
            lat = lat, 
            lon = lon, 
            distance = distance, 
            min_quality_per_parameter = min_quality_per_parameter
            )
        return self.wind_data 

    def get_dwd_temp_data(self,lat,lon,distance = 30, min_quality_per_parameter = 80):
        self.temp_data = self.__get_dwd_data(
            dataset = 'air', 
            lat = lat, 
            lon = lon, 
            distance = distance, 
            min_quality_per_parameter = min_quality_per_parameter
            )
        return self.temp_data
    
    def get_dwd_mean_temp_hours(self, lat, lon, distance = 30, min_quality_per_parameter = 80):
        if len(self.temp_data) == 0:
            self.get_dwd_temp_data(
                lat = lat,
                lon = lon, 
                distance = distance, 
                min_quality_per_parameter = min_quality_per_parameter
                )
        self.mean_temp_hours = self.__resample_data(self.temp_data,'60 min')
    
    def get_dwd_mean_temp_days(self,lat,lon,distance = 30, min_quality_per_parameter = 80):
        if len(self.temp_data) == 0:
            self.get_dwd_temp_data(
                lat = lat, 
                lon = lon, 
                distance = distance, 
                min_quality_per_parameter = min_quality_per_parameter
                )
        self.mean_temp_days = self.__resample_data(self.temp_data,'1440 min')
        




