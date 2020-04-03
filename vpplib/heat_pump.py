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
        super(HeatPump, self).__init__(unit, environment, user_profile, cost)

        # Configure attributes
        self.identifier = identifier

        # heatpump parameters
        self.cop = pd.DataFrame()
        self.heat_pump_type = heat_pump_type
        self.el_power = el_power
        self.th_power = th_power
        self.limit = 1

        # Ramp parameters
        self.ramp_up_time = ramp_up_time
        self.ramp_down_time = ramp_down_time
        self.min_runtime = min_runtime
        self.min_stop_time = min_stop_time
        self.last_ramp_up = self.user_profile.thermal_energy_demand.index[0]
        self.last_ramp_down = self.user_profile.thermal_energy_demand.index[0]

        self.timeseries_year = pd.DataFrame(
            columns=["thermal_energy_output", "cop", "el_demand"],
            index=self.user_profile.thermal_energy_demand.index,
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
        Calculate COP of heatpump according to heatpump type
        
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
            index=pd.date_range(
                self.environment.year, periods=8760, freq="H", name="time"
            ),
        )
        self.cop.columns = ["cop"]

        return self.cop

    def get_current_cop(self, tmp):

        """
        Info
        ----
        Calculate COP of heatpump according to heatpump type
        
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

        if len(self.cop) == 0:
            self.get_cop()

        if (
            pd.isna(
                next(
                    iter(
                        self.user_profile.thermal_energy_demand.thermal_energy_demand
                    )
                )
            )
            == True
        ):
            self.user_profile.get_thermal_energy_demand()

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

        self.timeseries_year[
            "thermal_energy_output"
        ] = self.user_profile.thermal_energy_demand
        self.timeseries_year["cop"] = self.cop
        self.timeseries_year.cop.interpolate(inplace=True)
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
        This function limits the power of the heatpump to the given percentage.
        It cuts the current power production down to the peak power multiplied 
        by the limit (Float [0;1]).
        
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

            return self.timeseries.el_demand.iloc[timestamp] * self.limit

        elif type(timestamp) == str:

            return self.timeseries.el_demand.loc[timestamp] * self.limit

        else:
            raise ValueError(
                "timestamp needs to be of type int or string. "
                + "Stringformat: YYYY-MM-DD hh:mm:ss"
            )

    def observations_for_timestamp(self, timestamp):

        """
        Info
        ----
        This function takes a timestamp as the parameter and returns a 
        dictionary with key (String) value (Any) pairs. 
        Depending on the type of component, different status parameters of the 
        respective component can be queried. 
        
        For example, a power store can report its "State of Charge".
        Returns an empty dictionary since this function needs to be 
        implemented by child classes.
        
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

            if pd.isna(next(iter(self.timeseries.iloc[timestamp]))) == False:

                thermal_energy_output, cop, el_demand = self.timeseries.iloc[
                    timestamp
                ]

            else:

                if self.is_running:
                    el_demand = self.el_power
                    temp = self.user_profile.mean_temp_quarter_hours.temperature.iloc[
                        timestamp
                    ]
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
                    temp = self.user_profile.mean_temp_quarter_hours.temperature.loc[
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
                    temp = self.user_profile.mean_temp_quarter_hours.temperature.loc[
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

        self.timeseries.thermal_energy_output.loc[timestamp] = observation[
            "thermal_energy_output"
        ]
        self.timeseries.cop.loc[timestamp] = observation["cop"]
        self.timeseries.el_demand.loc[timestamp] = observation["el_demand"]

        return self.timeseries

    #%% ramping functions

    def is_valid_ramp_up(self, timestamp):

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

    def is_valid_ramp_down(self, timestamp):

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

    def ramp_up(self, timestamp):

        """
        Info
        ----
        This function ramps up the combined heat and power plant. The timestamp is neccessary to calculate
        if the combined heat and power plant is running in later iterations of balancing. The possible
        return values are:
            - None:       Ramp up has no effect since the combined heat and power plant is already running
            - True:       Ramp up was successful
            - False:      Ramp up was not successful (due to constraints for minimum running and stop times)
        
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
        This function ramps down the combined heat and power plant. The timestamp is neccessary to calculate
        if the combined heat and power plant is running in later iterations of balancing. The possible
        return values are:
            - None:       Ramp down has no effect since the combined heat and power plant is not running
            - True:       Ramp down was successful
            - False:      Ramp down was not successful (due to constraints for minimum running and stop times)
        
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

        if not self.is_running:
            return None
        else:
            if self.is_valid_ramp_down(timestamp):
                self.is_running = False
                return True
            else:
                return False
