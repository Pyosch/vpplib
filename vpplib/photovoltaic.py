# -*- coding: utf-8 -*-
"""Photovoltaic Module.

This module contains the Photovoltaic class, which models a photovoltaic system
using the pvlib library. It provides functionality for simulating power generation
based on weather data and system specifications.

The Photovoltaic class inherits from the Component class and implements methods
for preparing time series data, limiting power output, and retrieving observations.
"""

from vpplib.component import Component

import pandas as pd
import random

# pvlib imports
import pvlib

from pvlib.pvsystem import PVSystem
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS


class Photovoltaic(Component):
    """Photovoltaic system component for a virtual power plant.
    
    This class models a photovoltaic system using the pvlib library. It simulates
    power generation based on weather data and system specifications.
    
    Attributes
    ----------
    identifier : str
        Unique identifier for the photovoltaic system.
    limit : float
        Power limit factor (0.0 to 1.0) to curtail output.
    module_lib : dict
        Dictionary of available PV modules from SAM library.
    inverter_lib : dict
        Dictionary of available inverters from SAM library.
    temperature_model_parameters : dict
        Parameters for the temperature model.
    module : pandas.Series
        Selected module specifications.
    inverter : pandas.Series
        Selected inverter specifications.
    location : pvlib.location.Location
        Geographic location of the PV system.
    surface_azimuth : float
        Azimuth angle of the PV array surface.
    surface_tilt : float
        Tilt angle of the PV array surface.
    modules_per_string : int
        Number of modules per string.
    strings_per_inverter : int
        Number of strings per inverter.
    system : pvlib.pvsystem.PVSystem
        PV system object from pvlib.
    modelchain : pvlib.modelchain.ModelChain
        ModelChain object for simulating the PV system.
    peak_power : float
        Peak power of the PV system in kW.
    modules_area : float
        Total area of all PV modules in m².
    timeseries : pandas.DataFrame
        Time series of power generation.
    """
    
    def __init__(
        self,
        unit,
        latitude,
        longitude,
        module_lib,
        inverter_lib,
        surface_tilt,
        surface_azimuth,
        module=None,
        inverter=None,
        modules_per_string=None,
        strings_per_inverter=None,
        temp_lib=None,
        temp_model=None,
        identifier=None,
        environment=None,
    ):
        """Initialize a Photovoltaic object.
        
        Parameters
        ----------
        unit : str
            Unit of measurement for power output (typically 'kW').
        latitude : float
            Latitude of the PV system location.
        longitude : float
            Longitude of the PV system location.
        module_lib : str
            Name of the module library to use from SAM (e.g., 'SandiaMod').
        inverter_lib : str
            Name of the inverter library to use from SAM (e.g., 'SandiaInverter').
        surface_tilt : float
            Tilt angle of the PV array surface in degrees.
        surface_azimuth : float
            Azimuth angle of the PV array surface in degrees.
        module : str, optional
            Name of the specific module to use from the module library.
        inverter : str, optional
            Name of the specific inverter to use from the inverter library.
        modules_per_string : int, optional
            Number of modules per string.
        strings_per_inverter : int, optional
            Number of strings per inverter.
        temp_lib : str, optional
            Name of the temperature model library to use.
        temp_model : str, optional
            Name of the specific temperature model to use.
        identifier : str, optional
            Unique identifier for the PV system.
        environment : Environment, optional
            Environment object providing weather data.
        """

        # Call to super class
        super(Photovoltaic, self).__init__(
            unit, environment
        )

        # Configure attributes
        self.identifier = identifier

        self.limit = 1.0

        # load some module and inverter specifications
        self.module_lib = pvlib.pvsystem.retrieve_sam(module_lib)
        self.inverter_lib = pvlib.pvsystem.retrieve_sam(inverter_lib)

        self.temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS[temp_lib][temp_model]

        if module:
            self.module = self.module_lib[module]

        if inverter:
            self.inverter = self.inverter_lib[inverter]

        self.location = Location(
            latitude=latitude,
            longitude=longitude,
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
                temperature_model_parameters=self.temperature_model_parameters,
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
        """Prepare time series data for the photovoltaic system.
        
        This method simulates the power generation of the PV system using the
        weather data provided by the environment object. It uses either the
        plane-of-array irradiance data or standard weather data depending on
        what's available in the environment.
        
        Returns
        -------
        pandas.DataFrame
            Time series of power generation in kW.
            
        Raises
        ------
        ValueError
            If the environment's PV data is empty.
        """
        if len(self.environment.pv_data) == 0:
            raise ValueError("self.environment.pv_data is empty.")

        if 'poa_global' in self.environment.pv_data.columns:
            
            self.modelchain.run_model_from_poa(
                data=self.environment.pv_data.loc[
                    self.environment.start: self.environment.end
                ],
            )
        else:
            self.modelchain.run_model(
                weather=self.environment.pv_data.loc[
                    self.environment.start: self.environment.end
                ],
            )

        timeseries = pd.DataFrame(
            self.modelchain.results.ac / 1000)  # convert to kW
        timeseries.rename(columns={0: self.identifier}, inplace=True)
        timeseries.set_index(timeseries.index, inplace=True)
        timeseries.index = pd.to_datetime(timeseries.index)

        self.timeseries = timeseries
        self.timeseries = self.timeseries.fillna(0)

        return timeseries

    def reset_time_series(self):
        """Reset the time series data for the photovoltaic system.
        
        This method resets the timeseries attribute to None.
        
        Returns
        -------
        None
            The reset timeseries value (None).
        """
        self.timeseries = None

        return self.timeseries

    # ===================================================================================
    # Controlling functions
    # ===================================================================================

    def limit_power_to(self, limit):
        """Limit the power output of the photovoltaic system.
        
        This method limits the power output of the PV system to a given percentage
        of its maximum capacity. It sets the limit attribute which is used in the
        value_for_timestamp method to scale the power output.
        
        Parameters
        ----------
        limit : float
            A value between 0 and 1 representing the percentage of maximum power.
            0 means no power output, 1 means full power output.
            
        Raises
        ------
        ValueError
            If the limit parameter is not between 0 and 1.
        """
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

    def value_for_timestamp(self, timestamp):
        """Get the power output value for a specific timestamp.
        
        This method overrides the value_for_timestamp method from the Component class.
        It returns the power output of the PV system at the given timestamp, scaled
        by the limit factor.
        
        Parameters
        ----------
        timestamp : int or str
            The timestamp for which to retrieve the value.
            If int, it's treated as an index in the timeseries.
            If str, it's treated as a datetime string in format 'YYYY-MM-DD hh:mm:ss'.
            
        Returns
        -------
        float
            The power output value at the given timestamp in kW.
            
        Raises
        ------
        ValueError
            If the timestamp is not of type int or str.
        """
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
        """Get observations for the photovoltaic system at a specific timestamp.
        
        This method overrides the observations_for_timestamp method from the Component class.
        It returns a dictionary with the electrical generation value at the given timestamp.
        
        Parameters
        ----------
        timestamp : int or str
            The timestamp for which to retrieve observations.
            If int, it's treated as an index in the timeseries.
            If str, it's treated as a datetime string in format 'YYYY-MM-DD hh:mm:ss'.
            
        Returns
        -------
        dict
            A dictionary with the key 'el_generation' and the corresponding power value.
            
        Raises
        ------
        ValueError
            If the timestamp is not of type int or str.
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
        """Select appropriate PV modules and inverter for the system.
        
        This method selects appropriate PV modules and an inverter based on the
        desired power output and module power range. It configures the PV system
        with the selected components.
        
        Parameters
        ----------
        min_module_power : float
            Minimum acceptable module power in W.
        max_module_power : float
            Maximum acceptable module power in W.
        pv_power : float
            Desired total PV system power in W.
        inverter_power_range : float
            Initial acceptable power range for inverter selection in W.
            
        Returns
        -------
        tuple
            A tuple containing:
            - modules_per_string (int): Number of modules per string
            - strings_per_inverter (int): Number of strings per inverter
            - module (pandas.Series): Selected module specifications
            - inverter (pandas.Series): Selected inverter specifications
        """
        power_lst = []
        # choose modules depending on module power
        for module in self.module_lib.columns:
            if (max_module_power
                > self.module_lib[module].Impo
                * self.module_lib[module].Vmpo
                    > min_module_power):
                power_lst.append(module)

        # pick random module from list
        module = power_lst[random.randint(0, (len(power_lst) - 1))]

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
        inverter_lst = []
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
            random.randint(0, (len(inverter_lst) - 1))]

        self.module = self.module_lib[module]
        self.inverter = self.inverter_lib[inverter]

        self.system = PVSystem(
            surface_tilt=self.surface_tilt,
            surface_azimuth=self.surface_azimuth,
            module_parameters=self.module,
            inverter_parameters=self.inverter,
            temperature_model_parameters=self.temperature_model_parameters,
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
            * self.modules_per_string
            * self.strings_per_inverter
        )

        # calculate area of pv modules
        self.modules_area = (self.module.Area
                             * self.modules_per_string
                             * self.strings_per_inverter)

        return (self.modules_per_string,
                self.strings_per_inverter,
                self.module,
                self.inverter)
