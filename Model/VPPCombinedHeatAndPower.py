
import VPPComponent

class VPPCombinedHeatAndPower(VPPComponent):

    # The constructor takes an identifier (String) for referencing the current
    # combined heat and power plant. The parameters nominal power (Float) determines the
    # nominal power both electrical and thermal.
    # The parameters ramp up time and ramp down time (Int [s]) as well as the minimum running
    # time and minimum stop time (Int [s]) are given for controlling the combined heat and power plant.
    def __init__(self, timebase, identifier, nominalPowerEl, nominalPowerTh, rampUpTime, rampDownTime, minimumRunningTime, minimumStopTime):

        # Call to super class
        super(VPPCombinedHeatAndPower, self).__init__(timebase)
    
    
        # Configure attributes
        self.identifier = identifier
        self.nominalPowerEl = nominalPowerEl
        self.nominalPowerTh = nominalPowerTh
        self.rampUpTime = rampUpTime
        self.rampDownTime = rampDownTime
        self.minimumRunningTime = minimumRunningTime
        self.minimumStopTime = minimumStopTime

        self.lastRampUp = None
        self.lastRampDown = None
        self.limit = 1.0
    
    
    
    
    
    def prepareTimeSeries(self):
    
        # -> Functions stub <-
        self.timeseries = []





    # ===================================================================================
    # Controlling functions
    # ===================================================================================

    # This function limits the power of the combined heat and power plant to the given percentage.
    # It cuts the current power production down to the peak power multiplied by
    # the limit (Float [0;1]).
    def limitPowerTo(self, limit):

        # Validate input parameter
        if limit >= 0 and limit <= 1:

            # Parameter is valid
            self.limit = limit

        else:
        
            # Paramter is invalid
            return





    def isRunning(self):
    
        # Calculate if the power plant is running
        if self.lastRampUp == None:
            return False
        else:
            if self.lastRampDown == None:
                if self.lastRampUp * self.timebase + self.rampUpTime <= timestamp * self.timestamp:
                    return True
                else:
                    return False
            else:
                if self.lastRampDown >= self.lastRampUp:
                    return False
                else:
                    if self.lastRampUp * self.timebase + self.rampUpTime <= timestamp * self.timestamp:
                        return True
                    else:
                        return False





    # This function ramps up the combined heat and power plant. The timestamp is neccessary to calculate
    # if the combined heat and power plant is running in later iterations of balancing. The possible
    # return values are:
    # - None:       Ramp up has no effect since the combined heat and power plant is already running
    # - True:       Ramp up was successful
    # - False:      Ramp up was not successful (due to constraints for minimum running and stop times)
    def rampUp(self, timestamp):

        # Check if already running
        if self.isRunning():
            return None
        else:
        
            # Check if ramp up is allowed
            if self.lastRampDown == None:
                
                # Ramp up is allowed
                self.lastRampUp = timestamp

                return True
                
            else:
            
                if self.lastRampDown * self.timebase + self.minimumStopTime <= timestamp:
                    
                    # Ramp up is allowed
                    self.lastRampUp = timestamp

                    return True
                    
                else:
                
                    # Ramp up is not allowed
                    return False
    
    
    


    # This function ramps down the combined heat and power plant. The timestamp is neccessary to calculate
    # if the combined heat and power plant is running in later iterations of balancing. The possible
    # return values are:
    # - None:       Ramp down has no effect since the combined heat and power plant is already running
    # - True:       Ramp down was successful
    # - False:      Ramp down was not successful (due to constraints for minimum running and stop times)
    def rampDown(self, timestamp):
    
        # Check if running
        if not self.isRunning():
            return None
        else:

            # Check if ramp down is allowed
            if self.lastRampUp == None:
                
                # Ramp down is allowed
                self.lastRampDown = timestamp

                return True
            
            else:
            
                if self.lastRampUp * self.timebase + self.minimumRunningTime <= timestamp:
                    
                    # Ramp down is allowed
                    self.lastRampDown = timestamp

                    return True
                
                else:
                
                    # Ramp down is not allowed
                    return False





    # This function forces a ramp up, ignoring the constraints for minimum running and stop tiimes.
    def forceRampUp(self, timestamp):

        # Ramp up
        self.lastRampUp = timestamp
    
    
    

    
    # This function forces a ramp down, ignoring the constraints for minimum running and stop tiimes.
    def forceRampDown(self, timestamp):

        # Ramp up
        self.lastRampDown = timestamp





    # ===================================================================================
    # Balancing Functions
    # ===================================================================================

    # Override balancing function from super class.
    def valueForTimestamp(self, timestamp):
    
        # Check if the power plant is running
        if self.isRunning():
        
            # Return current value
            return self.nominalPowerEl * limit
        
        else:
        
            # Return zero
            return 0.0
