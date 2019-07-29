"""
Info
----
This file contains the basic functionalities of the VPPEnergyStorage class.

"""

from .VPPComponent import VPPComponent
import traceback

class VPPEnergyStorage(VPPComponent):

    def __init__(self, timebase, capacity, chargeEfficiency, dischargeEfficiency, maxPower, maxC, environment = None, userProfile = None):
        
        """
        Info
        ----
        The class "VPPEnergyStorage" adds functionality to implement an 
        electrical energy storage to the virtual power plant.
        
        
        Parameters
        ----------
        
        capacity [kWh]
        chargeEfficiency [-] (between 0 and 1)
        dischargeEfficiency [-] (between 0 and 1)
        maxPower [kW]
        maxC [-]
        	
        Attributes
        ----------
        
        The stateOfCharge [kWh] is set to zero by default.
        
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
        super(VPPEnergyStorage, self).__init__(timebase, environment, userProfile)


        # Setup attributes
        self.timebase = timebase
        self.capacity = capacity
        self.chargeEfficiency = chargeEfficiency
        self.dischargeEfficiency = dischargeEfficiency
        self.maxPower = maxPower
        self.maxC = maxC

        self.stateOfCharge = 0





    def prepareTimeSeries(self):
    
        self.timeseries = []

    
    def operate_storage(self, residual_load):
        """
        #TODO: Find better name for this function
        
        residual_load > 0 = Energy demand
        residual_load < 0 = Energy surplus
        
        needed from device:                 implemented:
            device.p_nom                        ()
            device.efficiency_store             ()
            device.efficiency_dispatch          ()
            device.capacity                     (x)
            device.state_of_charge_initial      (needed?)
            device.state_of_charge_t            (x)
            device.time_base                    (x)
        """
        if residual_load > 0:
            #Energy demand --> discharge storage if stateOfCharge > 0
            
            if self.stateOfCharge > 0:
                #storage is not empty

                self.stateOfCharge -= residual_load * self.timebase
                
                #do not discharge below 0 kWh
                if self.stateOfCharge < 0:
                    residual_load = self.stateOfCharge / self.timebase * -1
                    self.stateOfCharge = 0
                    
                else:
                    residual_load = 0
                    
            else:
                return self.stateOfCharge, residual_load
                
        elif residual_load < 0:
            
            #Energy surplus --> charge storage if stateOfCharge < maxC 
            
            if self.stateOfCharge < self.maxC:
                #storage has not reached its max capacity
                
                self.stateOfCharge += residual_load *self.timebase * -1
                
                #do not overcharge the storage
                if self.stateOfCharge > self.maxC:
                    residual_load = (self.maxC - 
                                     self.stateOfCharge) /self.timebase
                    self.stateOfCharge = self.maxC
                    
                else:
                    residual_load = 0
                    
            else:
                #storage has reached its max capacity
                return self.stateOfCharge, residual_load
        
        return self.stateOfCharge, residual_load


    # ===================================================================================
    # Observation Functions
    # ===================================================================================

    def observationsForTimestamp(self, timestamp):
        
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
            
            stateOfCharge = self.timeseries.iloc[timestamp]
        
        elif type(timestamp) == str:
            
            stateOfCharge = self.timeseries.loc[timestamp]
        
        else:
            traceback.print_exc("timestamp needs to be of type int or string. Stringformat: YYYY-MM-DD hh:mm:ss")
        
        # TODO: cop would change if power of heatpump is limited. 
        # Dropping limiting factor for heatpumps
        
        observations = {'stateOfCharge':stateOfCharge, 'max_power':self.maxPower, 'maxC':self.maxC}
        
        return observations

    # ===================================================================================
    # Controlling functions
    # ===================================================================================

    def charge(self, energy, timebase, timestamp):
        
        """
        Info
        ----
        This function takes the energy [kWh] that should be charged and the timebase as
        parameters. The timebase [minutes] is neccessary to calculate if the maximum
        power is exceeded.
        
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


    def discharge(self, energy, timebase, timestamp):
        
        """
        Info
        ----
        This function takes the energy [kWh] that should be discharged and the timebase as
        parameters. The timebase [minutes] is neccessary to calculate if the maximum
        power is exceeded.
        
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
    
    
