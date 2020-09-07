# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 16:40:51 2020

@author: andre
class SolarThermal
kept simple, not concerning area or slope/intensity of irradiation (Handbuch Viessmann)
temperature of fluid is expected to be 3°C above ambient temperature, due to irradiation
"""

import pandas as pd
from .component import Component

class SolarThermal(Component):
    def __init__(
        self,
        cp_heat_carrier = 3.5   # [kj/(kg*K)] wikipedia
        mass_fluid = None,
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
        super(SolarThermal, self).__init__(
            unit, environment, user_profile, cost
        )
        
        # Configure attributes
        self.identifier = identifier
        self.environment = environment
        self.user_profile = user_profile
        self.cost = cost
        
        self.timeseries = pd.DataFrame(
                columns = ["temperature", "state_of_charge", "m_ice", "m_water"],
                index = pd.date_range(
                        start = self.environment.start,
                        end = self.environment.end,
                        freq = self.environment.time_freq,
                        name = "time"
                        )
                )        