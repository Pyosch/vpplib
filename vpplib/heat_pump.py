# -*- coding: utf-8 -*-
"""
Info
----
This file contains the basic functionalities of the HeatPump class.

"""

import pandas as pd
from .component import Component


class HeatPump(Component):
    def __init__(
        self,
        thermal_energy_demand,
        heat_pump_type,
        heat_sys_temp,
        el_power,
        th_power,
        ramp_up_time,
        ramp_down_time,
        min_runtime,
        min_stop_time,
        unit,
        identifier=None,
        environment=None,
    ):

        """
        Info
        ----
        Initializes a HeatPump instance with specified parameters and configuration.
        
        Parameters
        ----------
        thermal_energy_demand : pandas.Series or pandas.DataFrame
            Time series of the required thermal energy demand.
        heat_pump_type : str
            Type or model of the heat pump (e.g., 'air-source', 'ground-source').
        heat_sys_temp : float
            Target temperature of the heating system (in °C).
        el_power : float
            Maximum electrical power input of the heat pump (in kW).
        th_power : float
            Maximum thermal power output of the heat pump (in kW).
        ramp_up_time : float
            Minimum time required for the heat pump to ramp up to full operation (in hours).
        ramp_down_time : float
            Minimum time required for the heat pump to ramp down to stop (in hours).
        min_runtime : float
            Minimum continuous runtime once the heat pump is started (in hours).
        min_stop_time : float
            Minimum time the heat pump must remain off after stopping (in hours).
        unit : str
            Unit identifier for the heat pump.
        identifier : str, optional
            Unique identifier for the heat pump instance (default is None).
        environment : object, optional
            Environment object containing simulation parameters such as start, end, and time frequency (default is None).
        
        Attributes
        ----------
        cop : pandas.DataFrame
            DataFrame to store coefficient of performance (COP) values.
        limit : int
            Operational limit flag (default is 1).
        last_ramp_up : pandas.Timestamp
            Timestamp of the last ramp-up event.
        last_ramp_down : pandas.Timestamp
            Timestamp of the last ramp-down event.
        timeseries_year : pandas.DataFrame
            DataFrame to store yearly time series results.
        timeseries : pandas.DataFrame
            DataFrame to store simulation time series results.
        heat_sys_temp : float
            Target heating system temperature.
        is_running : bool
            Operational status of the heat pump.
        
        """

        # Call to super class
        super(HeatPump, self).__init__(
            unit, environment
            )

        # Configure attributes
        self.identifier = identifier

        # heatpump parameters
        self.cop = pd.DataFrame()
        self.heat_pump_type = heat_pump_type
        self.el_power = el_power
        self.th_power = th_power
        self.thermal_energy_demand = thermal_energy_demand
        self.limit = 1

        # Ramp parameters
        self.ramp_up_time = ramp_up_time
        self.ramp_down_time = ramp_down_time
        self.min_runtime = min_runtime
        self.min_stop_time = min_stop_time
        self.last_ramp_up = self.thermal_energy_demand.index[0]
        self.last_ramp_down = self.thermal_energy_demand.index[0]

        self.timeseries_year = pd.DataFrame(
            columns=["thermal_energy_output", "cop", "el_demand"],
            index=self.thermal_energy_demand.index,
        )
        self.timeseries = pd.DataFrame(
            columns=["thermal_energy_output", "cop", "el_demand"],
            index=pd.date_range(
                start=self.environment.start,
                end=self.environment.end,
                freq=self.environment.time_freq,
                name="time",
            ),
        )

        self.heat_sys_temp = heat_sys_temp

        self.is_running = False

    def get_cop(self):

        """
        Info
        ----
        Calculate the Coefficient of Performance (COP) of the heat pump based on its type and environmental conditions.
        This method computes the COP for each hour using empirical formulas specific to the heat pump type
        ("Air" or "Ground"). The calculation uses the system's heat supply temperature and the mean hourly
        environmental temperature.
        
        The COP is calculated using the following formulas:
            - For "Air" heat pumps:
                COP = 6.81 - 0.121 * ΔT + 0.00063 * (ΔT)^2
            - For "Ground" heat pumps:
                COP = 8.77 - 0.15 * ΔT + 0.000734 * (ΔT)^2
            where ΔT = heat_sys_temp - mean environmental temperature.
        The method ensures that mean hourly temperatures are available by calling
        `self.environment.get_mean_temp_hours()` if necessary.
        
        Returns
        -------
        cop: pd.DataFrame
            DataFrame containing the calculated COP values for each hour, indexed by the corresponding time.
        
        """
        if len(self.environment.mean_temp_hours) == 0:
            self.environment.get_mean_temp_hours()

        cop_lst = []

        if self.heat_pump_type == "Air":
            for i, tmp in self.environment.mean_temp_hours.iterrows():
                cop = (
                    6.81
                    - 0.121 * (self.heat_sys_temp - tmp)
                    + 0.00063 * (self.heat_sys_temp - tmp) ** 2
                )
                cop_lst.append(cop)
                
        elif self.heat_pump_type == "Ground":
            for i, tmp in self.environment.mean_temp_hours.iterrows():
                cop = (
                    8.77
                    - 0.15 * (self.heat_sys_temp - tmp)
                    + 0.000734 * (self.heat_sys_temp - tmp) ** 2
                )
                cop_lst.append(cop)

        else:
            raise ValueError("Heatpump type is not defined!")

        self.cop = pd.DataFrame(
            data=cop_lst,
            index=self.environment.mean_temp_hours.index,
        )
        self.cop.columns = ["cop"]

        return self.cop

    def get_current_cop(self, tmp):
        """
        Info
        ----
        Calculate the current coefficient of performance (COP) for the heat pump based on the input temperature.
        The COP is determined using different empirical formulas depending on the type of heat pump:
            - For "Air" heat pumps, a quadratic formula based on the temperature difference is used.
            - For "Ground" heat pumps, a different quadratic formula is applied.
        Arguments
        ----------
            tmp (float): The current temperature (°C) to use in the COP calculation.
            
        Notes
        -----
            - self.heat_pump_type (str): Type of the heat pump ("Air" or "Ground").
            - self.heat_sys_temp (float): The system temperature (°C) of the heat pump.
            
        Returns
        -------
            float: The calculated COP value. Returns -9999 if the heat pump type is not defined.
        """

        if self.heat_pump_type == "Air":
            cop = (
                6.81
                - 0.121 * (self.heat_sys_temp - tmp)
                + 0.00063 * (self.heat_sys_temp - tmp) ** 2
            )

        elif self.heat_pump_type == "Ground":
            cop = (
                8.77
                - 0.15 * (self.heat_sys_temp - tmp)
                + 0.000734 * (self.heat_sys_temp - tmp) ** 2
            )

        else:
            print("Heatpump type is not defined")
            return -9999

        return cop

    # from VPPComponents
    def prepare_time_series(self):
        """
        Info
        ----
        Prepares and returns the time series data for the heat pump operation.
        This method ensures that the coefficient of performance (COP) and thermal energy demand
        are available and valid. If the COP is not set, it is calculated. If the thermal energy
        demand or the yearly time series output is missing or contains NaN values, appropriate
        actions are taken or errors are raised. The method then extracts the relevant time series
        data for the specified environment time range.
        Returns
        -------
        pandas.DataFrame
            The time series data for the heat pump operation within the specified environment time range.
        Raises
        ------
        ValueError
            If no thermal energy demand is available (i.e., contains NaN values).
        """

        if len(self.cop) == 0:
            self.get_cop()

        if (
            pd.isna(
                next(
                    iter(
                        self.thermal_energy_demand.thermal_energy_demand
                    )
                )
            )
            == True
        ):
            raise ValueError("No thermal energy demand available")

        if (
            pd.isna(next(iter(self.timeseries_year.thermal_energy_output)))
            == True
        ):
            self.get_timeseries_year()

        self.timeseries = self.timeseries_year.loc[
            self.environment.start : self.environment.end
        ]

        return self.timeseries

    def get_timeseries_year(self):
        """
        Info
        ----
        Generates and returns a DataFrame containing the yearly time series data for the heat pump.
        This method populates the `timeseries_year` DataFrame with the following columns:
            - "thermal_energy_output": Set equal to the heat pump's thermal energy demand.
            - "cop": The coefficient of performance, interpolated to fill missing values.
            - "el_demand": The calculated electrical demand, computed as the ratio of thermal energy output to COP.
            
        Returns
        -------
        pandas.DataFrame
            The updated yearly time series DataFrame with thermal energy output, COP, and electrical demand.
        """

        self.timeseries_year[
            "thermal_energy_output"
        ] = self.thermal_energy_demand
        self.timeseries_year["cop"] = self.cop
        self.timeseries_year["cop"] = self.timeseries_year["cop"].interpolate()
        self.timeseries_year["el_demand"] = (
            self.timeseries_year.thermal_energy_output
            / self.timeseries_year.cop
        )

        return self.timeseries_year

    def reset_time_series(self):

        self.timeseries = pd.DataFrame(
            columns=["thermal_energy_output", "cop", "el_demand"],
            index=pd.date_range(
                start=self.environment.start,
                end=self.environment.end,
                freq=self.environment.time_freq,
                name="time",
            ),
        )
        return self.timeseries

    # =========================================================================
    # Controlling functions
    # =========================================================================
    def limit_power_to(self, limit):
        """
        Info
        ----
        Sets the power limit for the heat pump.
        This method validates and sets the power limit as a fraction of the maximum power.
        The limit must be a float between 0 and 1 (inclusive). If the provided value is
        outside this range, a ValueError is raised.
        
        Parameters
        ----------
        limit : float
            The desired power limit as a fraction of maximum power (0 <= limit <= 1).
            
        Raises
        ------
        ValueError
            If the limit is not within the valid range [0, 1].
        """

        # Validate input parameter
        if limit >= 0 and limit <= 1:

            # Parameter is valid
            self.limit = limit

        else:

            # Parameter is invalid

            raise ValueError("Limit-parameter is not valid")

    # =========================================================================
    # Balancing Functions
    # =========================================================================

    # Override balancing function from super class.
    def value_for_timestamp(self, timestamp):

        if type(timestamp) == int:

            return self.timeseries.iloc[timestamp]["el_demand"] * self.limit

        elif type(timestamp) == str:

            return self.timeseries.loc[timestamp, "el_demand"] * self.limit

        else:
            raise ValueError(
                "timestamp needs to be of type int or string. "
                + "Stringformat: YYYY-MM-DD hh:mm:ss"
            )

    def observations_for_timestamp(self, timestamp):
        """
        Info
        ----
        Returns a dictionary of observations for a given timestamp, including thermal energy output, 
        coefficient of performance (COP), and electrical demand.
        
        Parameters
        ----------
        timestamp : int, str, or pandas._libs.tslibs.timestamps.Timestamp
            The timestamp for which to retrieve observations. Can be an integer index, 
            a string in the format 'YYYY-MM-DD hh:mm:ss', or a pandas Timestamp object.
            
        Returns
        -------
        dict
            A dictionary containing:
                - 'thermal_energy_output': float
                    The thermal energy output at the given timestamp.
                - 'cop': float
                    The coefficient of performance at the given timestamp.
                - 'el_demand': float
                    The electrical demand at the given timestamp.
                    
        Raises
        ------
        ValueError
            If the timestamp is not of type int, str, or pandas Timestamp.
            
        Notes
        -----
        If the timeseries data at the given timestamp is missing (NaN), the method estimates the values 
        based on the current running state and environmental temperature. If the heat pump is not running, 
        all values are set to zero.
        """

        if type(timestamp) == int:

            if pd.isna(next(iter(self.timeseries.iloc[timestamp]))) == False:

                thermal_energy_output, cop, el_demand = self.timeseries.iloc[
                    timestamp
                ]

            else:

                if self.is_running:
                    el_demand = self.el_power
                    temp = self.environment.mean_temp_quarter_hours.temperature.iloc[
                        timestamp
                    ]["temperature"]
                    cop = self.get_current_cop(temp)
                    thermal_energy_output = el_demand * cop
                else:
                    el_demand, cop, thermal_energy_output = 0, 0, 0

        elif type(timestamp) == str:

            if pd.isna(next(iter(self.timeseries.loc[timestamp]))) == False:

                thermal_energy_output, cop, el_demand = self.timeseries.loc[
                    timestamp
                ]
            else:

                if self.is_running:
                    el_demand = self.el_power
                    temp = self.environment.mean_temp_quarter_hours.temperature.loc[
                        timestamp
                    ]
                    cop = self.get_current_cop(temp)
                    thermal_energy_output = el_demand * cop
                else:
                    el_demand, cop, thermal_energy_output = 0, 0, 0

        elif type(timestamp) == pd._libs.tslibs.timestamps.Timestamp:

            if (
                pd.isna(next(iter(self.timeseries.loc[str(timestamp)])))
                == False
            ):

                thermal_energy_output, cop, el_demand = self.timeseries.loc[
                    str(timestamp)
                ]

            else:

                if self.is_running:
                    el_demand = self.el_power
                    temp = self.environment.mean_temp_quarter_hours.temperature.loc[
                        str(timestamp)
                    ]
                    cop = self.get_current_cop(temp)
                    thermal_energy_output = el_demand * cop
                else:
                    el_demand, cop, thermal_energy_output = 0, 0, 0

        else:
            raise ValueError(
                "timestamp needs to be of type int, "
                + "string (Stringformat: YYYY-MM-DD hh:mm:ss)"
                + " or pd._libs.tslibs.timestamps.Timestamp"
            )

        observations = {
            "thermal_energy_output": thermal_energy_output,
            "cop": cop,
            "el_demand": el_demand,
        }

        return observations

    def log_observation(self, observation, timestamp):

        self.timeseries.loc[timestamp, "thermal_energy_output"] = observation[
            "thermal_energy_output"
        ]
        self.timeseries.loc[timestamp, "cop"] = observation["cop"]
        self.timeseries.loc[timestamp, "el_demand"] = observation["el_demand"]

        return self.timeseries

    #%% ramping functions

    def is_valid_ramp_up(self, timestamp):
        """
        Info
        ----
        Determines whether the heat pump can validly ramp up at the given timestamp.
        
        Parameters
        ----------
        timestamp : int or pandas._libs.tslibs.timestamps.Timestamp
            The current time at which to check if ramp up is allowed. Can be an integer (e.g., seconds since epoch)
            or a pandas Timestamp.
            
        Returns
        -------
        None
            Updates the `is_running` attribute of the instance based on whether the minimum stop time has elapsed
            since the last ramp down.
            
        Raises
        ------
        ValueError
            If `timestamp` is not of type int or pandas._libs.tslibs.timestamps.Timestamp.
            
        Notes
        -----
        - For integer timestamps, checks if the difference between the current timestamp and `last_ramp_down` 
          exceeds `min_stop_time`.
        - For pandas Timestamps, checks if the sum of `last_ramp_down` and the minimum stop time (scaled by the 
          timeseries frequency) is less than the current timestamp.
        """

        if type(timestamp) == int:
            if timestamp - self.last_ramp_down > self.min_stop_time:
                self.is_running = True
            else:
                self.is_running = False

        elif type(timestamp) == pd._libs.tslibs.timestamps.Timestamp:
            if (
                self.last_ramp_down + self.min_stop_time * self.timeseries.index.freq
                < timestamp
            ):
                self.is_running = True
            else:
                self.is_running = False

        else:
            raise ValueError(
                "timestamp needs to be of type int or "
                + "pandas._libs.tslibs.timestamps.Timestamp"
            )

    def is_valid_ramp_down(self, timestamp):
        """
        Info
        ----
        Determines whether the heat pump can validly ramp down at the given timestamp.
        
        Parameters
        ----------
        timestamp : int or pandas._libs.tslibs.timestamps.Timestamp
            The current time, either as an integer (e.g., seconds since epoch) or as a pandas Timestamp.
            
        Returns
        -------
        None
        
        Raises
        ------
        ValueError
            If `timestamp` is not of type int or pandas._libs.tslibs.timestamps.Timestamp.
            
        Notes
        -----
        This method updates the `is_running` attribute based on whether the minimum runtime has elapsed since the last ramp up.
        """

        if type(timestamp) == int:
            if timestamp - self.last_ramp_up > self.min_runtime:
                self.is_running = False
            else:
                self.is_running = True

        elif type(timestamp) == pd._libs.tslibs.timestamps.Timestamp:
            if (
                self.last_ramp_up + self.min_runtime * self.timeseries.index.freq
                < timestamp
            ):
                self.is_running = False
            else:
                self.is_running = True

        else:
            raise ValueError(
                "timestamp needs to be of type int or "
                + "pandas._libs.tslibs.timestamps.Timestamp"
            )

    def ramp_up(self, timestamp):
        """
        Info
        ----
        Attempts to ramp up the heat pump at the specified timestamp.
        
        Parameters
        ----------
        timestamp : Any
            The timestamp at which to attempt ramping up the heat pump.
            
        Returns
        -------
        bool or None
            Returns True if the heat pump was successfully ramped up,
            False if ramp up conditions are not met,
            or None if the heat pump is already running.
            
        Notes
        -----
        This method checks if the heat pump is already running. If not, it validates
        whether ramp up is allowed at the given timestamp using `is_valid_ramp_up`.
        If successful, it sets the heat pump to running state.
        """

        if self.is_running:
            return None
        else:
            if self.is_valid_ramp_up(timestamp):
                self.is_running = True
                return True
            else:
                return False

    def ramp_down(self, timestamp):
        """
        Info
        ----
        Attempts to ramp down (turn off) the heat pump at the specified timestamp.
        
        Parameters
        ----------
        timestamp : Any
            The timestamp at which to attempt ramping down the heat pump.
            
        Returns
        -------
        bool or None
            Returns True if the heat pump was successfully ramped down,
            False if ramp down is not valid at the given timestamp,
            or None if the heat pump is not currently running.
        """


        if not self.is_running:
            return None
        else:
            if self.is_valid_ramp_down(timestamp):
                self.is_running = False
                return True
            else:
                return False
