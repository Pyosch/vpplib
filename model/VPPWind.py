"""
Info
----
This file contains the basic functionalities of the VPPWind class.

"""

from .VPPComponent import VPPComponent

import pandas as pd
import traceback

# windpowerlib imports
from windpowerlib import ModelChain
from windpowerlib import WindTurbine

class VPPWind(VPPComponent):

    # The constructor takes an identifier (String) for referencing the current
    # photovoltaic power plant. The parameter peak power (Float) determines the maximum
    # power that the photovoltaic power plant can generate.
    def __init__(self, timebase = 1, identifier = None, 
                 environment = None, userProfile = None,
                 start = None, end = None, timezone = 'Europe/Berlin',
                 weather_filename = None,
                 turbine_type = 'E-126/4200', hub_height = 135,
                 rotor_diameter = 127, fetch_curve = 'power_curve',
                 data_source = 'oedb',
                 wind_speed_model = 'logarithmic', density_model = 'barometric',
                 temperature_model = 'linear_gradient', 
                 power_output_model = 'power_curve', density_correction = False,
                 obstacle_height = 0, hellman_exp = None
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

        # Call to super class
        super(VPPWind, self).__init__(timebase, environment, userProfile)
    
    
        # Configure attributes
        self.identifier = identifier
        self.start = start
        self.end = end
        self.timezone = timezone
    
        self.limit = 1.0
        
        #WindTurbine data
        self.turbine_type = turbine_type  # turbine type as in register #
        self.hub_height = hub_height  # in m
        self.rotor_diameter = rotor_diameter  # in m
        self.fetch_curve = fetch_curve  # fetch power curve #
        self.data_source = data_source  # data source oedb or name of csv file
        self.WindTurbine = None
        
        #ModelChain data
        self.wind_speed_model = wind_speed_model  # 'logarithmic' (default),
                                                # 'hellman' or
                                                # 'interpolation_extrapolation'
        self.density_model = density_model  # 'barometric' (default), 'ideal_gas' or
                                           # 'interpolation_extrapolation'
        self.temperature_model = temperature_model  # 'linear_gradient' (def.) or
                                                     # 'interpolation_extrapolation'
        self.power_output_model = power_output_model  # 'power_curve' (default) or
                                                  # 'power_coefficient_curve'
        self.density_correction = density_correction  # False (default) or True
        self.obstacle_height = obstacle_height  # default: 0
        self.hellman_exp = hellman_exp # None (default)
        self.ModelChain = None
        
        self.timeseries = None
        
    

    def get_weather_data(self, weather_filename, **kwargs):
        r"""
        Imports weather data from a file.
    
        The data include wind speed at two different heights in m/s, air
        temperature in two different heights in K, surface roughness length in m
        and air pressure in Pa. The file is located in the example folder of the
        windpowerlib. The height in m for which the data applies is specified in
        the second row.
    
        Parameters
        ----------
        filename : string
            Filename of the weather data file. Default: 'weather.csv'.
    
        Other Parameters
        ----------------
        datapath : string, optional
            Path where the weather data file is stored.
            Default: 'windpowerlib/example'.
    
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
            weather_filename, index_col=0, header=[0, 1],
            date_parser=lambda idx: pd.to_datetime(idx, utc=True))
        # change type of index to datetime and set time zone
        weather_df.index = pd.to_datetime(weather_df.index).tz_convert(
                self.timezone)
        # change type of height from str to int by resetting columns
        l0 = [_[0] for _ in weather_df.columns]
        l1 = [int(_[1]) for _ in weather_df.columns]
        weather_df.columns = [l0, l1]
        
        return weather_df
    
    
    def get_wind_turbine(self):
        r"""
        fetch power and/or power coefficient curve data from the OpenEnergy 
        Database (oedb)
        Execute ``windpowerlib.wind_turbine.get_turbine_types()`` to get a table
        including all wind turbines for which power and/or power coefficient curves
        are provided.
    
        Returns
        -------
        WindTurbine
    
        """
    
        # specification of wind turbine where power curve is provided in the oedb
        # if you want to use the power coefficient curve change the value of
        # 'fetch_curve' to 'power_coefficient_curve'
        wind_turbine = {
            'name': self.turbine_type, # turbine type as in register #
            'hub_height': self.hub_height, # in m
            'rotor_diameter': self.rotor_diameter, # in m
            'fetch_curve': self.fetch_curve,  # fetch power curve #
            'data_source': self.data_source  # data source oedb or name of csv file
        }
        # initialize WindTurbine object
        self.wind_turbine = WindTurbine(**wind_turbine)
    
        return self.wind_turbine
    
    
    def calculate_power_output(self, weather):
        r"""
        Calculates power output of wind turbines using the
        :class:`~.modelchain.ModelChain`.
    
        The :class:`~.modelchain.ModelChain` is a class that provides all necessary
        steps to calculate the power output of a wind turbine. You can either use
        the default methods for the calculation steps, or choose different methods, 
        as done for the 'e126'. Of course, you can also use the default methods 
        while only changing one or two of them.
    
        Parameters
        ----------
        weather : pd.DataFrame
            Contains weather data time series.
        e126 : WindTurbine
            WindTurbine object with power curve from the OpenEnergy Database.
    
        """
        # power output calculation for e126
        # own specifications for ModelChain setup
        modelchain_data = {
            'wind_speed_model': self.wind_speed_model,  # 'logarithmic' (default),
                                                # 'hellman' or
                                                # 'interpolation_extrapolation'
            'density_model': self.density_model,  # 'barometric' (default), 'ideal_gas' or
                                           # 'interpolation_extrapolation'
            'temperature_model': self.temperature_model,  # 'linear_gradient' (def.) or
                                                     # 'interpolation_extrapolation'
            'power_output_model': self.power_output_model,  # 'power_curve' (default) or
                                                  # 'power_coefficient_curve'
            'density_correction': self.density_correction,  # False (default) or True
            'obstacle_height': self.obstacle_height,  # default: 0
            'hellman_exp': self.hellman_exp}  # None (default) or None
        
        # initialize ModelChain with own specifications and use run_model method
        # to calculate power output
        if self.start ==None or self.end == None:
            self.ModelChain = ModelChain(self.wind_turbine, **modelchain_data).run_model(weather)
            
        else:
            self.ModelChain = ModelChain(self.wind_turbine, **modelchain_data).run_model(weather[self.start:self.end])
            
        # write power output time series to VPPWind object
        self.timeseries = self.ModelChain.power_output /1000 #convert to kW
    
        return


    def prepareTimeSeries(self, weather_filename):
    
        # -> Functions stub <-
        weather = self.get_weather_data(weather_filename)
        self.get_wind_turbine()
        self.calculate_power_output(weather)
        
        return self.timeseries


    # ===================================================================================
    # Controlling functions
    # ===================================================================================

    # This function limits the power of the photovoltaic to the given percentage.
    # It cuts the current power production down to the peak power multiplied by
    # the limit (Float [0;1]).
    def limitPowerTo(self, limit):

        # Validate input parameter
        if limit >= 0 and limit <= 1:

            # Parameter is valid
            self.limit = limit

        else:
            traceback.print_exc("Paramter is invalid")
        
            return
        

    # ===================================================================================
    # Balancing Functions
    # ===================================================================================

    # Override balancing function from super class.
    def valueForTimestamp(self, timestamp):
        
        if type(timestamp) == int:
            
            return self.timeseries.iloc[timestamp].item() * self.limit
        
        elif type(timestamp) == str:
            
            return self.timeseries.loc[timestamp].item() * self.limit
        
        else:
            traceback.print_exc("timestamp needs to be of type int or string. Stringformat: YYYY-MM-DD hh:mm:ss")
            

    def observationsForTimestamp(self, timestamp):
        
        """
        Info
        ----
        This function takes a timestamp as the parameter and returns a 
        dictionary with key (String) value (Any) pairs. 
        Depending on the type of component, different status parameters of the 
        respective component can be queried.
        
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
        if type(timestamp) == int:
            
            wind_generation= self.timeseries.iloc[timestamp]
        
        elif type(timestamp) == str:
            
            wind_generation= self.timeseries.loc[timestamp]
        
        else:
            traceback.print_exc("timestamp needs to be of type int or string. Stringformat: YYYY-MM-DD hh:mm:ss")
        
        
        observations = {'wind_generation':wind_generation}
        
        return observations