# -*- coding: utf-8 -*-
"""
Info
----
This file contains the basic functionalities of the Photovoltaic class.

"""

from .component import Component

import pandas as pd
import random

# pvlib imports
import pvlib

from pvlib.pvsystem import PVSystem
from pvlib.location import Location
from pvlib.modelchain import ModelChain


class Photovoltaic(Component):
    def __init__(
        self,
        unit,
        module_lib,
        inverter_lib,
        surface_tilt,
        surface_azimuth,
        module=None,
        inverter=None,
        modules_per_string=None,
        strings_per_inverter=None,
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
        super(Photovoltaic, self).__init__(
            unit, environment, user_profile, cost
        )

        # Configure attributes
        self.identifier = identifier

        self.limit = 1.0

        # load some module and inverter specifications
        self.module_lib = pvlib.pvsystem.retrieve_sam(module_lib)
        self.inverter_lib = pvlib.pvsystem.retrieve_sam(inverter_lib)

        if module:
            self.module = self.module_lib[module]

        if inverter:
            self.inverter = self.inverter_lib[inverter]

        self.location = Location(
            latitude=self.user_profile.latitude,
            longitude=self.user_profile.longitude,
        )

        self.surface_azimuth = surface_azimuth
        self.surface_tilt = surface_tilt

        if module and inverter and modules_per_string and strings_per_inverter:

            self.modules_per_string = modules_per_string
            self.strings_per_inverter = strings_per_inverter

            self.system = PVSystem(
                surface_tilt=self.surface_tilt,
                surface_azimuth=self.surface_azimuth,
                module_parameters=self.module,
                inverter_parameters=self.inverter,
                modules_per_string=self.modules_per_string,
                strings_per_inverter=self.strings_per_inverter,
            )

            self.modelchain = ModelChain(
                self.system, self.location, name=identifier
            )

            self.peak_power = (
                self.module.Impo
                * self.module.Vmpo
                / 1000
                * self.modules_per_string
                * self.strings_per_inverter
            )
            # calculate area of pv modules
            self.modules_area = (self.module.Area
              * self.modules_per_string
              * self.strings_per_inverter)

        self.timeseries = None

    def prepare_time_series(self):

        if len(self.environment.pv_data) == 0:
            raise ValueError("self.environment.pv_data is empty.")

        self.modelchain.run_model(
            times=self.environment.pv_data.loc[
                self.environment.start : self.environment.end
            ].index,
            weather=self.environment.pv_data.loc[
                self.environment.start : self.environment.end
            ],
        )

        timeseries = pd.DataFrame(self.modelchain.ac / 1000)  # convert to kW
        timeseries.rename(columns={0: self.identifier}, inplace=True)
        timeseries.set_index(timeseries.index, inplace=True)
        timeseries.index = pd.to_datetime(timeseries.index)

        self.timeseries = timeseries

        return timeseries

    def reset_time_series(self):

        self.timeseries = None

        return self.timeseries

    # ===================================================================================
    # Controlling functions
    # ===================================================================================

    # This function limits the power of the photovoltaic to the given percentage.
    # It cuts the current power production down to the peak power multiplied by
    # the limit (Float [0;1]).
    def limit_power_to(self, limit):

        # Validate input parameter
        if 0 <= limit <= 1:

            # Parameter is valid
            self.limit = limit

        else:

            # Parameter is invalid

            raise ValueError("Limit-parameter is not valid")

    # ===================================================================================
    # Balancing Functions
    # ===================================================================================

    # Override balancing function from super class.
    def value_for_timestamp(self, timestamp):

        if type(timestamp) == int:

            return (
                self.timeseries[self.identifier].iloc[timestamp] * self.limit
            )

        elif type(timestamp) == str:

            return self.timeseries[self.identifier].loc[timestamp] * self.limit

        else:
            raise ValueError(
                "timestamp needs to be of type int or string. "
                + "Stringformat: YYYY-MM-DD hh:mm:ss"
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
        if type(timestamp) == int:

            el_generation = self.timeseries.iloc[timestamp]

        elif type(timestamp) == str:

            el_generation = self.timeseries.loc[timestamp]

        else:
            raise ValueError(
                "timestamp needs to be of type int or string. "
                + "Stringformat: YYYY-MM-DD hh:mm:ss"
            )

        observations = {"el_generation": el_generation}

        return observations

    def pick_pvsystem(self, min_module_power,
                      max_module_power,
                      pv_power,
                      inverter_power_range):

        power_lst = []
        # choose modules depending on module power
        for module in self.module_lib.columns:
            if (max_module_power
                > self.module_lib[module].Impo
                * self.module_lib[module].Vmpo
                > min_module_power):
                power_lst.append(module)

        # pick random module from list
        module = power_lst[random.randint(0, (len(power_lst) -1))]

        # calculate amount of modules needed to reach power
        n_modules = (pv_power
                     / (self.module_lib[module].Impo
                        * self.module_lib[module].Vmpo))

        # calculate modules per string and strings per inverter
        if round(n_modules, 0) % 3 == 0:
            self.modules_per_string = round(n_modules, 0) / 3
            self.strings_per_inverter = 3

        elif round(n_modules, 0) % 4 == 0:
            self.modules_per_string = round(n_modules, 0) / 4
            self.strings_per_inverter = 4

        else:
            self.modules_per_string = round(n_modules, 0) / 2
            self.strings_per_inverter = 2

        # pick inverter according to peak power of modules
        inverter_lst =[]
        # sandia_inverters = pvsystem.retrieve_sam(name=inverter_lib)

        while len(inverter_lst) == 0:
            for inverter in self.inverter_lib.columns:
                if (self.inverter_lib[inverter].Paco
                    > (self.module_lib[module].Impo
                       * self.module_lib[module].Vmpo
                       * self.modules_per_string
                       * self.strings_per_inverter)) and (
                           self.inverter_lib[inverter].Paco
                           < (self.module_lib[module].Impo
                       * self.module_lib[module].Vmpo
                       * self.modules_per_string
                       * self.strings_per_inverter) + inverter_power_range):
                    inverter_lst.append(inverter)

            # increase power range of inverter if no inverter was found
            inverter_power_range += 100

        inverter = inverter_lst[
            random.randint(0, (len(inverter_lst) -1))]

        self.module = self.module_lib[module]
        self.inverter = self.inverter_lib[inverter]

        self.system = PVSystem(
            surface_tilt=self.surface_tilt,
            surface_azimuth=self.surface_azimuth,
            module_parameters=self.module,
            inverter_parameters=self.inverter,
            modules_per_string=self.modules_per_string,
            strings_per_inverter=self.strings_per_inverter,
        )

        self.modelchain = ModelChain(
            self.system, self.location, name=self.identifier
        )
    
        self.peak_power = (
            self.module.Impo
            * self.module.Vmpo
            / 1000
            * self.system.modules_per_string
            * self.system.strings_per_inverter
        )
        
        # calculate area of pv modules
        self.modules_area = (self.module.Area
          * self.modules_per_string
          * self.strings_per_inverter)

        return (self.modules_per_string,
                self.strings_per_inverter,
                self.module,
                self.inverter)