# -*- coding: utf-8 -*-
"""
Info
----
This file contains the basic functionalities of the WindPower class.

"""

from .component import Component


# windpowerlib imports
from windpowerlib import ModelChain
from windpowerlib import WindTurbine


class WindPower(Component):
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
        user_profile=None,
        cost=None,
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
        super(WindPower, self).__init__(unit, environment, user_profile, cost)

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
        if self.environment.start == None or self.environment.end == None:
            self.ModelChain = ModelChain(
                self.wind_turbine, **modelchain_data
            ).run_model(self.environment.wind_data)

        else:
            self.ModelChain = ModelChain(
                self.wind_turbine, **modelchain_data
            ).run_model(
                self.environment.wind_data[
                    self.environment.start : self.environment.end
                ]
            )

        # write power output time series to WindPower.timeseries
        self.timeseries = self.ModelChain.power_output / 1000  # convert to kW

        return

    def prepare_time_series(self):

        if len(self.environment.wind_data) == 0:
            raise ValueError("self.environment.wind_data is empty.")

        self.get_wind_turbine()
        self.calculate_power_output()

        return self.timeseries

    def reset_time_series(self):

        self.timeseries = None

        return self.timeseries

    # ===================================================================================
    # Controlling functions
    # ===================================================================================

    # This function limits the power to the given percentage.
    # It cuts the current power production down to the peak power multiplied by
    # the limit (Float [0;1]).
    def limit_power_to(self, limit):

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

    # Override balancing function from super class.
    def value_for_timestamp(self, timestamp):

        if type(timestamp) == int:

            return self.timeseries.iloc[timestamp].item() * self.limit

        elif type(timestamp) == str:

            return self.timeseries.loc[timestamp].item() * self.limit

        else:
            raise ValueError(
                "timestamp needs to be of type int or string. Stringformat: YYYY-MM-DD hh:mm:ss"
            )

    def observations_for_timestamp(self, timestamp):

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

            wind_generation = self.timeseries.iloc[timestamp]

        elif type(timestamp) == str:

            wind_generation = self.timeseries.loc[timestamp]

        else:
            raise ValueError(
                "timestamp needs to be of type int or string. "
                + "Stringformat: YYYY-MM-DD hh:mm:ss"
            )

        observations = {"wind_generation": wind_generation}

        return observations
