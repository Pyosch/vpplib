"""
Info
----
This file contains the basic functionalities of the VPPCombinedHeatAndPower class.

"""

from .VPPComponent import VPPComponent
import pandas as pd

class VPPCombinedHeatAndPower(VPPComponent):

    def __init__(self, unit="kW", identifier=None, 
                 environment=None, user_profile=None, cost = None,
                 el_power=None, th_power=None, 
                 overall_efficiency=None,
                 rampUpTime=0, rampDownTime=0,
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
        super(VPPCombinedHeatAndPower, self).__init__(unit, environment, user_profile, cost)
    
    
        # Configure attributes
        self.identifier = identifier
        self.el_power = el_power
        self.th_power = th_power
        self.overall_efficiency = overall_efficiency
        self.rampUpTime = rampUpTime
        self.rampDownTime = rampDownTime
        self.min_runtime = min_runtime
        self.min_stop_time = min_stop_time
        self.isRunning = False
        self.timeseries = pd.DataFrame(
                columns=["heat_output", "el_demand"], 
                index=pd.date_range(start=self.environment.start, 
                                    end=self.environment.end, 
                                    freq=self.environment.time_freq, 
                                    name="time"))

        self.lastRampUp = self.user_profile.heat_demand.index[0]
        self.lastRampDown = self.user_profile.heat_demand.index[0]
        self.limit = 1.0
    

    def prepareTimeSeries(self):
    
        self.timeseries = pd.DataFrame(
                columns=["heat_output", "el_demand"], 
                index=self.user_profile.heat_demand.index)


    # =========================================================================
    # Controlling functions
    # =========================================================================

    def limitPowerTo(self, limit):
        
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
        
            # Paramter is invalid
            return


    #%% ramping functions
    
    def isLegitRampUp(self, timestamp):
        
        if type(timestamp) == int:
            if timestamp - self.lastRampDown > self.min_stop_time:
                self.isRunning = True
            else: self.isRunning = False
        
        elif type(timestamp) == pd._libs.tslibs.timestamps.Timestamp:
            if self.lastRampDown + self.min_stop_time * timestamp.freq < timestamp:
                self.isRunning = True
            else: self.isRunning = False
            
        else:
            raise ValueError("timestamp needs to be of type int or " +
                             "pandas._libs.tslibs.timestamps.Timestamp")
        
    def isLegitRampDown(self, timestamp):
        
        if type(timestamp) == int:
            if timestamp - self.lastRampUp > self.min_runtime:
                self.isRunning = False
            else: self.isRunning = True
        
        elif type(timestamp) == pd._libs.tslibs.timestamps.Timestamp:
            if self.lastRampUp + self.min_runtime * timestamp.freq < timestamp:
                self.isRunning = False
            else: self.isRunning = True
            
        else:
            raise ValueError("timestamp needs to be of type int or " +
                             "pandas._libs.tslibs.timestamps.Timestamp")
        
    def rampUp(self, timestamp):
        
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
        if self.isRunning:
            return None
        else:
            if self.isLegitRampUp(timestamp):
                self.isRunning = True
                return True
            else: 
                return False


    def rampDown(self, timestamp):
        
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
    

        if not self.isRunning:
            return None
        else:
            if self.isLegitRampDown(timestamp):
                self.isRunning = False
                return True
            else: 
                return False


    
    # =========================================================================
    # Balancing Functions
    # =========================================================================

    def observationsForTimestamp(self, timestamp):

        # Return result
        if self.isRunning: 
            heat_output = self.th_power
            el_demand = self.el_power *-1
            
        else: 
            heat_output = 0
            el_demand = 0
            
        
        return {
            "heat_output": heat_output, 
            "el_demand" : el_demand,
            "isRunning": self.isRunning,
            "lastRampUp": self.lastRampUp,
            "lastRampDown": self.lastRampDown,
            "limit": self.limit
        }
        
    def log_observation(self, observation, timestamp):
        
        self.timeseries.heat_output.loc[timestamp] = observation["heat_output"]
        self.timeseries.el_demand.loc[timestamp] = observation["el_demand"]
        
        return self.timeseries



    # =========================================================================
    # Balancing Functions
    # =========================================================================

    # Override balancing function from super class.
    def valueForTimestamp(self, timestamp):
    
        # Check if the power plant is running
        if self.isRunning():
        
            # Return current value
            return self.el_power * self.limit
        
        else:
        
            # Return zero
            return 0.0
