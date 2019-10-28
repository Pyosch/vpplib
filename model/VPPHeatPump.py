"""
Info
----
This file contains the basic functionalities of the VPPHeatPump class.

"""

import pandas as pd
from .VPPComponent import VPPComponent

class VPPHeatPump(VPPComponent):
    
    def __init__(self, unit="kW", identifier=None,
                 environment=None, user_profile=None,
                 heatpump_type="Air",
                 heat_sys_temp=60,
                 el_power=None, th_power=None,
                 rampUpTime=0, rampDownTime=0,
                 min_runtime=0, min_stop_time=0):
        
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
        super(VPPHeatPump, self).__init__(unit, environment, user_profile)
        
        # Configure attributes
        self.identifier = identifier
        
        #heatpump parameters
        self.cop = pd.DataFrame()
        self.heatpump_type = heatpump_type
        self.el_power = el_power
        self.th_power = th_power
        self.limit = 1
        
        #Ramp parameters
        self.rampUpTime = rampUpTime
        self.rampDownTime = rampDownTime
        self.min_runtime = min_runtime
        self.min_stop_time = min_stop_time
        self.lastRampUp = self.user_profile.heat_demand.index[0]
        self.lastRampDown = self.user_profile.heat_demand.index[0]

        self.timeseries_year = pd.DataFrame(
                columns=["heat_output", "cop", "el_demand"], 
                index=self.user_profile.heat_demand.index)
        self.timeseries = pd.DataFrame(
                columns=["heat_output", "cop", "el_demand"], 
                index=pd.date_range(start=self.environment.start, 
                                    end=self.environment.end, 
                                    freq=self.environment.time_freq, 
                                    name="time"))

        self.heat_sys_temp = heat_sys_temp
        
        self.isRunning = False
              
    
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
        
        if self.heatpump_type == "Air":
            for i, tmp in self.environment.mean_temp_hours.iterrows():
                cop = (6.81 - 0.121 * (self.heat_sys_temp - tmp)
                       + 0.00063 * (self.heat_sys_temp - tmp)**2)
                cop_lst.append(cop)
        
        elif self.heatpump_type == "Ground":
            for i, tmp in self.environment.mean_temp_hours.iterrows():
                cop = (8.77 - 0.15 * (self.heat_sys_temp - tmp)
                       + 0.000734 * (self.heat_sys_temp - tmp)**2)
                cop_lst.append(cop)
        
        else:
            raise ValueError("Heatpump type is not defined!")
        
        self.cop = pd.DataFrame(
                data = cop_lst, 
                index = pd.date_range(self.environment.year, periods=8760, 
                                      freq = "H", name="time"))
        self.cop.columns = ['cop']
        
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
        
        
        if self.heatpump_type == "Air":
            cop = (6.81 - 0.121 * (self.heat_sys_temp - tmp)
                       + 0.00063 * (self.heat_sys_temp - tmp)**2)
        
        elif self.heatpump_type == "Ground":
            cop = (8.77 - 0.15 * (self.heat_sys_temp - tmp)
                       + 0.000734 * (self.heat_sys_temp - tmp)**2)
        
        else:
            print("Heatpump type is not defined")
            return -9999

        return cop
     
    #from VPPComponents
    def prepareTimeSeries(self):
        
        if len(self.cop) == 0:
            self.get_cop()
            
        if pd.isna(next(iter(self.user_profile.heat_demand.heat_demand))) == True:
            self.user_profile.get_heat_demand()
          
        if pd.isna(next(iter(self.timeseries_year.heat_output))) == True:
            self.get_timeseries_year()
        
        self.timeseries = self.timeseries_year.loc[self.environment.start:self.environment.end]
        
        return self.timeseries
    
    def get_timeseries_year(self):
        
        self.timeseries_year["heat_output"] = self.user_profile.heat_demand
        self.timeseries_year["cop"] = self.cop
        self.timeseries_year.cop.interpolate(inplace = True)
        self.timeseries_year["el_demand"] = (self.timeseries_year.heat_output / 
                            self.timeseries_year.cop)
        
        return self.timeseries_year

    # =========================================================================
    # Controlling functions
    # =========================================================================
    def limitPowerTo(self, limit):
        
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
        
            # Paramter is invalid
            return

    # =========================================================================
    # Balancing Functions
    # =========================================================================

    # Override balancing function from super class.
    def valueForTimestamp(self, timestamp):

        if type(timestamp) == int:
            
            return self.timeseries.el_demand.iloc[timestamp] * self.limit
        
        elif type(timestamp) == str:
            
            return self.timeseries.el_demand.loc[timestamp] * self.limit
        
        else:
            raise ValueError("timestamp needs to be of type int or string. " +
                             "Stringformat: YYYY-MM-DD hh:mm:ss")
        
    
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
            
            if pd.isna(next(iter(self.timeseries.iloc[timestamp]))) == False:
                
                heat_output, cop , el_demand = self.timeseries.iloc[timestamp]
                
            else:
                
                if self.isRunning: 
                    el_demand = self.el_power
                    temp = self.user_profile.mean_temp_quarter_hours.temperature.iloc[timestamp]
                    cop = self.get_current_cop(temp)                   
                    heat_output = el_demand * cop
                else: 
                    el_demand, cop, heat_output = 0, 0, 0
            
        elif type(timestamp) == str:
            
            if pd.isna(next(iter(self.timeseries.loc[timestamp]))) == False:
                
                heat_output, cop , el_demand = self.timeseries.loc[timestamp]
            else:
                
                if self.isRunning: 
                    el_demand = self.el_power
                    temp = self.user_profile.mean_temp_quarter_hours.temperature.loc[timestamp]
                    cop = self.get_current_cop(temp)                   
                    heat_output = el_demand * cop
                else: 
                    el_demand, cop, heat_output = 0, 0, 0
                
        elif type(timestamp) == pd._libs.tslibs.timestamps.Timestamp:
            
            if pd.isna(next(iter(self.timeseries.loc[str(timestamp)]))) == False:
                
                 heat_output, cop , el_demand = self.timeseries.loc[str(timestamp)]
                 
            else:
                
                if self.isRunning: 
                    el_demand = self.el_power
                    temp = self.user_profile.mean_temp_quarter_hours.temperature.loc[str(timestamp)]
                    cop = self.get_current_cop(temp)                   
                    heat_output = el_demand * cop
                else: 
                    el_demand, cop, heat_output = 0, 0, 0
            
        else:
            raise ValueError("timestamp needs to be of type int, " +
                             "string (Stringformat: YYYY-MM-DD hh:mm:ss)" +
                             " or pd._libs.tslibs.timestamps.Timestamp")
        
        observations = {'heat_output':heat_output, 
                        'cop':cop, 'el_demand':el_demand}
        
        return observations

    def log_observation(self, observation, timestamp):
        
        self.timeseries.heat_output.loc[timestamp] = observation["heat_output"]
        self.timeseries.cop.loc[timestamp] = observation["cop"]
        self.timeseries.el_demand.loc[timestamp] = observation["el_demand"]
        
        return self.timeseries
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
