"""
Info
----
This file contains the basic functionalities of the VPPEnvironment class.
The object "VPPEnvironment" defines external influences on the system to be simulated. 
In addition to weather and location, this also includes regulatory influences.

TODO: Add regulatory influences e. g. photovoltaik maximum power at the grid connection point

"""

import pandas as pd

class VPPEnvironment(object):

    def __init__(self, timebase=None, timezone='Europe/Berlin' ,
                 start=None, end=None, year=None,
                 time_freq="15 min",
                 mean_temp_days=[], 
                 mean_temp_hours=[], 
                 irradiation_data=[], 
                 wind_data=[]):
        
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
        self.irradiation_data = irradiation_data
        self.wind_data = wind_data
        
    def get_irradiation_data(self, file = "./Input_House/PV/2017_irradiation_15min.csv"):
        
        self.irradiation_data = pd.read_csv(file, index_col="index")
        
        return self.irradiation_data
    
    def get_mean_temp_days(self, file = "./Input_House/heatpump_model/mean_temp_days_2017.csv"):
        
        self.mean_temp_days = pd.DataFrame(pd.date_range(self.year, periods=365, freq = "D", name="time"))
        self.mean_temp_days['Mean_Temp'] = pd.read_csv(
                file, header = None)
        
        return self.mean_temp_days
    
    def get_mean_temp_hours(self):
        
        self.mean_temp_hours = pd.read_csv(
            './Input_House/heatpump_model/mean_temp_hours_2017_indexed.csv', index_col="time")
        
    def get_wind_filename(self, file = "./Input_House/Wind/weather.csv"):
        
        self.wind_filename = file
        
        

    def get_wind_data(self, file = "./Input_House/Wind/weather.csv"): #, **kwargs
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
            Filename of the weather data file. Default: 'weather.csv'.
    
    
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
        
        # read csv file
        weather_df = pd.read_csv(
            file, index_col=0, header=[0, 1],
            date_parser=lambda idx: pd.to_datetime(idx, utc=True))
        # change type of index to datetime and set time zone
        weather_df.index = pd.to_datetime(weather_df.index).tz_convert(
                self.timezone)
        # change type of height from str to int by resetting columns
        l0 = [_[0] for _ in weather_df.columns]
        l1 = [int(_[1]) for _ in weather_df.columns]
        weather_df.columns = [l0, l1]
        
        self.wind_data = weather_df
        
        return weather_df
        
