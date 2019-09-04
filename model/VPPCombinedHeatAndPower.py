"""
Info
----
This file contains the basic functionalities of the VPPCombinedHeatAndPower class.

"""

from .VPPComponent import VPPComponent
import traceback
import pandas as pd

class VPPCombinedHeatAndPower(VPPComponent):

    def __init__(self,environment, timebase, identifier, userProfile, nominalPowerEl, nominalPowerTh, rampUpTime, rampDownTime, minimumRunningTime, minimumStopTime):
        
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
        super(VPPCombinedHeatAndPower, self).__init__(timebase, environment, userProfile)
    
    
        # Configure attributes
        self.userProfile = userProfile
        self.identifier = identifier
        self.nominalPowerEl = nominalPowerEl
        self.nominalPowerTh = nominalPowerTh
        self.rampUpTime = rampUpTime
        self.rampDownTime = rampDownTime
        self.minimumRunningTime = minimumRunningTime
        self.minimumStopTime = minimumStopTime
        self.isRunning = False

        self.lastRampUp = 0
        self.lastRampDown = 0
        self.limit = 1.0
    

    def prepareTimeSeries(self):
    
        # -> Functions stub <-
        self.timeseries = []


    # ===================================================================================
    # Controlling functions
    # ===================================================================================

    def limitPowerTo(self, limit):
        
        """
        Info
        ----
        This function limits the power of the combined heat and power plant to the given percentage.
        It cuts the current power production down to the peak power multiplied by
        the limit (Float [0;1])
        
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
            if timestamp - self.lastRampDown > self.minimumStopTime:
                self.isRunning = True
            else: self.isRunning = False
        
        elif type(timestamp) == pd._libs.tslibs.timestamps.Timestamp:
            if self.lastRampDown + self.minimumStopTime * timestamp.freq < timestamp:
                self.isRunning = True
            else: self.isRunning = False
            
        else:
            traceback.print_exc("timestamp needs to be of type int or pandas._libs.tslibs.timestamps.Timestamp")
        
    def isLegitRampDown(self, timestamp):
        
        if type(timestamp) == int:
            if timestamp - self.lastRampUp > self.minimumRunningTime:
                self.isRunning = False
            else: self.isRunning = True
        
        elif type(timestamp) == pd._libs.tslibs.timestamps.Timestamp:
            if self.lastRampUp + self.minimumRunningTime * timestamp.freq < timestamp:
                self.isRunning = False
            else: self.isRunning = True
            
        else:
            traceback.print_exc("timestamp needs to be of type int or pandas._libs.tslibs.timestamps.Timestamp")
        
    def rampUp(self, timestamp):
        
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


    
    # ===================================================================================
    # Balancing Functions
    # ===================================================================================

    def observationsForTimestamp(self, timestamp):

        # Return result
        if self.isRunning: heat_output = self.nominalPowerTh
        else: heat_output = 0
        return {
            "heat_output": heat_output,   
            "isRunning": self.isRunning,
            "lastRampUp": self.lastRampUp,
            "lastRampDown": self.lastRampDown,
            "limit": self.limit
        }



    # ===================================================================================
    # Balancing Functions
    # ===================================================================================

    # Override balancing function from super class.
    def valueForTimestamp(self, timestamp):
    
        # Check if the power plant is running
        if self.isRunning():
        
            # Return current value
            return self.nominalPowerEl * self.limit
        
        else:
        
            # Return zero
            return 0.0
