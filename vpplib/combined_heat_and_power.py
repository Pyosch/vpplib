# -*- coding: utf-8 -*-
"""
Info
----
This file contains the basic functionalities of the CombinedHeatAndPower class.

"""

from .component import Component
import pandas as pd


class CombinedHeatAndPower(Component):
    def __init__(
        self,
        el_power,
        th_power,
        ramp_up_time,
        ramp_down_time,
        min_runtime,
        min_stop_time,
        overall_efficiency,
        unit,
        identifier=None,
        environment=None,
        user_profile=None,
        cost=None,
    ):

        """
        Info
        ----
        The constructor takes an identifier (String) for referencing the
        current combined heat and power plant. The parameters nominal power
        (Float) determines the nominal power both electrical and thermal.
        The parameters ramp up time and ramp down time as well as the minimum
        running time and minimum stop time are given for controlling the
        combined heat and power plant.

        Parameters
        ----------
        el_power: float
            nominal electrical power output of the chp

        th_power: float
            nominal thermal power output of the chp

        ramp_up_time: float
            number of timesteps needed for the chp to reach the nominal power

        ramp_down_time: float
            number of timesteps needed for the chp to reduce the nominal power
            to zero

        min_runtime: float
            number of timesteps the chp needs to be running to prevent damage

        min_stop_time: float
            number of timesteps the chp needs to be shut down after running to
            prevent damage

        overall_efficiency: float
            the efficiency to calculate the demand for primary resources
            (e.g. oil, gas)

        unit: string
            unit used for the power values of the chp

        identifier: string
            name of the component

        environment: vpplib.environment.Environment
            object containing time and weather related data

        user_profile: vpplib.user_profile.UserProfile
            object containing user specific data like heat demand

        cost: float
            financial cost of one unit of the component

        Attributes
        ----------
        timeseries: pandas.core.frame.DataFrame
            DataFrame containing the generation of electrival and thermal
            energy over a given period of time

        is_running: boolean
            True if the chp is running, False if turned off

        last_ramp_up: datetime64[ns]
            timestamp of the last ramp up

        last_ramp_down: datetime64[ns]
            timestamp of the last ramp down

        limit: float
            value between 0 and 1 to limit the nominal power

        """

        # Call to super class
        super(CombinedHeatAndPower, self).__init__(
            unit, environment, user_profile, cost
        )

        # Configure attributes
        self.identifier = identifier
        self.el_power = el_power
        self.th_power = th_power
        self.overall_efficiency = overall_efficiency
        self.ramp_up_time = ramp_up_time
        self.ramp_down_time = ramp_down_time
        self.min_runtime = min_runtime
        self.min_stop_time = min_stop_time
        self.is_running = False
        self.timeseries = pd.DataFrame(
            columns=["thermal_energy_output", "el_demand"],
            index=pd.date_range(
                start=self.environment.start,
                end=self.environment.end,
                freq=self.environment.time_freq,
                name="time",
            ),
        )

        self.last_ramp_up = self.user_profile.thermal_energy_demand.index[0]
        self.last_ramp_down = self.user_profile.thermal_energy_demand.index[0]
        self.limit = 1.0

    def prepare_time_series(self):

        """
        Info
        ----
        This is the standard function to create a time series for the
        CombinedHeatAndPower class. For this time series no specific operation
        stategy is implemented.

        Returns
        -------
        self.timeseries

        """

        self.timeseries = pd.DataFrame(
            columns=["thermal_energy_output", "el_demand"],
            index=self.user_profile.thermal_energy_demand.index,
        )

        return self.timeseries

    def reset_time_series(self):

        self.timeseries = pd.DataFrame(
            columns=["thermal_energy_output", "el_demand"],
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
        Limit the power of the combined heat and power plant to the given
        percentage.

        Parameters
        ----------
        limit: float
            value between 0 and 1 to limit the nominal power

        """

        # Validate input parameter
        if limit >= 0 and limit <= 1:

            # Parameter is valid
            self.limit = limit

        else:
            # Parameter is invalid
            raise ValueError("Limit-parameter is not valid")

    # %% ramping functions

    def is_valid_ramp_up(self, timestamp):

        """
        Info
        ----
        Check if a ramp up is valid by comparing the current timestamp,
        the timestamp of the last ramp down and the minimum stop time of the
        chp.

        Parameters
        ----------
        timestamp: datetime64[ns]
            value of the time of ramp up

        Returns
        -------
        self.is_running = True, if ramp up is valid
        self.is_running = False, if ramp up is not valid

        """

        if type(timestamp) == int:
            if timestamp - self.last_ramp_down > self.min_stop_time:
                self.is_running = True
            else:
                self.is_running = False

        elif type(timestamp) == pd._libs.tslibs.timestamps.Timestamp:
            if (
                self.last_ramp_down + self.min_stop_time * timestamp.freq
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

        return self.is_running

    def is_valid_ramp_down(self, timestamp):

        """
        Info
        ----
        Check if a ramp down is valid by comparing the current timestamp,
        the timestamp of the last ramp up and the minimum stop time of the
        chp.

        Parameters
        ----------
        timestamp: datetime64[ns]
            value of the time of ramp down

        Returns
        -------
        self.is_running = False, if ramp down is valid
        self.is_running = True, if ramp down is not valid

        """

        if type(timestamp) == int:
            if timestamp - self.last_ramp_up > self.min_runtime:
                self.is_running = False
            else:
                self.is_running = True

        elif type(timestamp) == pd._libs.tslibs.timestamps.Timestamp:
            if (
                self.last_ramp_up + self.min_runtime * timestamp.freq
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

        return self.is_running

    def ramp_up(self, timestamp):

        """
        Info
        ----
        This function ramps up the combined heat and power plant.
        The timestamp is neccessary to calculate if the chp is running in
        later iterations of balancing.

        Parameters
        ----------
        timestamp: datetime64[ns]
            value of the time of ramp up

        Returns
        -------
        None: Ramp up has no effect since the chp is already running
        True: Ramp up was successful
        False: Ramp up was not successful
               (due to constraints for minimum running and stop times).

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
        This function ramps down the combined heat and power plant.
        The timestamp is neccessary to calculate if the chp is running in
        later iterations of balancing.

        Parameters
        ----------
        timestamp: datetime64[ns]
            value of the time of ramp down

        Returns
        -------
        None: Ramp down has no effect since the chp is not running
        True: Ramp down was successful
        False: Ramp down was not successful
               (due to constraints for minimum running and stop times)

        """

        if not self.is_running:
            return None
        else:
            if self.is_valid_ramp_down(timestamp):
                self.is_running = False
                return True
            else:
                return False

    # =========================================================================
    # Balancing Functions
    # =========================================================================

    # Override balancing function from super class.
    def observations_for_timestamp(self, timestamp):

        """
        Info
        ----
        This function takes a timestamp as the parameter and returns a
        dictionary with key (String) value (Any) pairs.

        Parameters
        ----------
        timestamp: datetime64[ns]
            value of the time of ramp down

        Returns
        -------
        dict with:
            thermal power generation: float
            electrical power generation: float
            is_running: boolean
            last_ramp_up: datetime64[ns]
            last_ramp_down: datetime64[ns]
            limit: float

        """

        if self.is_running:
            thermal_energy_output = self.th_power
            el_demand = self.el_power * -1

        else:
            thermal_energy_output = 0
            el_demand = 0

        return {
            "thermal_energy_output": thermal_energy_output,
            "el_demand": el_demand,
            "is_running": self.is_running,
            "last_ramp_up": self.last_ramp_up,
            "last_ramp_down": self.last_ramp_down,
            "limit": self.limit,
        }

    def log_observation(self, observation, timestamp):

        """
        Info
        ----
        This function logs the values from the dictionary, returned by the
        function observations_for_timestamp to the corresponding timestamp
        in self.timeseries. This allows to create a timeseries, depending on an
        operation strategy, e.g. in combination with a electrical and/or
        thermal storage.

        Parameters
        ----------
        observation: dict
            dictionary returned by the function observations_for_timestamp

        timestamp: datetime64[ns]
            value of the time of ramp down

        Returns
        -------
        self.timeseries

        """

        self.timeseries.thermal_energy_output.loc[timestamp] = observation[
            "thermal_energy_output"
        ]
        self.timeseries.el_demand.loc[timestamp] = observation["el_demand"]

        return self.timeseries

    def value_for_timestamp(self, timestamp):

        """
        Info
        ----
        This function takes a timestamp as the parameter and returns the
        corresponding power demand for that timestamp.
        A positiv result represents a load.
        A negative result represents a generation.

        Parameters
        ----------
        timestamp: datetime64[ns]
            value of the time of ramp down

        Returns
        -------
        power value for timestamp: float

        """

        if self.is_running:

            # Return current value
            return self.el_power * self.limit

        else:

            # Return zero
            return 0.0
