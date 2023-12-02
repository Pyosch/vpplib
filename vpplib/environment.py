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
        self.__internal_start_datetime_with_class_timezone    =   datetime.datetime.strptime(
            self.start, '%Y-%m-%d %H:%M:%S'
            ).replace(tzinfo = self.timezone)
        self.__internal_end_datetime_with_class_timezone      =   datetime.datetime.strptime(
            self.end  , '%Y-%m-%d %H:%M:%S'
            ).replace(tzinfo = self.timezone)
        self.__internal_start_datetime_utc = (
            self.__internal_start_datetime_with_class_timezone - self.__internal_start_datetime_with_class_timezone.utcoffset()
            ).replace(tzinfo = datetime.timezone.utc, microsecond = 0)
        self.__internal_end_datetime_utc   = (
            self.__internal_end_datetime_with_class_timezone - self.__internal_end_datetime_with_class_timezone.utcoffset()
            ).replace(tzinfo = datetime.timezone.utc, microsecond = 0)
        self.__temp_station_metadata = 0 
        
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
        """
            Calculates solar parameters based on the given method by using pvlib estimation modells.

            Parameters
            ----------
            input_df : pandas.DataFrame
                Input DataFrame containing weather data (temperature, drew_point, pressure, ghi).
            lat : float
                Latitude of the location.
            lon : float
                Longitude of the location.
            height : float
                Altitude or height of the location.
            method : str, optional
                Method for solar parameter calculation (default is 'disc').
                Options: 'disc', 'erbs', 'dirint', 'boland'.
            use_method_name_in_columns : bool, optional
                If True, method name is included in the column names of the output DataFrame (default is False).

            Returns
            -------
            out_df : pandas.DataFrame
                DataFrame with calculated solar parameters.
                Columns include 'dni', 'dhi'.
                The DataFrame has the same index as the input_df.

            Notes
            -----
            - The input_df should contain necessary weather data columns. The Units are :
                index (time)    [datetime utc]
                'ghi'           [W/m2]
                'temperature'   [C]
                'drew_point'    [C]
                'pressure'      [Pa]
            - Solar zenith angles and other solar position parameters are calculated using the get_solarposition function.
            - The method parameter determines the algorithm used for solar parameter calculation.
        """
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
        
        #Add methode to column name of the parameters
        if use_methode_name_in_columns: out_df.columns = [str(col) + '_' + methode for col in out_df.columns]
        
        #Delete values in out_df, when ghi is NaN.
        out_df.where(cond=(np.isnan(df['ghi']) != True), other=None, inplace=True)

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
                Columns include 'ghi' when using mosmix and 'ghi', 'dni', and 'dhi' when using observation query type.
                The DataFrame has the same index as the input df.

            Notes
            -----
            - The input DataFrame (df) has to contain 'ghi' in columns. Additionaly there can be 'dni', and 'dhi' in columns.
            - The Units for all irradiance parameter are:
            [kJ/m^2/resulution] for MOSMIX
            [J/cm^2/resulution] for OBSERVATION

            - The query_type parameter specifies the type of data query, either 'MOSMIX' or 'OBSERVATION'.
            - The calculated solar power is returned in units of [W/m^2].
        """
        
        df_power = pd.DataFrame(index=df.index)
        df_power['ghi'] = 0
        if 'dni' in df.columns:
            df_power['dni'] = 0
        if 'dhi' in df.columns:
            df_power['dhi'] = 0
        
        resulution = (df.index[1]-df.index[0]).seconds
        if query_type == 'MOSMIX':
            for column in df_power.columns:
                df_power[column] = df[column] * 1000 / resulution #kJ/m2 -> J/m2 -> W/m2
        elif query_type == 'OBSERVATION':
            for column in df_power.columns:
                df_power[column] = df[column] * 10e3 / resulution #/J/cm2 -> J/m2 -> W/m2

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
            Calculated station pressure.

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
            pressure_reduced * ( 1 - ( -0.0065  * height) / temperature) ** ((9.81 * 0.02897) / (8.314 * -0.0065))
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
        """
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
        df.interpolate(inplace=True, limit_area='inside')
        #Resample to given resulotion and interpolate over missing values
        df = df.resample(time_freq).mean().interpolate(method = 'linear', limit_area='inside')
        
        if df.index[-1] > self.__end_dt_target_tz:
            df = df[df.index[0]:self.__end_dt_target_tz]
        
        df = df.reindex(sorted(df.columns), axis=1)
        df = round(df,2)
        return df
    
    
    def __get_multi_index_for_windpowerlib (self, columns, height):
        """
       Creates a MultiIndex DataFrame for wind-related parameters.
    
       Parameters
       ----------
       columns : list
           List of column names for the DataFrame.
       height : float
           Height of the station [m].
    
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
        df = pd.DataFrame(columns = columns)
        for act_column in df.columns:
            for key in rename_dict.keys():
                if key == act_column:
                    df[act_column] = (act_column, rename_dict[key])
                    break       
        df.columns = pd.MultiIndex.from_arrays([df.iloc[0], df.iloc[1]], names=['Parameter', 'Height'])
        return df.columns
    
    
    def __process_observation_parameter (self, pd_sorted_data_for_station, pd_station_metadata, dataset):
        """
            Processes observation parameters based on the dataset.

            Parameters
            ----------
            pd_sorted_data_for_station : pandas.DataFrame
                DataFrame containing weather data for a station.
            pd_station_metadata : pandas.DataFrame
                DataFrame containing station metadata.
            dataset : str
                Type of weather dataset, either 'solar', 'air' or 'wind'.

            Returns
            -------
            resampled_data : pandas.DataFrame
                Resampled and processed weather data.

            Notes
            -----
            - If the dataset is 'solar', the function calculates Direct Normal Irradiance (DNI)
            from Global Horizontal Irradiance (GHI) and Diffuse Horizontal Irradiance (DHI).
            It then updates the DataFrame with solar power calculated from energy.
            - If the dataset is 'wind', the function prepares data for Windpowerlib using the
            __get_multi_index_for_windpowerlib method and resamples the data.
            - Because the air parameter does not need to be processed, the function does not change them.
        """
        if dataset == 'solar': 
            pd_sorted_data_for_station['dni'] = pd_sorted_data_for_station.ghi - pd_sorted_data_for_station.dhi
            #Calculate power from irradiance
            pd_sorted_data_for_station.update(self.__get_solar_power_from_energy(pd_sorted_data_for_station,'OBSERVATION'), overwrite=True)
        elif dataset == 'wind':
            pd_sorted_data_for_station.pressure    = pd_sorted_data_for_station.pressure * 100 # hPa to Pa
            pd_sorted_data_for_station.temperature = pd_sorted_data_for_station.temperature + 274.15
            pd_sorted_data_for_station['roughness_length'] = 0.15
            pd_sorted_data_for_station.columns = self.__get_multi_index_for_windpowerlib(
                pd_sorted_data_for_station.columns,
                pd_station_metadata['height'].values[0])
            
        return self.__resample_data(pd_sorted_data_for_station)
        
        
    def __process_mosmix_parameter (self, pd_sorted_data_for_station, dataset, pd_station_metadata, additional_parameter_lst = None):
        """
            Processes MOSMIX parameters based on the dataset.

            Parameters
            ----------
            pd_sorted_data_for_station : pandas.DataFrame
                DataFrame containing weather data for a station.
            dataset : str
                Type of weather dataset, either 'solar', 'air', or 'wind'.
            pd_station_metadata : pandas.DataFrame
                DataFrame containing station metadata.
            additional_parameter_lst : list, optional
                List of additional parameters, which where retrieved for calculating missing parameters such as dhi dni, to drop from the DataFrame, by default None.

            Returns
            -------
            resampled_data : pandas.DataFrame
                Resampled and processed weather data.

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
            pd_sorted_data_for_station.pressure = self.__get_station_pressure_from_reduced_pressure(
                height = pd_station_metadata['height'].values[0], 
                pressure_reduced = pd_sorted_data_for_station.pressure, 
                temperature = pd_sorted_data_for_station.temperature)
            """
            Available methods for solar parameter calculation:
            lst_methodes = ['disc','erbs','dirint','boland']
            """
            lst_methodes = ['disc']
            for methode in lst_methodes:
                calculated_solar_parameter = self.__get_solar_parameter(
                        input_df = pd_sorted_data_for_station, 
                        lat      = pd_station_metadata['latitude' ].values[0], 
                        lon      = pd_station_metadata['longitude'].values[0],
                        height   = pd_station_metadata['height'   ].values[0],
                        methode  = methode,
                        use_methode_name_in_columns = (len(lst_methodes) > 1))
            
            pd_sorted_data_for_station = pd_sorted_data_for_station.merge(right = calculated_solar_parameter, left_index = True, right_index = True)
            pd_sorted_data_for_station.drop(additional_parameter_lst, axis = 1, inplace = True)
        elif dataset == 'air':
            pd_sorted_data_for_station.temperature = pd_sorted_data_for_station.temperature - 273.15  # K to °C
        elif dataset == 'wind':
            pd_sorted_data_for_station.pressure = self.__get_station_pressure_from_reduced_pressure(
                height = pd_station_metadata['height'].values[0], 
                pressure_reduced = pd_sorted_data_for_station.pressure, 
                temperature = pd_sorted_data_for_station.temperature)
            
            pd_sorted_data_for_station['roughness_length'] = 0.15
            pd_sorted_data_for_station.columns = self.__get_multi_index_for_windpowerlib(
                pd_sorted_data_for_station.columns,
                pd_station_metadata['height'].values[0])
            
        #Observation data discribes the value for the last timestep. MOSMIX forecasts the value for the next timestep
        #Shift by -1 to aling MOSMIX to Observation
        pd_sorted_data_for_station = pd_sorted_data_for_station.shift(-1)
        return self.__resample_data(pd_sorted_data_for_station)
    
    
    def __get_dwd_data(
        self, dataset, lat = None, lon = None, user_station_id = None, distance = 30, min_quality_per_parameter = 80, force_end_time = False
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
            force_end_time : Bool, optional
                Flag to surpress the adjustment of the class-end-time if query result is not available for this period, by default False

            Returns
            -------
            processed_data : pandas.DataFrame
                Resampled and processed weather data.
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
            - If a station with valid data is found, the function processes the data based on the dataset and returns the resampled and processed weather data along with station metadata.
         """
        activate_output = not self.surpress_output_globally

        if (lat is None or lon is None) and user_station_id is None:
            raise ValueError("No location or station-ID given!")
            

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
            if self.__end_dt_utc > observation_end_date and not force_end_time:
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
            if self.__start_dt_utc > time_now + datetime.timedelta(hours = 239):
                raise ValueError("No forecast data avaliable for this time")
            if (self.__end_dt_utc > time_now.replace(
                minute = 0 , 
                second = 0, 
                microsecond = 0
                ) + datetime.timedelta(hours = 240)) and not force_end_time:
                self.__end_dt_utc = time_now.replace(
                    minute = 0, 
                    second = 0, 
                    microsecond = 0
                    )+ datetime.timedelta(hours = 240)
                
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
            print('Checking query result for station ' + station_name, station_id + " ...") and activate_output
            
            #Get query result for the actual station
            wd_unsorted_data_for_station = wd_query_result.filter_by_station_id(station_id=station_id).values.all().df

            if isinstance(wd_unsorted_data_for_station,pd.core.frame.DataFrame):
                pd_unsorted_data_for_station = wd_unsorted_data_for_station
            elif isinstance(wd_unsorted_data_for_station,pl.DataFrame):
                pd_unsorted_data_for_station = wd_unsorted_data_for_station.to_pandas()
            else:
                raise Exception("Data type incorrect")
                
            pd_sorted_data_for_station = pd.DataFrame()
            pd_unsorted_data_for_station.set_index('date', inplace=True)

            #Format data to get a df with one column for each parameter
            for key in req_parameter_dict.keys():
                pd_sorted_data_for_station[key] = pd_unsorted_data_for_station.loc[pd_unsorted_data_for_station['parameter'] == req_parameter_dict[key]]['value']

            #Fill missing values with NaN, if end time is forced    
            if pd_sorted_data_for_station.index[-1] < self.__end_dt_utc and force_end_time and isinstance(wd_query_result,DwdMosmixRequest):
                pd_missing_dates = pd.DataFrame(index = pd.date_range(
                    start = pd_sorted_data_for_station.index[-1] + datetime.timedelta(hours = 1),
                    end   = self.__end_dt_utc,
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
        print("Query successful!") and activate_output
        
        if isinstance(wd_query_result,DwdObservationRequest):
           return self.__process_observation_parameter(
                pd_sorted_data_for_station = pd_sorted_data_for_station, 
                pd_station_metadata = pd_nearby_stations.loc[pd_nearby_stations['station_id'] == station_id],
                dataset = dataset
                ),pd_nearby_stations.loc[pd_nearby_stations['station_id'] == station_id]
        if isinstance(wd_query_result,DwdMosmixRequest):
           return self.__process_mosmix_parameter(
                pd_sorted_data_for_station = pd_sorted_data_for_station, 
                dataset = dataset, 
                pd_station_metadata = pd_nearby_stations.loc[pd_nearby_stations['station_id'] == station_id],
                additional_parameter_lst = additional_parameter_lst if 'additional_parameter_lst' in locals() else None
                ),pd_nearby_stations.loc[pd_nearby_stations['station_id'] == station_id]
    
    def get_dwd_pv_data(
        self, lat = None, lon = None, station_id = None, distance = 30, min_quality_per_parameter = 80, force_end_time = False
        ):
        """
        Retrieves solar weather data from the DWD database.

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
        force_end_time : bool, optional
            Flag to suppress the adjustment of the class-end-time if the query result is not available for this period, by default False.

        Returns
        -------
        station_metadata : pandas.DataFrame
            Metadata of the selected weather station.
        Notes
            -----
            - The query result is saved in class variable pv_data  
            - Station metadate is not saved in class      
    """
        self.pv_data, station_metadata  = self.__get_dwd_data(
            dataset = 'solar', 
            lat = lat, 
            lon = lon, 
            user_station_id = station_id,
            distance = distance, 
            min_quality_per_parameter = min_quality_per_parameter,
            force_end_time = force_end_time
            )
        return station_metadata

    def get_dwd_wind_data(
        self, lat = None, lon = None, station_id = None, distance = 30, min_quality_per_parameter = 80, force_end_time = False
        ):
        """
        Retrieves wind weather data from the DWD database.

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
        force_end_time : bool, optional
            Flag to suppress the adjustment of the class-end-time if the query result is not available for this period, by default False.

        Returns
        -------
        station_metadata : pandas.DataFrame
            Metadata of the selected weather station.
        Notes
            -----
            - The query result is saved in class variable wind_data  
            - Station meta data is not saved in class      
        """
        self.wind_data, station_metadata = self.__get_dwd_data(
            dataset = 'wind', 
            lat = lat, 
            lon = lon,
            user_station_id = station_id,
            distance = distance, 
            min_quality_per_parameter = min_quality_per_parameter,
            force_end_time = force_end_time
            )
        return station_metadata

    def get_dwd_temp_data(
        self, lat = None, lon = None, station_id = None, distance = 30, min_quality_per_parameter = 80, force_end_time = False
        ):
        """
        Retrieves temperature weather data from the DWD database.

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
        force_end_time : bool, optional
            Flag to suppress the adjustment of the class-end-time if the query result is not available for this period, by default False.

        Returns
        -------
        station_metadata : pandas.DataFrame
            Metadata of the selected weather station.
        Notes
            -----
            - The query result is saved in class variable temp_data  
            - Station meta data is saved in class variable __temp_station_metadata for usage in get_dwd_mean_temp_hours / get_dwd_mean_temp_days
        """
        self.temp_data, self.__temp_station_metadata = self.__get_dwd_data(
            dataset = 'air', 
            lat = lat, 
            lon = lon,
            user_station_id = station_id,
            distance = distance, 
            min_quality_per_parameter = min_quality_per_parameter,
            force_end_time = force_end_time
            )
        return self.__temp_station_metadata
    
    def get_dwd_mean_temp_hours(
        self, lat = None, lon = None, station_id = None, distance = 30, min_quality_per_parameter = 80, force_end_time = False
        ):
        """
        Resamples temperature data to horly resulution. 
        If there are no temperature data in temp_data, it retrieves temperature weather data from the DWD database.

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
        force_end_time : bool, optional
            Flag to suppress the adjustment of the class-end-time if the query result is not available for this period, by default False.

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
                min_quality_per_parameter = min_quality_per_parameter,
                force_end_time = force_end_time
                )
        self.mean_temp_hours = self.__resample_data(self.temp_data,'60 min')
        return self.__temp_station_metadata
    
    def get_dwd_mean_temp_days(
        self, lat = None, lon = None, station_id = None, distance = 30, min_quality_per_parameter = 80, force_end_time = False
        ):
        """
        Resamples temperature data to daily resulution. 
        If there are no temperature data in temp_data, it retrieves temperature weather data from the DWD database.

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
        force_end_time : bool, optional
            Flag to suppress the adjustment of the class-end-time if the query result is not available for this period, by default False.

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
                min_quality_per_parameter = min_quality_per_parameter,
                force_end_time = force_end_time
                )
        self.mean_temp_days = self.__resample_data(self.temp_data,'1440 min')
        return self.__temp_station_metadataN
        




