# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 11:13:47 2020

@author: andre

class LatentThermalStorage. 
"""

import pandas as pd
from .component import Component


class LatentThermalStorage(Component):
    def __init__(
        self,
        t_over,     # overheating water
        t_under,    # undercooling ice
        t_nuc = 0,
        mass = None,
        cp_water = 4.19,    # [kJ/(kg*K)]
        cp_ice = 2.06,  # [kJ/(kg*K)]
        h_crist = 333,   #[kJ/kg]
        unit = None,
        identifier = None,
        environment = None,
        user_profile = None,
        cost = None,
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
        super(LatentThermalStorage, self).__init__(
            unit, environment, user_profile, cost
        )

        # Configure attributes
        self.identifier = identifier
        self.environment = environment
        self.user_profile = user_profile
        self.cost = cost
        
        self.t_nuc = t_nuc
        self.t_over = t_over
        self.t_under = t_under
        self.current_temp = t_nuc - t_under     # start at lowest temp => storage "empty", water frozen
        self.mass = mass
        self.cp_ice = cp_ice
        self.cp_water = cp_water
        self.h_crist = h_crist
        self.density_ice = 0.92 #[kg/l]
        self.capacity = None
        self.capacity_solid = None
        self.capacity_phaseChange = None
        self.capacity_fluid = None
        self.current_state = None
        self.is_loaded = False
        
        self.timeseries = pd.DataFrame(
                columns = ["temperature", "state_of_charge", "m_ice", "m_water"],
                index = pd.date_range(
                        start = self.environment.start,
                        end = self.environment.end,
                        freq = self.environment.time_freq,
                        name = "time"
                        )
                )
                
        self.state_of_charge = 0.0        # water frozen, energy = 0 at beginning
        self.m_ice = self.mass          # water completely frozen
        self.m_water = None             # see above
        
    def layout_storage (self, hp_dimensionized):
        if hp_dimensionized.th_power <= 10:
            vol = 14.3 
        elif hp_dimensionized.th_power > 10:
            vol = 28.6
            
        self.mass = vol * 1000 * self.density_ice
        
        self.get_capacity()
# =============================================================================
#         density = 1  # kg/l
#         max_demand = self.user_profile.thermal_energy_demand.thermal_energy_demand.max()
#         # layout according to formula used for TES
#         mass = max_demand * 20 * density
#         mult_50 = mass / 50
#         mult_50 = int(mult_50) + 1
#         self.mass = mult_50 * 50
#         # calculate capacity [kWh] for later use
#         self.get_capacity()
# =============================================================================
        
    def get_capacity(self):
        # calculate capacity [kWh]
        self.capacity_solid = self.mass * self.cp_ice * self.t_under / 3600
        self.capacity_phaseChange = self.mass * self.h_crist / 3600
        self.capacity_fluid = self.mass * self.cp_water * self.t_over / 3600
        self.capacity = self.capacity_solid + self.capacity_phaseChange + self.capacity_fluid
        
# =============================================================================
#     def get_capacity_solid(self):
#         return self.mass * self.cp_ice * self.t_under / 3600
#     
#     def get_capacity_phaseChange(self):
#         return self.mass * self.h_crist / 3600
#     
#     def get_capacity_fluid(self):
#         return self.mass * self.cp_water * self.t_over / 3600
# =============================================================================
        
    def needs_loading(self):
        if self.current_temp <= self.t_nuc + self.t_under:
            return True
        elif self.current_temp >= self.t_nuc - self.t_over:
            return False
        
    def get_current_state(self):
        if self.state_of_charge <= self.capacity_solid:
            self.current_state = "solid"
        elif self.state_of_charge > self.capacity_solid and self.state_of_charge < (self.capacity_solid + self.capacity_phaseChange):
            self.current_state = "mix"
        elif self.state_of_charge >= (self.capacity_solid + self.capacity_phaseChange):
            self.current_state = "fluid"
            
    def get_phase_state(self):
        if self.current_state == "solid":
            self.m_water = 0
            self.m_ice = self.mass
        elif self.current_state == "mix":
            # part of water increasing linear with energy (=0 at start of melting and =1 at end of melting)
            self.m_water = self.state_of_charge / (self.capacity_solid + self.capacity_phaseChange) * self.mass
            self.m_ice = self.mass - self.m_water
        elif self.current_state == "fluid":
            self.m_water = self.mass
            self.m_ice = 0
            
    def get_current_temp(self):
        if self.current_state == "solid":
            self.current_temp = self.t_nuc - self.t_under + self.state_of_charge / (self.mass * self.cp_ice) *3600
        elif self.current_state == "mix":
            self.current_temp = self.t_nuc
        elif self.current_state == "fluid":
            self.current_temp = self.t_nuc + (self.state_of_charge - self.capacity_phaseChange - self.capacity_solid) / (self.mass * self.cp_water) * 3600
        
    # Anmerkung für Betrieb: HP bezieht Wärme eigentlich nur von Solar-Luft-Absorber (größtenteils Luft)
    # Nur wenn die Lufttemperatur unter einen gewissen wert fällt, wird zusätzlich wärme aus dem lts bezogen
    def operate_storage(self, timestamp, thermal_energy_generator):
        if not self.is_loaded:
            if self.needs_loading():
                thermal_energy_generator.ramp_up(timestamp)
            else:
                thermal_energy_generator.ramp_down(timestamp)
                
        else:
            if thermal_energy_generator.is_running:
                thermal_energy_generator.ramp_down(timestamp)
            
        thermal_energy_demand = self.user_profile.thermal_energy_demand.thermal_energy_demand.loc[timestamp]
        observation = thermal_energy_generator.observations_for_timestamp(timestamp)
        thermal_production = observation["thermal_energy_output"]
        
        thermal_energy_generator.log_observation(observation, timestamp)
        
        self.state_of_charge -= (thermal_energy_demand - thermal_production) * self.environment.timebase / 60
        if self.state_of_charge >= self.capacity:
            self.is_loaded = True
        elif self.state_of_charge <= 0:
            self.is_loaded = False
        
        self.get_current_state()
        
        self.get_current_temp()
        
        self.get_phase_state()
        
        self.timeseries.temperature.loc[timestamp] = self.current_temp
        self.timeseries.state_of_charge.loc[timestamp] = self.state_of_charge
        self.timeseries.m_ice.loc[timestamp] = self.m_ice /self.mass
        self.timeseries.m_water.loc[timestamp] = self.m_water / self.mass
                
                
    
    
        
        
        
        
        