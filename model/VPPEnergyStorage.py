"""
Info
----
This file contains the basic functionalities of the VPPEnergyStorage class.

"""

from .VPPComponent import VPPComponent
import traceback
import pandas as pd

class VPPEnergyStorage(VPPComponent):

    def __init__(self, timebase, identifier, capacity, chargeEfficiency, dischargeEfficiency, maxPower, maxC, environment = None, userProfile = None):
        
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
        self.identifier = identifier
        self.capacity = capacity
        self.chargeEfficiency = chargeEfficiency
        self.dischargeEfficiency = dischargeEfficiency
        self.maxPower = maxPower
        self.maxC = maxC #factor between 0.5 and 1.2

        self.stateOfCharge = 0
        self.residual_load = None
        self.timeseries = None


    def prepareTimeSeries(self):
        
        soc_lst = []
        res_load_lst = []
        for residual_load in self.residual_load:
            
            soc, res_load = self.operate_storage(residual_load=residual_load)
            soc_lst.append(soc)
            res_load_lst.append(res_load)
        
        #save state of charge and residual load
        self.timeseries = pd.DataFrame(data=soc_lst, columns=["state_of_charge"])
        self.timeseries['residual_load'] = pd.DataFrame(data=res_load_lst)
    
        self.timeseries.index = self.residual_load.index
        
        return self.timeseries

    
    def operate_storage(self, residual_load):
        
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
        
        if residual_load > 0:
            #Energy demand --> discharge storage if stateOfCharge > 0
            
            if self.stateOfCharge > 0:
                #storage is not empty

                self.stateOfCharge -= residual_load * self.dischargeEfficiency * self.timebase
                
                #do not discharge below 0 kWh
                if self.stateOfCharge < 0:
                    residual_load = self.stateOfCharge / self.chargeEfficiency / self.timebase * -1
                    self.stateOfCharge = 0
                    
                else:
                    residual_load = 0
                    
            else:
                return self.stateOfCharge, residual_load
                
        elif residual_load < 0:
            
            #Energy surplus --> charge storage if stateOfCharge < capacity 
            
            if self.stateOfCharge < self.capacity:
                #storage has not reached its max capacity
                
                self.stateOfCharge += residual_load * self.dischargeEfficiency * self.timebase * -1
                
                #do not overcharge the storage
                if self.stateOfCharge > self.capacity:
                    residual_load = (self.capacity - 
                                     self.stateOfCharge) / self.dischargeEfficiency / self.timebase
                    self.stateOfCharge = self.capacity
                    
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
            
            stateOfCharge, residual_load = self.timeseries.iloc[timestamp]
        
        elif type(timestamp) == str:
            
            stateOfCharge, residual_load = self.timeseries.loc[timestamp]
        
        else:
            traceback.print_exc("timestamp needs to be of type int or string. Stringformat: YYYY-MM-DD hh:mm:ss")
        
        observations = {'stateOfCharge':stateOfCharge, 'residual_load':residual_load, 'max_power':self.maxPower, 'maxC':self.maxC}
        
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
        
        if type(timestamp) == int:
            
            return self.timeseries['residual_load'].iloc[timestamp]
        
        elif type(timestamp) == str:
            
            return self.timeseries['residual_load'].loc[timestamp]
        
        else:
            traceback.print_exc("timestamp needs to be of type int or string. Stringformat: YYYY-MM-DD hh:mm:ss")
        
    
    
