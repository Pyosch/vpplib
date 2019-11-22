"""
Info
----
This file contains the basic functionalities of the CombinedHeatAndPower class.

"""

from .component import Component
import pandas as pd


class CombinedHeatAndPower(Component):

    def __init__(self, unit="kW", identifier=None,
                 environment=None, user_profile=None, cost = None,
                 el_power=None, th_power=None,
                 overall_efficiency=None,
                 ramp_up_time=0, ramp_down_time=0,
                 min_runtime=0, min_stop_time=0):
        
        """
        Info
        ----
        The constructor takes an identifier (String) for referencing the current
        combined heat and power plant. The parameters nominal power (Float) determines the
        nominal power both electrical and thermal.
        The parameters ramp up time and ramp down time (Int [s]) as well as the minimum running
        time and minimum stop time (Int [s]) are given for controlling the combined heat and power plant.
        
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
        super(CombinedHeatAndPower, self).__init__(unit, environment, user_profile, cost)
    
    
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
                index=pd.date_range(start=self.environment.start, 
                                    end=self.environment.end, 
                                    freq=self.environment.time_freq, 
                                    name="time"))

        self.last_ramp_up = self.user_profile.thermal_energy_demand.index[0]
        self.last_ramp_down = self.user_profile.thermal_energy_demand.index[0]
        self.limit = 1.0
    

    def prepare_time_series(self):
    
        self.timeseries = pd.DataFrame(
                columns=["thermal_energy_output", "el_demand"],
                index=self.user_profile.thermal_energy_demand.index)
        
        return self.timeseries
    
    
    def reset_time_series(self):
        
        self.timeseries = pd.DataFrame(
                columns=["thermal_energy_output", "el_demand"],
                index=pd.date_range(start=self.environment.start, 
                                    end=self.environment.end, 
                                    freq=self.environment.time_freq, 
                                    name="time"))
        return self.timeseries


    # =========================================================================
    # Controlling functions
    # =========================================================================

    def limit_power_to(self, limit):
        
        """
        Info
        ----
        This function limits the power of the combined heat and power plant to 
        the given percentage.
        It cuts the current power production down to the peak power multiplied 
        by the limit (Float [0;1])
        
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


    #%% ramping functions
    
    def is_valid_ramp_up(self, timestamp):
        
        if type(timestamp) == int:
            if timestamp - self.last_ramp_down > self.min_stop_time:
                self.is_running = True
            else:
                self.is_running = False
        
        elif type(timestamp) == pd._libs.tslibs.timestamps.Timestamp:
            if self.last_ramp_down + self.min_stop_time * timestamp.freq < timestamp:
                self.is_running = True
            else:
                self.is_running = False
            
        else:
            raise ValueError("timestamp needs to be of type int or " +
                             "pandas._libs.tslibs.timestamps.Timestamp")
        
    def is_valid_ramp_down(self, timestamp):
        
        if type(timestamp) == int:
            if timestamp - self.last_ramp_up > self.min_runtime:
                self.is_running = False
            else:
                self.is_running = True

        elif type(timestamp) == pd._libs.tslibs.timestamps.Timestamp:
            if self.last_ramp_up + self.min_runtime * timestamp.freq < timestamp:
                self.is_running = False
            else:
                self.is_running = True
            
        else:
            raise ValueError("timestamp needs to be of type int or " +
                             "pandas._libs.tslibs.timestamps.Timestamp")
        
    def ramp_up(self, timestamp):
        
        """
        Info
        ----
        This function ramps up the combined heat and power plant. 
        The timestamp is neccessary to calculate if the combined heat and 
        power plant is running in later iterations of balancing. The possible
        return values are:
            - None:       Ramp up has no effect since the combined heat and 
                          power plant is already running
            - True:       Ramp up was successful
            - False:      Ramp up was not successful (due to constraints for 
                          minimum running and stop times)
        
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


    
    # =========================================================================
    # Balancing Functions
    # =========================================================================

    def observations_for_timestamp(self, timestamp):

        # Return result
        if self.is_running:
            thermal_energy_output = self.th_power
            el_demand = self.el_power *-1
            
        else: 
            thermal_energy_output = 0
            el_demand = 0
            
        
        return {
            "thermal_energy_output": thermal_energy_output,
            "el_demand": el_demand,
            "is_running": self.is_running,
            "last_ramp_up": self.last_ramp_up,
            "last_ramp_down": self.last_ramp_down,
            "limit": self.limit
        }
        
    def log_observation(self, observation, timestamp):
        
        self.timeseries.thermal_energy_output.loc[timestamp] = observation["thermal_energy_output"]
        self.timeseries.el_demand.loc[timestamp] = observation["el_demand"]
        
        return self.timeseries



    # =========================================================================
    # Balancing Functions
    # =========================================================================

    # Override balancing function from super class.
    def value_for_timestamp(self, timestamp):
    
        # Check if the power plant is running
        if self.is_running():
        
            # Return current value
            return self.el_power * self.limit
        
        else:
        
            # Return zero
            return 0.0
