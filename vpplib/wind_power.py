# -*- coding: utf-8 -*-
"""
Wind Power Module
---------------
This module contains the WindPower class which models a wind turbine component
in a virtual power plant environment.

The WindPower class uses the windpowerlib package to calculate power output
based on wind speed data and turbine specifications. It supports various models
for wind speed, air density, temperature, and power output calculations.
"""

from .component import Component
import pandas as pd
import datetime

# windpowerlib imports
from windpowerlib import ModelChain
from windpowerlib import WindTurbine


class WindPower(Component):
    """
    A class representing a wind power component in a virtual power plant.
    
    The WindPower class models a wind turbine and calculates its power output
    based on wind speed data and turbine specifications. It uses the windpowerlib
    package to perform the calculations and supports various models for wind speed,
    air density, temperature, and power output calculations.
    
    Attributes
    ----------
    identifier : str, optional
        Unique identifier for the wind power component
    limit : float
        Power limit factor between 0 and 1 (default: 1.0)
    turbine_type : str
        Type of wind turbine as specified in the windpowerlib turbine database
    hub_height : float
        Height of the turbine hub in meters
    rotor_diameter : float
        Diameter of the rotor in meters
    fetch_curve : str
        Type of curve to fetch ('power_curve' or 'power_coefficient_curve')
    data_source : str
        Data source for turbine data ('oedb' or name of CSV file)
    wind_speed_model : str
        Model for wind speed calculation ('logarithmic', 'hellman', or 'interpolation_extrapolation')
    density_model : str
        Model for air density calculation ('barometric', 'ideal_gas', or 'interpolation_extrapolation')
    temperature_model : str
        Model for temperature calculation ('linear_gradient' or 'interpolation_extrapolation')
    power_output_model : str
        Model for power output calculation ('power_curve' or 'power_coefficient_curve')
    density_correction : bool
        Whether to apply density correction
    obstacle_height : float
        Height of obstacles affecting wind flow in meters
    hellman_exp : float or None
        Hellman exponent for wind speed calculation
    wind_turbine : WindTurbine
        WindTurbine object from windpowerlib
    ModelChain : ModelChain
        ModelChain object from windpowerlib
    timeseries : pandas.Series
        Time series of power output in kW
    """
    
    def __init__(
        self,
        turbine_type,
        hub_height,
        rotor_diameter,
        fetch_curve,
        data_source,
        wind_speed_model,
        density_model,
        temperature_model,
        power_output_model,
        density_correction,
        obstacle_height,
        hellman_exp,
        unit,
        identifier=None,
        environment=None,
    ):
        """
        Initialize a WindPower object.
        
        Parameters
        ----------
        turbine_type : str
            Type of wind turbine as specified in the windpowerlib turbine database
        hub_height : float
            Height of the turbine hub in meters
        rotor_diameter : float
            Diameter of the rotor in meters
        fetch_curve : str
            Type of curve to fetch ('power_curve' or 'power_coefficient_curve')
        data_source : str
            Data source for turbine data ('oedb' or name of CSV file)
        wind_speed_model : str
            Model for wind speed calculation ('logarithmic', 'hellman', or 'interpolation_extrapolation')
        density_model : str
            Model for air density calculation ('barometric', 'ideal_gas', or 'interpolation_extrapolation')
        temperature_model : str
            Model for temperature calculation ('linear_gradient' or 'interpolation_extrapolation')
        power_output_model : str
            Model for power output calculation ('power_curve' or 'power_coefficient_curve')
        density_correction : bool
            Whether to apply density correction
        obstacle_height : float
            Height of obstacles affecting wind flow in meters
        hellman_exp : float or None
            Hellman exponent for wind speed calculation
        unit : str
            Unit of power measurement (e.g., 'kW')
        identifier : str, optional
            Unique identifier for the wind power component
        environment : Environment, optional
            Environment object containing weather data and simulation parameters
            
        Notes
        -----
        The wind power calculation requires wind speed data in the environment object.
        The data should be provided in the environment.wind_data attribute.
        """

        # Call to super class
        super(WindPower, self).__init__(unit, environment)

        # Configure attributes
        self.identifier = identifier
        self.limit = 1.0

        # WindTurbine data
        self.turbine_type = turbine_type  # turbine type as in register
        self.hub_height = hub_height  # in m
        self.rotor_diameter = rotor_diameter  # in m
        self.fetch_curve = fetch_curve  # fetch power curve #
        self.data_source = data_source  # data source oedb or name of csv file
        self.WindTurbine = None

        # ModelChain data
        self.wind_speed_model = wind_speed_model  # 'logarithmic' (default),
        # 'hellman' or
        # 'interpolation_extrapolation'
        self.density_model = (
            density_model
        )  # 'barometric' (default), 'ideal_gas' or
        # 'interpolation_extrapolation'
        self.temperature_model = (
            temperature_model
        )  # 'linear_gradient' (def.) or
        # 'interpolation_extrapolation'
        self.power_output_model = (
            power_output_model
        )  # 'power_curve' (default) or
        # 'power_coefficient_curve'
        self.density_correction = density_correction  # False (default) or True
        self.obstacle_height = obstacle_height  # default: 0
        self.hellman_exp = hellman_exp  # None (default)
        self.ModelChain = None

        self.timeseries = None

    def get_wind_turbine(self):
        """
        Create a WindTurbine object with the specified parameters.
        
        This method initializes a WindTurbine object from the windpowerlib package
        using the turbine specifications provided during initialization. The turbine
        data (power curve or power coefficient curve) is fetched from the specified
        data source, which can be the OpenEnergy Database (oedb) or a CSV file.
        
        Returns
        -------
        WindTurbine
            A WindTurbine object from the windpowerlib package
            
        Notes
        -----
        To see available turbine types, execute:
        ``windpowerlib.wind_turbine.get_turbine_types()``
        
        This will return a table including all wind turbines for which power and/or
        power coefficient curves are provided in the OpenEnergy Database.
        
        The 'fetch_curve' parameter determines whether to fetch the power curve
        ('power_curve') or the power coefficient curve ('power_coefficient_curve').
        """

        # specification of wind turbine where power curve is provided in the oedb
        # if you want to use the power coefficient curve change the value of
        # 'fetch_curve' to 'power_coefficient_curve'
        wind_turbine = {
            "turbine_type": self.turbine_type,  # turbine type as in register
            "hub_height": self.hub_height,  # in m
            "rotor_diameter": self.rotor_diameter,  # in m
            "fetch_curve": self.fetch_curve,  # fetch power curve
            "data_source": self.data_source,  # data source oedb or name of csv file
        }
        # initialize WindTurbine object
        self.wind_turbine = WindTurbine(**wind_turbine)

        return self.wind_turbine

    def calculate_power_output(self):
        """
        Calculate the power output of the wind turbine using ModelChain.
        
        This method creates a ModelChain object from the windpowerlib package
        and uses it to calculate the power output of the wind turbine based on
        the wind data provided in the environment. The calculation uses the
        models specified during initialization for wind speed, air density,
        temperature, and power output.
        
        The resulting power output time series is stored in the timeseries attribute
        after conversion from W to kW.
        
        Returns
        -------
        None
            The method updates the timeseries attribute but does not return a value
            
        Notes
        -----
        The ModelChain class from windpowerlib provides all necessary steps to
        calculate the power output of a wind turbine. You can use the default methods
        for the calculation steps or choose different methods as specified in the
        initialization parameters.
        
        The wind data is filtered to the specified time period if start and end
        timestamps are provided in the environment.
        """
        # power output calculation for e126
        # own specifications for ModelChain setup
        modelchain_data = {
            "wind_speed_model": self.wind_speed_model,  # 'logarithmic' (default),
            # 'hellman' or
            # 'interpolation_extrapolation'
            "density_model": self.density_model,  # 'barometric' (default), 'ideal_gas' or
            # 'interpolation_extrapolation'
            "temperature_model": self.temperature_model,  # 'linear_gradient' (def.) or
            # 'interpolation_extrapolation'
            "power_output_model": self.power_output_model,  # 'power_curve' (default) or
            # 'power_coefficient_curve'
            "density_correction": self.density_correction,  # False (default) or True
            "obstacle_height": self.obstacle_height,  # default: 0
            "hellman_exp": self.hellman_exp,
        }  # None (default) or None

        # initialize ModelChain with own specifications and use run_model method
        # to calculate power output
        
        # Ensure wind_data has the correct MultiIndex format
        wind_data = self.environment.wind_data.copy()
        
        # Make sure the MultiIndex has the correct names
        if isinstance(wind_data.columns, pd.MultiIndex):
            # Set the names if they're not already set
            if wind_data.columns.names != ['variable', 'height']:
                wind_data.columns.names = ['variable', 'height']
            
            # Create a new DataFrame with the correct MultiIndex format
            # This is a workaround for the windpowerlib issue
            try:
                # Extract the data
                wind_speed = wind_data[('wind_speed', 10)] if ('wind_speed', 10) in wind_data.columns else wind_data.iloc[:, 0]
                temperature = wind_data[('temperature', 2)] if ('temperature', 2) in wind_data.columns else wind_data.iloc[:, 2]
                pressure = wind_data[('pressure', 0)] if ('pressure', 0) in wind_data.columns else wind_data.iloc[:, 1]
                roughness_length = wind_data[('roughness_length', 0)] if ('roughness_length', 0) in wind_data.columns else pd.Series(0.15, index=wind_data.index)
                
                # Create a new DataFrame with the correct MultiIndex
                tuples = [
                    ('wind_speed', 10),
                    ('temperature', 2),
                    ('pressure', 0),
                    ('roughness_length', 0)
                ]
                
                # Create MultiIndex with explicit names
                columns = pd.MultiIndex.from_tuples(tuples, names=['variable', 'height'])
                
                # Create the DataFrame with MultiIndex columns
                new_wind_data = pd.DataFrame(index=wind_data.index)
                new_wind_data[('wind_speed', 10)] = wind_speed
                new_wind_data[('temperature', 2)] = temperature
                new_wind_data[('pressure', 0)] = pressure
                new_wind_data[('roughness_length', 0)] = roughness_length
                
                # Set the MultiIndex columns with names
                new_wind_data.columns = columns
                
                # Use the new DataFrame
                wind_data = new_wind_data
                
                print("Successfully converted wind data to proper MultiIndex format")
            except Exception as e:
                print(f"Error converting wind data to MultiIndex format: {e}")
        else:
            try:
                # Create a simple DataFrame with the data
                weather = pd.DataFrame(index=wind_data.index)
                weather['wind_speed'] = wind_data['wind_speed'] if 'wind_speed' in wind_data.columns else 0
                weather['temperature'] = wind_data['temperature'] if 'temperature' in wind_data.columns else 0
                weather['pressure'] = wind_data['pressure'] if 'pressure' in wind_data.columns else 0
                weather['roughness_length'] = wind_data['roughness_length'] if 'roughness_length' in wind_data.columns else 0.15
                
                # Create tuples for MultiIndex
                tuples = [
                    ('wind_speed', 10),
                    ('temperature', 2),
                    ('pressure', 0),
                    ('roughness_length', 0)
                ]
                
                # Create MultiIndex with explicit names
                columns = pd.MultiIndex.from_tuples(tuples, names=['variable', 'height'])
                
                # Create the DataFrame with MultiIndex columns
                wind_data = pd.DataFrame(index=weather.index)
                wind_data[('wind_speed', 10)] = weather['wind_speed']
                wind_data[('temperature', 2)] = weather['temperature']
                wind_data[('pressure', 0)] = weather['pressure']
                wind_data[('roughness_length', 0)] = weather['roughness_length']
                
                # Set the MultiIndex columns with names
                wind_data.columns = columns
                
                print("Successfully created MultiIndex DataFrame from regular DataFrame")
            except Exception as e:
                print(f"Error converting wind data to MultiIndex format: {e}")
        
        if self.environment.start == None or self.environment.end == None:
            self.ModelChain = ModelChain(
                self.wind_turbine, **modelchain_data
            ).run_model(wind_data)

        else:
            self.ModelChain = ModelChain(
                self.wind_turbine, **modelchain_data
            ).run_model(
                wind_data[
                    self.environment.start : self.environment.end
                ]
            )

        # write power output time series to WindPower.timeseries
        self.timeseries = self.ModelChain.power_output / 1000  # convert to kW

        return

    def prepare_time_series(self):
        """
        Prepare the time series data for the wind power component.
        
        This method initializes the wind turbine and calculates its power output
        for the simulation period. It checks if wind data is available in the
        environment and raises an error if it's not.
        
        Returns
        -------
        pandas.Series
            Time series of power output in kW
            
        Raises
        ------
        ValueError
            If the environment.wind_data is empty
        """
        if len(self.environment.wind_data) == 0:
            raise ValueError("self.environment.wind_data is empty.")

        self.get_wind_turbine()
        self.calculate_power_output()

        return self.timeseries

    def reset_time_series(self):
        """
        Reset the time series data to its initial state.
        
        This method clears the power output time series by setting it to None.
        It can be used to reset the component before recalculating the power output.
        
        Returns
        -------
        None
            The method returns None to indicate that the timeseries has been reset
        """
        self.timeseries = None

        return self.timeseries

    # ===================================================================================
    # Controlling functions
    # ===================================================================================

    def limit_power_to(self, limit):
        """
        Limit the power output of the wind turbine.
        
        This method sets a limit on the power output of the wind turbine as a
        fraction of its calculated output. The limit is a float between 0 and 1,
        where 0 means no power output and 1 means full power output.
        
        Parameters
        ----------
        limit : float
            Power limit factor between 0 and 1
            
        Raises
        ------
        ValueError
            If the limit is not between 0 and 1
            
        Notes
        -----
        This method can be used to simulate curtailment of wind power output,
        for example, due to grid constraints or market conditions.
        """
        # Validate input parameter
        if limit >= 0 and limit <= 1:
            # Parameter is valid
            self.limit = limit
        else:
            # Parameter is invalid
            raise ValueError("Limit-parameter is not valid")

    # ===================================================================================
    # Balancing Functions
    # ===================================================================================

    def value_for_timestamp(self, timestamp):
        """
        Get the power output value for a specific timestamp.
        
        This method returns the power output of the wind turbine at the specified
        timestamp, adjusted by the power limit factor. It overrides the method
        from the Component superclass.
        
        Parameters
        ----------
        timestamp : int or str
            If int: index position in the timeseries
            If str: timestamp in format 'YYYY-MM-DD hh:mm:ss'
            
        Returns
        -------
        float
            Power output in kW at the specified timestamp, adjusted by the limit factor
            
        Raises
        ------
        ValueError
            If the timestamp is not of type int or str
            
        Notes
        -----
        In the context of a virtual power plant, this method returns a negative value
        as wind power is considered generation (not consumption).
        """
        if type(timestamp) == int:
            return self.timeseries.iloc[timestamp].item() * self.limit
        elif type(timestamp) == str:
            return self.timeseries.loc[timestamp].item() * self.limit
        elif isinstance(timestamp, pd.Timestamp) or isinstance(timestamp, datetime.datetime):
            # Convert to string format that matches the index
            timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            try:
                return self.timeseries.loc[timestamp_str].item() * self.limit
            except KeyError:
                # If the exact timestamp is not found, find the closest one
                if len(self.timeseries) > 0:
                    closest_timestamp = self.timeseries.index[0]
                    min_diff = abs((timestamp - pd.to_datetime(closest_timestamp)).total_seconds())
                    for ts in self.timeseries.index:
                        diff = abs((timestamp - pd.to_datetime(ts)).total_seconds())
                        if diff < min_diff:
                            min_diff = diff
                            closest_timestamp = ts
                    return self.timeseries.loc[closest_timestamp].item() * self.limit
                else:
                    raise ValueError("No data available in timeseries")
        else:
            raise ValueError(
                "timestamp needs to be of type int, string, or datetime. Stringformat: YYYY-MM-DD hh:mm:ss"
            )

    def observations_for_timestamp(self, timestamp):
        """
        Get detailed observations for a specific timestamp.
        
        This method returns a dictionary containing the wind power generation
        at the specified timestamp. It can be used to query the status of the
        wind power component at a particular point in time.
        
        Parameters
        ----------
        timestamp : int or str
            If int: index position in the timeseries
            If str: timestamp in format 'YYYY-MM-DD hh:mm:ss'
            
        Returns
        -------
        dict
            Dictionary with key 'wind_generation' and the corresponding power output value
            
        Raises
        ------
        ValueError
            If the timestamp is not of type int or str
            
        Notes
        -----
        This method can be extended to include additional observations such as
        wind speed, air density, or other relevant parameters if they are available
        in the ModelChain results.
        """
        if type(timestamp) == int:
            wind_generation = self.timeseries.iloc[timestamp]
        elif type(timestamp) == str:
            wind_generation = self.timeseries.loc[timestamp]
        elif isinstance(timestamp, pd.Timestamp) or isinstance(timestamp, datetime.datetime):
            # Convert to string format that matches the index
            timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            try:
                wind_generation = self.timeseries.loc[timestamp_str]
            except KeyError:
                # If the exact timestamp is not found, find the closest one
                if len(self.timeseries) > 0:
                    closest_timestamp = self.timeseries.index[0]
                    min_diff = abs((timestamp - pd.to_datetime(closest_timestamp)).total_seconds())
                    for ts in self.timeseries.index:
                        diff = abs((timestamp - pd.to_datetime(ts)).total_seconds())
                        if diff < min_diff:
                            min_diff = diff
                            closest_timestamp = ts
                    wind_generation = self.timeseries.loc[closest_timestamp]
                else:
                    raise ValueError("No data available in timeseries")
        else:
            raise ValueError(
                "timestamp needs to be of type int, string, or datetime. "
                + "Stringformat: YYYY-MM-DD hh:mm:ss"
            )

        observations = {"wind_generation": wind_generation}

        return observations
