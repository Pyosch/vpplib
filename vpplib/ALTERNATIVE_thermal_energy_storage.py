# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 16:40:16 2020

@author: andre
"""


import pandas as pd
from .component import Component


class ThermalEnergyStorage(Component):
    def __init__(
        self,
        target_temperature,
        hysteresis,
        mass,
        cp,
        #thermal_energy_loss_per_day,
        efficiency_class,
        unit,
        identifier=None,
        environment=None,
        user_profile=None,
        cost=None,
    ):

        """
        Info
        ----
        ...
        
        Parameters
        ----------
        
        The parameter timebase determines the resolution of the given data. 
        Furthermore the parameter environment (Environment) is given to provide weather data and further external influences.
        To account for different people using a component, a use case (VPPUseCase) can be passed in to improve the simulation.
        	
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
        super(ThermalEnergyStorage, self).__init__(
            unit, environment, user_profile, cost
        )

        # Configure attributes
        self.identifier = identifier
        self.target_temperature = target_temperature
        self.current_temperature = target_temperature - hysteresis
        self.timeseries = pd.DataFrame(
            columns=["temperature"],
            index=pd.date_range(
                start=self.environment.start,
                end=self.environment.end,
                freq=self.environment.time_freq,
                name="time",
            ),
        )
            
        self.efficiencies_data_APlus = [20.6, 25.4, 28.9, 31.8, 34.4, 36.4, 38.4,
                                        40.2, 41.9, 43.5, 44.9, 46.3, 47.7, 48.9,
                                        50.1, 51.3, 52.4, 53.5, 54.6, 55.6]
        
        self.efficiencies_data_A = [28.8, 35.3, 40.0, 43.9, 47.2, 50.1, 52.8,
                                    55.2, 57.4, 59.5, 61.5, 63.4, 65.2, 66.9,
                                    68.5, 70.1, 71.6, 73.1, 74.5, 75.9]
        
        self.efficiencies_data_B = [40.4, 49.4, 56.0, 61.4, 66.0, 70.1, 73.8,
                                    77.1, 80.3, 83.2, 86.0, 88.6, 91.1, 93.5,
                                    95.8, 98.0, 100.1, 102.1, 104.1, 106.1]
        
        self.efficiencies_data_C = [56.6, 69.2, 78.5, 86.0, 92.5, 98.2, 103.4,
                                    109.2, 112.6, 116.7, 120.6, 124.3, 127.8,
                                    131.1, 134.3, 137.4, 140.4, 143.2, 146.0,
                                    148.7]
        
        self.efficiencies_data = [self.efficiencies_data_APlus,
                                  self.efficiencies_data_A,
                                  self.efficiencies_data_B,
                                  self.efficiencies_data_C]
        
        self.efficiencies_volumes = [50, 100, 150, 200, 250, 300, 350, 400,
                                     450, 500, 550, 600, 650, 700, 750, 800,
                                     850, 900, 950, 1000]
        
        self.efficiencies = pd.DataFrame(self.efficiencies_data,
                                         index =["A+", "A", "B", "C"],
                                         columns = self.efficiencies_volumes)
            
        self.hysteresis = hysteresis
        self.mass = mass
        self.cp = cp
        self.efficiency_class = efficiency_class
        #self.state_of_charge = mass * cp * (self.current_temperature + 273.15)
        self.state_of_charge = mass * cp * (self.current_temperature - (target_temperature +    # somit müsste der Ladestand zu beginn immer = 0 sein
                                                                        - hysteresis))
   
        self.thermal_energy_loss_per_day = self.efficiencies[self.mass].loc[self.efficiency_class] #thermal_energy_loss_per_day
        self.thermal_energy_loss_per_day *= 24/1000
        
        self.efficiency_per_timestep = 1 - (
            self.thermal_energy_loss_per_day
            / (24 * (60 / self.environment.timebase))
        )
        self.needs_loading = None

    def operate_storage(self, timestamp, thermal_energy_generator):

        if self.get_needs_loading():
            thermal_energy_generator.ramp_up(timestamp)
        else:
            thermal_energy_generator.ramp_down(timestamp)

        thermal_energy_demand = self.user_profile.thermal_energy_demand.thermal_energy_demand.loc[
            timestamp
        ]
        observation = thermal_energy_generator.observations_for_timestamp(
            timestamp
        )
        thermal_production = observation["thermal_energy_output"]

        # Formula: E = m * cp * T
        #     <=> T = E / (m * cp)
        self.state_of_charge -= (
            (thermal_energy_demand - thermal_production)
            * 1000
            / (60 / self.environment.timebase)
        )
        self.state_of_charge *= self.efficiency_per_timestep
        self.current_temperature = (
            self.state_of_charge / (self.mass * self.cp)
        ) + (self.target_temperature - self.hysteresis) #- 273.15

        if thermal_energy_generator.is_running:
            el_load = observation["el_demand"]
        else:
            el_load = 0

        self.timeseries.temperature[timestamp] = self.current_temperature

        # log timeseries of thermal_energy_generator_class:
        thermal_energy_generator.log_observation(observation, timestamp)

        #return self.current_temperature, el_load
    
    def operate_storage_bivalent(self, timestamp, hp, hr, norm_temp):
        # determine bivalence temperature according to norm_temperature
        if norm_temp <= -16:
            biv_temp = -4 #-1
        elif (norm_temp > -16) & (norm_temp <= -10):
            biv_temp = -3 #0
        elif norm_temp > -10:
            biv_temp = -2 #1
        # dataframe with temperatures to decide whether hp or hr has to be run    
       # temperatures = pd.read_csv("./input/thermal/dwd_temp_15min_2015.csv",
                                   #index_col = "time")
        #temperatures.index = self.user_profile.thermal_energy_demand.index

        # for temperatures above bivalence the hp is running
        #if temperatures.temperature.loc[timestamp] > biv_temp:
        if self.user_profile.mean_temp_quarter_hours.temperature.loc[timestamp] > biv_temp:
            if hr.is_running:
                hr.ramp_down(timestamp)
            if self.get_needs_loading():
                hp.ramp_up(timestamp)
            else:
                hp.ramp_down(timestamp)

            thermal_energy_demand = self.user_profile.thermal_energy_demand.thermal_energy_demand.loc[
                timestamp
            ]
            observation = hp.observations_for_timestamp(
                timestamp
            )
            observation_hr = hr.observations_for_timestamp(
                    timestamp
                    )
            thermal_production = observation["thermal_energy_output"]
    
            # Formula: E = m * cp * T
            #     <=> T = E / (m * cp)
            self.state_of_charge -= (
                (thermal_energy_demand - thermal_production)
                * 1000
                / (60 / self.environment.timebase)
            )
            self.state_of_charge *= self.efficiency_per_timestep
            self.current_temperature = (
                self.state_of_charge / (self.mass * self.cp)    # hier eventuell noch Faktor 3.6 für Umrechnung Wh (abgegebene Energie hp) nach kJ
            ) + (self.target_temperature - self.hysteresis) #- 273.15
            
            #print("tes temp: " + str(self.current_temperature))
    
            if hp.is_running:
                el_load = observation["el_demand"]
            else:
                el_load = 0
    
            self.timeseries.temperature[timestamp] = self.current_temperature
    
            # log timeseries of thermal_energy_generator_class:
            hp.log_observation(observation, timestamp)
            hr.log_observation(observation_hr, timestamp)
            
            #return self.current_temperature, el_load
        
        # for temperatures below bivalence the hr is running
        #if temperatures.temperature.loc[timestamp] <= biv_temp:
        if self.user_profile.mean_temp_quarter_hours.temperature.loc[timestamp] < biv_temp:
            if hp.is_running:
                hp.ramp_down(timestamp)
            if self.get_needs_loading():
                hr.ramp_up(timestamp)
            else:
                hr.ramp_down(timestamp)

            thermal_energy_demand = self.user_profile.thermal_energy_demand.thermal_energy_demand.loc[
                timestamp
            ]
            observation = hr.observations_for_timestamp(
                timestamp
            )
            
            observation_hp = hp.observations_for_timestamp(
                timestamp
            )
            
            thermal_production = observation["thermal_energy_output"]
    
            # Formula: E = m * cp * T
            #     <=> T = E / (m * cp)
            self.state_of_charge -= (
                (thermal_energy_demand - thermal_production)
                * 1000
                / (60 / self.environment.timebase)
            )
            self.state_of_charge *= self.efficiency_per_timestep
            self.current_temperature = (
                self.state_of_charge / (self.mass * self.cp)
            ) + (self.target_temperature - self.hysteresis) #- 273.15
            
            #print("tes temp: " + str(self.current_temperature))
    
            if hr.is_running:
                el_load = observation["el_demand"]
            else:
                el_load = 0
    
            self.timeseries.temperature[timestamp] = self.current_temperature
    
            # log timeseries of thermal_energy_generator_class:
            hr.log_observation(observation, timestamp)
            hp.log_observation(observation_hp, timestamp)
            
            #return self.current_temperature, el_load


    def get_needs_loading(self):

        if self.current_temperature <= (
            self.target_temperature - self.hysteresis
        ):
            self.needs_loading = True

        if self.current_temperature >= (
            self.target_temperature + self.hysteresis
        ):
            self.needs_loading = False

        if self.current_temperature < 40:
            raise ValueError(
                "Thermal energy production to low to maintain "
                + "heat storage temperature!"
            )

        return self.needs_loading

    def value_for_timestamp(self, timestamp):

        """
        Info
        ----
        This function takes a timestamp as the parameter and returns the 
        corresponding value for that timestamp. 
        A positiv result represents a load. 
        A negative result represents a generation. 
        
        This abstract function needs to be implemented by child classes.
        Raises an error since this function needs to be implemented by child classes.
        
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

        raise NotImplementedError(
            "value_for_timestamp needs to be implemented by child classes!"
        )

    def observations_for_timestamp(self, timestamp):

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

        return {}

    def prepare_time_series(self):

        """
        Info
        ----
        This function is called to prepare the time series.
        Currently equals reset_time_series. Adjust if needed in later versions.
        
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

        self.timeseries = pd.DataFrame(
            columns=["temperature"],
            index=pd.date_range(
                start=self.environment.start,
                end=self.environment.end,
                freq=self.environment.time_freq,
                name="time",
            ),
        )
        return self.timeseries

    def reset_time_series(self):

        """
        Info
        ----
        This function is called to reset the time series
        
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

        self.timeseries = pd.DataFrame(
            columns=["temperature"],
            index=pd.date_range(
                start=self.environment.start,
                end=self.environment.end,
                freq=self.environment.time_freq,
                name="time",
            ),
        )

        return self.timeseries
    
    def optimize_tes_hp(self, hp, mode):
        if mode == "optimize runtime":
            factor = 20
        elif mode == "overcome shutdown":
            factor = 60
        else:
            raise ValueError("mode needs to be 'optimize runtime' or 'overcome shutdown'.")
            
        th_demand = self.user_profile.thermal_energy_demand
        temps = pd.read_csv("./input/thermal/dwd_temp_15min_2015.csv",
                                  index_col="time")
        
        dataframe = pd.concat([th_demand, temps], axis = 1)
        dataframe.sort_values(by = ['thermal_energy_demand'], ascending = False, inplace = True)
        
        hp.th_power = round(float(dataframe['thermal_energy_demand'][0]), 1)
        hp.el_power = round(float(hp.th_power / hp.get_current_cop(dataframe['temperature'][0])), 1)
        
        density = 1  #kg/l
        
        # mass is multiple of 10
        self.mass = hp.th_power * factor * density
        mult_50 = self.mass / 50
        mult_50 = int(mult_50) + 1
        self.mass = mult_50 * 50
        #self.mass = self.mass / 100
        #self.mass = round(self.mass, 0)
        #self.mass = self.mass * 100 + 50

