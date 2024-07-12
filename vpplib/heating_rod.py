"""
Info
----
This file contains the basic functionalities of the VPPHeatPump class.

"""

import pandas as pd
from .component import Component

class HeatingRod(Component):
    
    def __init__(self, unit="kW", identifier=None,
                 environment=None, user_profile=None,
                 cost = None, el_power=None,
                 rampUpTime=0, rampDownTime=0,
                 min_runtime=0, min_stop_time=0, efficiency=0.95):

        
        # Call to super class
        super(HeatingRod, self).__init__(unit, environment, user_profile, cost)
        
        # Configure attributes
        self.identifier = identifier
        
        #heatinrod parameters
        self.efficiency = efficiency
        self.el_power = el_power
        self.limit = 1
        
        #Ramp parameters
        self.rampUpTime = rampUpTime
        self.rampDownTime = rampDownTime
        self.min_runtime = min_runtime
        self.min_stop_time = min_stop_time
        self.lastRampUp = self.user_profile.thermal_energy_demand.index[0]
        self.lastRampDown = self.user_profile.thermal_energy_demand.index[0]

        self.timeseries_year = pd.DataFrame(
                columns=["heat_output", "efficiency", "el_demand"], 
                index=self.user_profile.thermal_energy_demand.index)
        self.timeseries = pd.DataFrame(
                columns=["heat_output", "efficiency", "el_demand"], 
                index=pd.date_range(start=self.environment.start, 
                                    end=self.environment.end, 
                                    freq=self.environment.time_freq, 
                                    name="time"))

#        self.heat_sys_temp = heat_sys_temp
        
        self.isRunning = False
              
   
# =============================================================================
#     def get_cop(self):
#     
#         if len(self.environment.mean_temp_hours) == 0:
#             self.environment.get_mean_temp_hours()
#             
#         cop_lst = []
#         
#         if self.heatpump_type == "Air":
#             for i, tmp in self.environment.mean_temp_hours.iterrows():
#                 cop = (6.81 - 0.121 * (self.heat_sys_temp - tmp)
#                        + 0.00063 * (self.heat_sys_temp - tmp)**2)
#                 cop_lst.append(cop)
#         
#         elif self.heatpump_type == "Ground":
#             for i, tmp in self.environment.mean_temp_hours.iterrows():
#                 cop = (8.77 - 0.15 * (self.heat_sys_temp - tmp)
#                        + 0.000734 * (self.heat_sys_temp - tmp)**2)
#                 cop_lst.append(cop)
#         
#         else:
#             raise ValueError("Heatpump type is not defined!")
#         
#         self.cop = pd.DataFrame(
#                 data = cop_lst, 
#                 index = pd.date_range(self.environment.year, periods=8760, 
#                                       freq = "H", name="time"))
#         self.cop.columns = ['cop']
#         
#         return self.cop  
#     
#     def get_current_cop(self, tmp):
#         
#         """
#         Info
#         ----
#         Calculate COP of heatpump according to heatpump type
#         
#         Parameters
#         ----------
#         
#         ...
#         	
#         Attributes
#         ----------
#         
#         ...
#         
#         Notes
#         -----
#         
#         ...
#         
#         References
#         ----------
#         
#         ...
#         
#         Returns
#         -------
#         
#         ...
#         
#         """
#         
#         
#         if self.heatpump_type == "Air":
#             cop = (6.81 - 0.121 * (self.heat_sys_temp - tmp)
#                        + 0.00063 * (self.heat_sys_temp - tmp)**2)
#         
#         elif self.heatpump_type == "Ground":
#             cop = (8.77 - 0.15 * (self.heat_sys_temp - tmp)
#                        + 0.000734 * (self.heat_sys_temp - tmp)**2)
#         
#         else:
#             print("Heatpump type is not defined")
#             return -9999
# 
#         return cop
# =============================================================================
     
    #from VPPComponents
    def prepareTimeSeries(self):
            
        if pd.isna(next(iter(self.user_profile.thermal_energy_demand.thermal_energy_demand))) == True:
            self.user_profile.get_thermal_energy_demand()
          
        if pd.isna(next(iter(self.timeseries_year.heat_output))) == True:
            self.get_timeseries_year()
        
        self.timeseries = self.timeseries_year.loc[self.environment.start:self.environment.end]
        
        return self.timeseries
    
    def get_timeseries_year(self):
        
        self.timeseries_year["heat_output"] = self.user_profile.thermal_energy_demand
        self.timeseries_year["el_demand"] = (self.timeseries_year.heat_output / 
                            self.efficiency)
        
        return self.timeseries_year

    # =========================================================================
    # Controlling functions
    # =========================================================================
    def limitPowerTo(self, limit):
        
        
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
            
            return self.timeseries.iloc[timestamp]["el_demand"] * self.limit
        
        elif type(timestamp) == str:
            
            return self.timeseries.loc[timestamp, "el_demand"] * self.limit
        
        else:
            raise ValueError("timestamp needs to be of type int or string. " +
                             "Stringformat: YYYY-MM-DD hh:mm:ss")
        
    
    def observationsForTimestamp(self, timestamp):
        
        if type(timestamp) == int:
            
            if pd.isna(next(iter(self.timeseries.iloc[timestamp]))) == False:
                
                heat_output, efficiency , el_demand = self.timeseries.iloc[timestamp]
                
            else:
                
                if self.isRunning: 
                    el_demand = self.el_power
                    temp = self.user_profile.mean_temp_quarter_hours.temperature.iloc[timestamp]
                    efficiency = self.efficiency                   
                    heat_output = el_demand * efficiency
                else: 
                    el_demand, efficiency, heat_output = 0, 0, 0
            
        elif type(timestamp) == str:
            
            if pd.isna(next(iter(self.timeseries.loc[timestamp]))) == False:
                
                heat_output, efficiency , el_demand = self.timeseries.loc[timestamp]
            else:
                
                if self.isRunning: 
                    el_demand = self.el_power
                    temp = self.user_profile.mean_temp_quarter_hours.temperature.loc[timestamp]
                    efficiency = self.efficiency                  
                    heat_output = el_demand * efficiency
                else: 
                    el_demand, efficiency, heat_output = 0, 0, 0
                
        elif type(timestamp) == pd._libs.tslibs.timestamps.Timestamp:
            
            if pd.isna(next(iter(self.timeseries.loc[str(timestamp)]))) == False:
                
                 heat_output, efficiency , el_demand = self.timeseries.loc[str(timestamp)]
                 
            else:
                
                if self.isRunning: 
                    el_demand = self.el_power
                    temp = self.user_profile.mean_temp_quarter_hours.temperature.loc[str(timestamp)]
                    efficiency = self.efficiency                  
                    heat_output = el_demand * efficiency
                else: 
                    el_demand, efficiency, heat_output = 0, 0, 0
            
        else:
            raise ValueError("timestamp needs to be of type int, " +
                             "string (Stringformat: YYYY-MM-DD hh:mm:ss)" +
                             " or pd._libs.tslibs.timestamps.Timestamp")
        
        observations = {'heat_output':heat_output, 
                        'efficiency':efficiency, 'el_demand':el_demand}
        
        return observations

    def log_observation(self, observation, timestamp):
        
        self.timeseries.loc[timestamp, "heat_output"] = observation["heat_output"]
        self.timeseries.loc[timestamp, "el_demand"] = observation["el_demand"]
        
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
        
        
        if self.isRunning:
            return None
        else:
            if self.isLegitRampUp(timestamp):
                self.isRunning = True
                return True
            else: 
                return False


    def rampDown(self, timestamp):
        
    

        if not self.isRunning:
            return None
        else:
            if self.isLegitRampDown(timestamp):
                self.isRunning = False
                return True
            else: 
                return False
