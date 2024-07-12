# -*- coding: utf-8 -*-
"""
Info
----
This file contains the basic functionalities of the ElectricalEnergyStorage class.

"""

from .component import Component
import pandas as pd
import numpy as np
import math
import datetime as dt
import time
from configparser import ConfigParser
from simses.main import SimSES

import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.optimize import fsolve

class ElectrolysisSimses(Component):
    """.

    Info
    ----
    Standard values are taken from
    "simses/simulation/system_tests/configs/simulation.test_23.ini"

    Parameters
    ----------
    max_power : float
        nominal power in kW
    capacity : float
        nominal energy capacity in kWh
    soc : float
        initial state of charge
        between 0.0 and 1!
    soc_min: float
        minimal state of charge
        between 0.0 and 1!
    soc_max: float
        maximal state of charge
        between 0.0 and 1!
    efficiency: float
        charging/discharging efficiency, only used when model == 'simple'
    identifier : str
        name of the Energy Storage System
    model : str
        model to use for the Energy Storage simulation.
        The default is 'simple'.
    result_path : str, optional
        DESCRIPTION. The default is None
    environment: class,
        Instance fo the Environment class containing information about
        time dependent variables.
    user_profile : TYPE, optional
        DESCRIPTION. The default is None.
    unit : TYPE, optional
        DESCRIPTION. The default is None.
    cost : TYPE, optional
        DESCRIPTION. The default is None.

    Raises
    ------
    ValueError
        If soc_min > soc_max.
    """

    def __init__(self,
                 electrolyzer_power: float,
                 fuelcell_power: float,
                 capacity: float,
                 tank_size: float,
                 soc_start: float,
                 soc_min: float,
                 soc_max: float,
                 identifier=None,
                 result_path: str = None,
                 environment=None,
                 user_profile=None,
                 unit=None,
                 cost=None
                 ):

        # self.max_power = max_power

        # Call to super class
        super().__init__(
            unit, environment, user_profile, cost
        )

        if soc_max < soc_min:
            raise ValueError('soc_max must be higher than soc_min!')
        self.identifier = identifier

        if electrolyzer_power:
            self.electrolyzer_power = electrolyzer_power * 1000
        else:
            self.electrolyzer_power = 0

        if fuelcell_power:
            self.fuelcell_power = fuelcell_power * 1000
        else:
            self.fuelcell_power = 0

        if capacity:
            self.capacity = capacity * 1000
        else:
            self.capacity = 0

        self.tank_size = tank_size
        self.soc_min = soc_min
        self.soc_max = soc_max
        self.soc_start = soc_start
        self.df = pd.DataFrame(columns=['P', 'SOC'],
                               index=pd.date_range(
                                   start=self.environment.start,
                                   end=self.environment.end,
                                   freq=self.environment.time_freq))

        if self.identifier is None:
            simulation_name = 'NoName'
        else:
            simulation_name = self.identifier  # TODO: Add timestamp (?)
        self.simulation_config: ConfigParser = ConfigParser()
        # self.storage_config = StorageSystemConfig(self.simulation_config)

        # GENERAL config from "simses-master\simses\commons\config\simulation"
        self.simulation_config.add_section('GENERAL')
        # SimSES needs step size in sec
        self.simulation_config.set('GENERAL', 'TIME_STEP',
                                   str(self.environment.timebase * 60))
        self.simulation_config.set('GENERAL', 'START',
                                   str(dt.datetime.strptime(
                                       self.environment.start,
                                       "%Y-%m-%d %H:%M:%S")
                                       - dt.timedelta(
                                       minutes=self.environment.timebase*9))
                                   )
        self.simulation_config.set('GENERAL', 'END',
                                   self.environment.end)
        # possible extensions to GENERAL:
        # self.simulation_config.set('GENERAL', 'LOOP', 1)
        # self.simulation_config.set('GENERAL', 'EXPORT_DATA', True)
        # self.simulation_config.set('GENERAL', 'EXPORT_INTERVAL', 1)

        # Config for ELECTROLYZER
        self.simulation_config.add_section('ELECTROLYZER')

        # According to battery config, EOL is defined btwn. 0-1
        self.simulation_config.set('ELECTROLYZER',
                                   'EOL',
                                   str(0.8))

        self.simulation_config.set('ELECTROLYZER', 'PRESSURE_CATHODE', str(20))
        self.simulation_config.set('ELECTROLYZER', 'PRESSURE_ANODE', str(2))
        self.simulation_config.set('ELECTROLYZER', 'TOTAL_PRESSURE', str(20))
        self.simulation_config.set('ELECTROLYZER', 'TEMPERATURE', str(75))

        # Config for FUEL_CELL
        self.simulation_config.add_section('FUEL_CELL')

        # According to battery config, EOL is defined btwn. 0-1
        self.simulation_config.set('FUEL_CELL',
                                   'EOL',
                                   str(0.8))

        self.simulation_config.set('FUEL_CELL', 'PRESSURE_CATHODE', str(20))
        self.simulation_config.set('FUEL_CELL', 'PRESSURE_ANODE', str(2))
        self.simulation_config.set('FUEL_CELL', 'TEMPERATURE', str(75))

        # Config for the hydrogen storage
        self.simulation_config.add_section('HYDROGEN')
        self.simulation_config.set(
            'HYDROGEN', 'START_SOC', str(self.soc_start))
        self.simulation_config.set('HYDROGEN', 'MIN_SOC', str(self.soc_min))
        self.simulation_config.set('HYDROGEN', 'MAX_SOC', str(self.soc_max))

        # Config for STORAGE_SYSTEM, the overall system settings
        self.simulation_config.add_section('STORAGE_SYSTEM')

        # Config AC
        self.simulation_config.set('STORAGE_SYSTEM', 'STORAGE_SYSTEM_AC',
                                   'system_1,'
                                   # 5500.0
                                   + str(abs(self.electrolyzer_power))
                                   + ',333,'
                                   + 'fix,no_housing,no_hvac')

        # Config DC
        self.simulation_config.set('STORAGE_SYSTEM', 'STORAGE_SYSTEM_DC',
                                   'system_1,fix,hydrogen')

        # Config ACDC converter
        self.simulation_config.set(
            'STORAGE_SYSTEM',
            'ACDC_CONVERTER',
            'fix,FixEfficiencyAcDcConverter')

        # Config DCDC converter
        self.simulation_config.set(
            'STORAGE_SYSTEM',
            'DCDC_CONVERTER',
            'fix,FixEfficiencyDcDcConverter')

        self.simulation_config.set('STORAGE_SYSTEM',
                                   'STORAGE_TECHNOLOGY',
                                   # Config uses Watt hours
                                   'hydrogen, ' + \
                                   str(self.capacity)
                                   + ',hydrogen,'
                                   + 'NoFuelCell,'
                                   + str(abs(self.fuelcell_power))+','
                                   + 'PemElectrolyzer,'
                                   + str(abs(self.electrolyzer_power))
                                   + ','
                                   + 'PressureTank,'
                                   + str(self.tank_size)  # '700'
                                   )

        self.simses: SimSES = SimSES(
            str(result_path + '\\').replace('\\', '/'),
            simulation_name,
            do_simulation=True,
            do_analysis=True,
            simulation_config=self.simulation_config)

    def operate_storage(self, timestep, load):
        """.

        Parameters
        ----------
        timestep : TYPE
            DESCRIPTION.
        load : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        self.simses.run_one_simulation_step(
            time.mktime(
                dt.datetime.strptime(str(timestep),
                                     "%Y-%m-%d %H:%M:%S").timetuple()
            ),
            (load * -1000)
        )

        return (self.simses.state.soc,
                (self.simses.state.get(
                    self.simses.state.AC_POWER_DELIVERED) / 1000))

    def prepare_time_series(self):
        """.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        soc_lst = list()
        ac_lst = list()

        for timestep in pd.date_range(start=self.environment.start,
                                      end=self.environment.end,
                                      freq=self.environment.time_freq):

            soc, ac = self.operate_storage(
                timestep,
                self.residual_load[timestep]
            )

            soc_lst.append(soc)
            ac_lst.append(ac)

        self.timeseries = pd.DataFrame(
            {"state_of_charge": soc_lst,
             "ac_power": ac_lst},
            index=pd.date_range(start=self.environment.start,
                                end=self.environment.end,
                                freq=self.environment.time_freq)
        )

        return self.timeseries

    def reset_time_series(self):

        self.timeseries = None

        return self.timeseries

    def value_for_timestamp(self, timestamp):

        if type(timestamp) == int:

            return self.timeseries.iloc[timestamp]["ac_power"]

        elif type(timestamp) == str:

            return self.timeseries.loc[timestamp, "ac_power"]

        else:
            raise ValueError(
                "timestamp needs to be of type int or string."
                + " Stringformat: YYYY-MM-DD hh:mm:ss"
            )

    def observations_for_timestamp(self, timestamp):
        """.

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

            state_of_charge, ac_power = self.timeseries.iloc[timestamp]

        elif type(timestamp) == str:

            state_of_charge, ac_power = self.timeseries.loc[timestamp]

        else:
            raise ValueError(
                "timestamp needs to be of type int or string."
                + " Stringformat: YYYY-MM-DD hh:mm:ss"
            )

        observations = {
            "state_of_charge": state_of_charge,
            "ac_power": ac_power,
            "electrolyzer_power": self.electrolyzer_power,
            "fuelcell_power": self.fuelcell_power,
            "max_capacity": self.capacity * self.soc_max,
        }

        return observations