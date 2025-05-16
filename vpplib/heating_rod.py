"""
HeatingRod Module
----------------
This module contains the HeatingRod class which models an electrical resistance heater
that converts electrical energy directly into thermal energy with a specified efficiency.

The HeatingRod class inherits from the Component base class and implements specific
functionality for simulating heating rods in a virtual power plant environment.

Key features:
- Conversion of electrical energy to thermal energy
- Power limiting capabilities
- Ramping constraints (minimum runtime, minimum stop time)
- Time series generation for heat output and electrical demand
"""

import pandas as pd
from .component import Component

class HeatingRod(Component):
    """
    A class representing an electrical heating rod component in a virtual power plant.
    
    The heating rod converts electrical energy directly into thermal energy with a specified efficiency.
    It can be controlled by limiting its power output and includes ramping constraints.
    
    Attributes
    ----------
    identifier : str, optional
        Unique identifier for the heating rod
    efficiency : float
        Conversion efficiency from electrical to thermal energy (default: 0.95)
    el_power : float
        Nominal electrical power of the heating rod in kW
    limit : float
        Power limit factor between 0 and 1 (default: 1)
    thermal_energy_demand : pandas.DataFrame
        Time series of thermal energy demand
    rampUpTime : int
        Time required for the heating rod to ramp up to full power
    rampDownTime : int
        Time required for the heating rod to ramp down from full power
    min_runtime : int
        Minimum time the heating rod must run once started
    min_stop_time : int
        Minimum time the heating rod must remain off once stopped
    lastRampUp : pandas.Timestamp
        Timestamp of the last ramp up event
    lastRampDown : pandas.Timestamp
        Timestamp of the last ramp down event
    timeseries_year : pandas.DataFrame
        Annual time series of heat output and electrical demand
    timeseries : pandas.DataFrame
        Time series of heat output and electrical demand for the simulation period
    isRunning : bool
        Flag indicating whether the heating rod is currently running
    """
    
    def __init__(self, 
                 thermal_energy_demand,
                 unit="kW", 
                 identifier=None,
                 environment=None,
                 el_power=None,
                 rampUpTime=0, 
                 rampDownTime=0,
                 min_runtime=0, 
                 min_stop_time=0, 
                 efficiency=0.95):
        """
        Initialize a HeatingRod object.
        
        Parameters
        ----------
        thermal_energy_demand : pandas.DataFrame
            Time series of thermal energy demand
        unit : str, optional
            Unit of power measurement (default: "kW")
        identifier : str, optional
            Unique identifier for the heating rod
        environment : Environment, optional
            Environment object containing simulation parameters and weather data
        el_power : float, optional
            Nominal electrical power of the heating rod in kW
        rampUpTime : int, optional
            Time required for the heating rod to ramp up to full power (default: 0)
        rampDownTime : int, optional
            Time required for the heating rod to ramp down from full power (default: 0)
        min_runtime : int, optional
            Minimum time the heating rod must run once started (default: 0)
        min_stop_time : int, optional
            Minimum time the heating rod must remain off once stopped (default: 0)
        efficiency : float, optional
            Conversion efficiency from electrical to thermal energy (default: 0.95)
        """
        
        # Call to super class
        super(HeatingRod, self).__init__(unit, environment)
        
        # Configure attributes
        self.identifier = identifier
        
        # Heating rod parameters
        self.efficiency = efficiency
        self.el_power = el_power
        self.limit = 1
        self.thermal_energy_demand = thermal_energy_demand
        
        # Ramp parameters
        self.rampUpTime = rampUpTime
        self.rampDownTime = rampDownTime
        self.min_runtime = min_runtime
        self.min_stop_time = min_stop_time
        self.lastRampUp = self.thermal_energy_demand.index[0]
        self.lastRampDown = self.thermal_energy_demand.index[0]

        self.timeseries_year = pd.DataFrame(
                columns=["heat_output", "el_demand"], 
                index=self.thermal_energy_demand.index)
        self.timeseries = pd.DataFrame(
                columns=["heat_output", "el_demand"], 
                index=pd.date_range(start=self.environment.start, 
                                    end=self.environment.end, 
                                    freq=self.environment.time_freq, 
                                    name="time"))
        
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
        """
        Prepare the time series data for the simulation period.
        
        This method checks if thermal energy demand data is available, generates the annual
        time series if needed, and extracts the relevant time period for the simulation.
        
        Raises
        ------
        ValueError
            If no thermal energy demand data is available.
            
        Returns
        -------
        pandas.DataFrame
            Time series of heat output and electrical demand for the simulation period.
        """
        if pd.isna(next(iter(self.thermal_energy_demand.thermal_energy_demand))) == True:
            raise ValueError("No thermal energy demand available.")
          
        if pd.isna(next(iter(self.timeseries_year.heat_output))) == True:
            self.get_timeseries_year()
        
        self.timeseries = self.timeseries_year.loc[self.environment.start:self.environment.end]
        
        return self.timeseries
    
    def get_timeseries_year(self):
        """
        Generate the annual time series for heat output and electrical demand.
        
        This method calculates the electrical demand based on the thermal energy demand
        and the heating rod's efficiency.
        
        Returns
        -------
        pandas.DataFrame
            Annual time series of heat output and electrical demand.
        """
        self.timeseries_year["heat_output"] = self.thermal_energy_demand
        self.timeseries_year["el_demand"] = (self.timeseries_year.heat_output / 
                            self.efficiency)
        
        return self.timeseries_year

    # =========================================================================
    # Controlling functions
    # =========================================================================
    def limitPowerTo(self, limit):
        """
        Limit the power output of the heating rod.
        
        Parameters
        ----------
        limit : float
            Power limit factor between 0 and 1, where:
            - 0 means the heating rod is completely off
            - 1 means the heating rod operates at full power
            
        Returns
        -------
        None
            Returns silently if the limit is invalid.
        
        Notes
        -----
        This method validates that the limit is between 0 and 1 before applying it.
        """
        # Validate input parameter
        if limit >= 0 and limit <= 1:
            # Parameter is valid
            self.limit = limit
        else:
            # Parameter is invalid
            return

    # =========================================================================
    # Balancing Functions
    # =========================================================================

    # Override balancing function from super class.
    def valueForTimestamp(self, timestamp):
        """
        Get the electrical demand value for a specific timestamp.
        
        This method overrides the balancing function from the Component super class.
        
        Parameters
        ----------
        timestamp : int or str
            The timestamp for which to retrieve the value.
            If int: index position in the timeseries DataFrame.
            If str: timestamp in format 'YYYY-MM-DD hh:mm:ss'.
            
        Returns
        -------
        float
            The electrical demand at the specified timestamp, adjusted by the power limit.
            
        Raises
        ------
        ValueError
            If the timestamp is not of type int or string.
        """
        if type(timestamp) == int:
            return self.timeseries.iloc[timestamp]["el_demand"] * self.limit
        
        elif type(timestamp) == str:
            return self.timeseries.loc[timestamp, "el_demand"] * self.limit
        
        else:
            raise ValueError("timestamp needs to be of type int or string. " +
                             "Stringformat: YYYY-MM-DD hh:mm:ss")
        
    
    def observationsForTimestamp(self, timestamp):
        """
        Get detailed observations for a specific timestamp.
        
        This method retrieves or calculates the heat output, electrical demand, and efficiency
        for the specified timestamp.
        
        Parameters
        ----------
        timestamp : int, str, or pandas.Timestamp
            The timestamp for which to retrieve observations.
            If int: index position in the timeseries DataFrame.
            If str: timestamp in format 'YYYY-MM-DD hh:mm:ss'.
            If pandas.Timestamp: a pandas Timestamp object.
            
        Returns
        -------
        dict
            A dictionary containing 'heat_output', 'efficiency', and 'el_demand' values.
            
        Raises
        ------
        ValueError
            If the timestamp is not of a supported type.
        """
        if type(timestamp) == int:
            
            if pd.isna(next(iter(self.timeseries.iloc[timestamp]))) == False:
                
                heat_output, el_demand = self.timeseries.iloc[timestamp]
                efficiency = self.efficiency   
                
            else:
                
                if self.isRunning: 
                    el_demand = self.el_power
                    temp = self.environment.mean_temp_quarter_hours.temperature.iloc[timestamp]
                    efficiency = self.efficiency                   
                    heat_output = el_demand * efficiency
                else: 
                    el_demand, efficiency, heat_output = 0, 0, 0
            
        elif type(timestamp) == str:
            
            if pd.isna(next(iter(self.timeseries.loc[timestamp]))) == False:
                
                heat_output, el_demand = self.timeseries.loc[timestamp]
                efficiency = self.efficiency   
                
            else:
                
                if self.isRunning: 
                    el_demand = self.el_power
                    temp = self.environment.mean_temp_quarter_hours.temperature.loc[timestamp]
                    efficiency = self.efficiency                  
                    heat_output = el_demand * efficiency
                else: 
                    el_demand, efficiency, heat_output = 0, 0, 0
                
        elif type(timestamp) == pd._libs.tslibs.timestamps.Timestamp:
            
            if pd.isna(next(iter(self.timeseries.loc[str(timestamp)]))) == False:
                
                 heat_output, el_demand = self.timeseries.loc[str(timestamp)]
                 efficiency = self.efficiency   
                 
            else:
                
                if self.isRunning: 
                    el_demand = self.el_power
                    temp = self.environment.mean_temp_quarter_hours.temperature.loc[str(timestamp)]
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
        """
        Log observation values to the timeseries at the specified timestamp.
        
        Parameters
        ----------
        observation : dict
            Dictionary containing 'heat_output' and 'el_demand' values to be logged.
        timestamp : str or pandas.Timestamp
            The timestamp at which to log the observation.
            
        Returns
        -------
        pandas.DataFrame
            The updated timeseries DataFrame.
        """
        self.timeseries.loc[timestamp, "heat_output"] = observation["heat_output"]
        self.timeseries.loc[timestamp, "el_demand"] = observation["el_demand"]
        
        return self.timeseries
    #%% ramping functions
    
    
    def isLegitRampUp(self, timestamp):
        """
        Check if it's legitimate to ramp up the heating rod at the given timestamp.
        
        This method verifies if the minimum stop time has been respected since the last ramp down.
        
        Parameters
        ----------
        timestamp : int or pandas.Timestamp
            The timestamp at which to check if ramping up is legitimate.
            
        Raises
        ------
        ValueError
            If the timestamp is not of a supported type.
            
        Notes
        -----
        This method updates the isRunning attribute based on the check result.
        """
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
        """
        Check if it's legitimate to ramp down the heating rod at the given timestamp.
        
        This method verifies if the minimum runtime has been respected since the last ramp up.
        
        Parameters
        ----------
        timestamp : int or pandas.Timestamp
            The timestamp at which to check if ramping down is legitimate.
            
        Raises
        ------
        ValueError
            If the timestamp is not of a supported type.
            
        Notes
        -----
        This method updates the isRunning attribute based on the check result.
        """
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
        Attempt to ramp up the heating rod at the given timestamp.
        
        Parameters
        ----------
        timestamp : int or pandas.Timestamp
            The timestamp at which to attempt ramping up.
            
        Returns
        -------
        None
            If the heating rod is already running.
        bool
            True if ramping up was successful, False otherwise.
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
        Attempt to ramp down the heating rod at the given timestamp.
        
        Parameters
        ----------
        timestamp : int or pandas.Timestamp
            The timestamp at which to attempt ramping down.
            
        Returns
        -------
        None
            If the heating rod is already stopped.
        bool
            True if ramping down was successful, False otherwise.
        """
        if not self.isRunning:
            return None
        else:
            if self.isLegitRampDown(timestamp):
                self.isRunning = False
                return True
            else: 
                return False
