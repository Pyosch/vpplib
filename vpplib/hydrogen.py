# -*- coding: utf-8 -*-
"""
Info
----
This file contains the basic functionalities of the ElectricalEnergyStorage class.

"""

from .component import Component
import pandas as pd
import datetime as dt
import time
from configparser import ConfigParser
from simses.main import SimSES
# from simses.config.simulation.storage_system_config import StorageSystemConfig


class ElectrolysisSimses(Component):
    """.

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
                 max_power: float,
                 capacity: float,
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

        self.max_power = max_power

        # Call to super class
        super().__init__(
            unit, environment, user_profile, cost
        )

        if soc_max < soc_min:
            raise ValueError('soc_max must be higher than soc_min!')
        self.identifier = identifier
        self.capacity = capacity
        self.soc_min = soc_min
        self.soc_max = soc_max
        self.soc_start = soc_start
        # P: power [kW], SOC: State of Charge [-]
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
        self.simulation_config.add_section('STORAGE_SYSTEM')

        self.simulation_config.set(
            'STORAGE_SYSTEM',
            'STORAGE_SYSTEM_AC',
            'system_1,'
            + str(abs(self.max_power * 1000))
            + ',600,'
            + 'acdc,no_housing,no_hvac')

        self.simulation_config.set(
            'STORAGE_SYSTEM',
            'ACDC_CONVERTER',
            'acdc,FixEfficiencyAcDcConverter')

        self.simulation_config.set('STORAGE_SYSTEM',
                                   'STORAGE_TECHNOLOGY',
                                   # Config uses Watt hours
                                   'storage_1, ' + \
                                   str(self.capacity * 1000)
                                   + ', lithium_ion,'
                                   + 'SonyLFP')  # str(self.storage_config.cell_type))

        self.simulation_config.add_section('BATTERY')
        self.simulation_config.set(
            'BATTERY', 'START_SOC', str(self.soc_start))
        self.simulation_config.set('BATTERY', 'MIN_SOC', str(self.soc_min))
        self.simulation_config.set('BATTERY', 'MAX_SOC', str(self.soc_max))
        # Following line has something to do with aging not soc... #TODO
        self.simulation_config.set(
            'BATTERY', 'START_SOH', str(1.0))  # self.soh_start

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

            return self.timeseries["ac_power"].iloc[timestamp]

        elif type(timestamp) == str:

            return self.timeseries["ac_power"].loc[timestamp]

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
            "max_power": self.max_power,
            "max_capacity": self.capacity * self.soc_max,
        }

        return observations
