
# The class "VPPEnergyStorage" adds functionality to implement an electrical energy storage to the virtual power plant

class VPPEnergyStorage(VPPComponent):

    # The constructor of the "VPPEnergyStorage"-object takes the following parameters
    # capacity [kWh]
    # chargeEfficiency [-] (between 0 and 1)
    # dischargeEfficiency [-] (between 0 and 1)
    # maxPower [kW]
    # maxC [-]
    
    # The state of charge [kWh] is set to zero by default.

    def __init__(self, capacity, chargeEfficiency, dischargeEfficiency, maxPower, maxC):

        # Call to super class
        super(VPPEnergyStorage, self).__init__(timebase)


        # Setup attributes
        self.capacity = capacity
        self.chargeEfficiency = chargeEfficiency
        self.dischargeEfficiency = dischargeEfficiency
        self.maxPower = maxPower
        self.maxC = maxC

        self.stateOfCharge = 0





    def prepareTimeSeries(self):
    
        self.timeseries = []




    # ===================================================================================
    # Observation Functions
    # ===================================================================================

    def observationsForTimestamp(self, timestamp):
    
        # TODO: Implement dataframe to return state of charge





    # ===================================================================================
    # Controlling functions
    # ===================================================================================

    # This function takes the energy [kWh] that should be charged and the timebase as
    # parameters. The timebase [minutes] is neccessary to calculate if the maximum
    # power is exceeded.

    def charge(self, energy, timebase, timestamp):

        # Check if power exceeds max power
        power = energy / (timebase / 60)

        if power > self.maxPower * self.maxC:
            energy = (self.maxPower * self.maxC) * (timebase / 60)


        # Check if charge exceeds capacity
        if self.stateOfCharge + energy * self.chargeEfficiency > self.capacity:
            energy = (self.capacity - self.stateOfCharge) * (1 / self.chargeEfficiency)


        # Update state of charge
        self.stateOfCharge += energy * self.chargeEfficiency
        
        
        # Check if data already exists
        if self.timeseries[timestamp] == None:
            self.append(energy)
        else:
            self.timeseries[timestamp] = energy





    # This function takes the energy [kWh] that should be discharged and the timebase as
    # parameters. The timebase [minutes] is neccessary to calculate if the maximum
    # power is exceeded.

    def discharge(self, energy, timebase, timestamp):

        # Check if power exceeds max power
        power = energy / (timebase / 60)

        if power > self.maxPower * self.maxC:
            energy = (self.capacity - self.stateOfCharge) * (1 / self.chargeEfficiency)


        # Check if discharge exceeds state of charge
        if self.stateOfCharge - energy * (1 / self.dischargeEfficiency) < 0:
            energy = self.stateOfCharge * self.dischargeEfficiency


        # Update state of charge
        self.stateOfCharge -= energy * (1 / self.dischargeEfficiency)
        
        
        # Check if data already exists
        if self.timeseries[timestamp] == None:
            self.append(energy)
        else:
            self.timeseries[timestamp] = energy





    # ===================================================================================
    # Balancing Functions
    # ===================================================================================

    # Override balancing function from super class.
    def valueForTimestamp(self, timestamp):

        return self.timeseries[timestamp]
