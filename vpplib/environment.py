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
import polars as pl
import  datetime
from wetterdienst.provider.dwd.observation import (
    DwdObservationPeriod,
    DwdObservationRequest,
    DwdObservationResolution
)

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
    
    def __get_dwd_data(
        self, parameter, lat, lon, distance,target_timezone=datetime.timezone.utc, min_quality_per_dataset=99, resample_to = '15min'
        ):

        start_datetime = datetime.datetime.strptime(self.start, '%Y-%m-%d %H:%M:%S').replace(tzinfo=target_timezone)
        end_datetime   = datetime.datetime.strptime(self.end  , '%Y-%m-%d %H:%M:%S').replace(tzinfo=target_timezone)
        req_parameter = list(parameter.keys())

        #Get station data for your location
        station_result = DwdObservationRequest(
            parameter  = req_parameter,
            resolution = DwdObservationResolution.MINUTE_10,
            period     = DwdObservationPeriod.RECENT,
            start_date = start_datetime,
            end_date   = end_datetime + datetime.timedelta(minutes = 10),
        ).filter_by_distance(latlon = (lat, lon), distance = distance)

        if(isinstance(station_result.df,pd.core.frame.DataFrame)):
            empty = station_result.df.empty
            if not empty:
                pd_station_result = station_result.df
        elif(isinstance(station_result.df,pl.DataFrame)):
            empty = station_result.df.is_empty()
            if not empty:
                pd_station_result = station_result.df.to_pandas()
        else:
            empty = True

        if (empty):
            print("No station found!")
            return

        #Get weather data
        values = (
            DwdObservationRequest(
                parameter  = req_parameter,
                resolution = DwdObservationResolution.MINUTE_10,
                start_date = start_datetime,
                end_date   = end_datetime + datetime.timedelta(minutes = 10),
            )
        )
        
        valid_station_data = False
        #Check query result for the stations within defined distance
        for station_id in pd_station_result["station_id"].values:
            name  = pd_station_result.loc[pd_station_result['station_id'] == station_id]['name'].values[0]
            print('Checking query result for station '+ name, station_id +" ...")
            
            #Get query result for the actual station
            values_for_station = values.filter_by_station_id(station_id=station_id).values.all().df

            if(isinstance(values_for_station,pd.core.frame.DataFrame)):
                pd_values_for_station = values_for_station
            elif(isinstance(values_for_station,pl.DataFrame)):
                pd_values_for_station = values_for_station.to_pandas()
            else:
                print("Data type incorrect")
                return
                
            dwd_result_processed        = pd.DataFrame()
            pd_values_for_station.index = pd_values_for_station.date

            #Format data to get a df with one column for each parameter
            for key in parameter.keys():
                dwd_result_processed[key] = pd_values_for_station.loc[pd_values_for_station['parameter'] == key]['value']
                
            quality                         = pd.DataFrame()
            quality.index                   = [True,False,'quality']
            quality[list(parameter.keys())] = ""
        
            #Counting the amound of valid and invalid data per parameter
            for column in dwd_result_processed.columns:
                count           = dwd_result_processed.isna()[column].value_counts()
                quality[column] = count
                quality         = quality.fillna(0)
            
            #Calculate the percentage of valid data per parameter query    
            quality.loc['quality'] = round((quality.loc[0]/(quality.loc[0]+quality.loc[1]))*100,1)
            print("Quality of the data set:",quality.loc['quality'].values)
            
            #If quality is good enough
            if quality.loc['quality'].min() >= min_quality_per_dataset:
                distance            = str(round(pd_station_result.loc[pd_station_result['station_id'] == station_id]['distance'].values[0]))
                valid_station_data  = True
                print("Query result valid!")
                print("Station " + station_id + " " + name +" used")
                print("Distance to location: " + distance + " km")
                break
        if not valid_station_data:
            print("No station found")
            return

        print("Query successful!")
        
        dwd_result_processed.rename(columns=parameter, inplace=True)

        #Missing data is marked with -999. Replace by NaN
        dwd_result_processed.where(cond=(dwd_result_processed[parameter.values()] != -999), other=None, inplace=True)
        dwd_result_processed.interpolate(inplace=True)
    
        #Calculate dni if df contains PV data
        if 'ghi' in dwd_result_processed.columns and 'dhi' in dwd_result_processed.columns:
            dwd_result_processed['dni'] = dwd_result_processed.ghi - dwd_result_processed.dhi
        
        dwd_result_processed = dwd_result_processed.resample(self.time_freq).mean()
        dwd_result_processed = dwd_result_processed[start_datetime:end_datetime]
        dwd_result_processed.index.rename("time", inplace=True)
        #dwd_result_processed.plot(figsize=(10, 6))
        return dwd_result_processed
    
    def get_dwd_pv_data(self,lat,lon,distance = 30):
        parameter = {"radiation_global": "ghi", "radiation_sky_short_wave_diffuse": "dhi"}
        self.pv_data = self.__get_dwd_data(parameter, lat, lon, distance) 
    
    def get_dwd_wind_data(self,lat,lon,distance = 30):
        parameter = {"wind_speed": "wind_speed"}
        self.wind_data = self.__get_dwd_data(parameter, lat, lon, distance)   

    def get_dwd_temp_data(self,lat,lon,distance = 30):
        parameter = {"pressure_air_site": "pressure", "temperature_air_mean_200": "temperature"}
        self.mean_temp_hours = self.__get_dwd_data(parameter, lat, lon, distance, resample_to = '1h')



        

    

