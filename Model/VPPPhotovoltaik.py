
import VPPComponent

class VPPPhotovoltaik(VPPComponent):

    # The constructor takes an identifier (String) for referencing the current
    # photovoltaik power plant. The parameter peak power (Float) determines the maximum
    # power that the photovoltaik power plant can generate.
    def __init__(self, timebase, identifier, peakPower):

        # Call to super class
        super(VPPPhotovoltaik, self).__init__(timebase)
    
    
        # Configure attributes
        self.identifier = identifier
        self.peakPower = peakPower
    
        self.limit = 1.0
    
    
    
    
    
    def prepareTimeSeries(self):
    
        # -> Functions stub <-
        self.timeseries = []





    # ===================================================================================
    # Controlling functions
    # ===================================================================================

    # This function limits the power of the photovoltaik to the given percentage.
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





    # ===================================================================================
    # Balancing Functions
    # ===================================================================================

    # Override balancing function from super class.
    def valueForTimestamp(self, timestamp):

        # -> Function stub <-
        return self.timeseries[timestamp] * self.limit
