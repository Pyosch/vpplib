# -*- coding: utf-8 -*-
"""
Info
----
This file contains the basic functionalities of the ElectricalEnergyStorage class.

"""

from .component import Component
import pandas as pd

from configparser import ConfigParser
from simses.main import SimSES
# from simses.config.simulation.storage_system_config import StorageSystemConfig


class ElectricalEnergyStorage(Component):
    def __init__(
        self,
        capacity,
        charge_efficiency,
        discharge_efficiency,
        max_power,
        max_c,
        unit,
        identifier=None,
        environment=None,
        user_profile=None,
        cost=None,
    ):
        """
        Info
        ----
        The class "ElectricalEnergyStorage" adds functionality to implement an
        electrical energy storage to the virtual power plant.


        Parameters
        ----------

        capacity [kWh]
        charge_efficiency [-] (between 0 and 1)
        discharge_efficiency [-] (between 0 and 1)
        max_power [kW]
        maxC [-] (between 0.5 and 1.2)

        Attributes
        ----------

        The stateOfCharge [kWh] is set to zero by default.

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
        super(ElectricalEnergyStorage, self).__init__(
            unit, environment, user_profile, cost
        )

        # Setup attributes
        self.identifier = identifier
        self.capacity = capacity
        self.charge_efficiency = charge_efficiency
        self.discharge_efficiency = discharge_efficiency
        self.max_power = max_power
        self.max_c = max_c  # factor between 0.5 and 1.2

        self.state_of_charge = 0
        self.residual_load = None
        self.timeseries = None

    def prepare_time_series(self):

        soc_lst = []
        res_load_lst = []
        for residual_load in self.residual_load:

            soc, res_load = self.operate_storage(residual_load=residual_load)
            soc_lst.append(soc)
            res_load_lst.append(res_load)

        # save state of charge and residual load
        self.timeseries = pd.DataFrame(
            data=soc_lst, columns=["state_of_charge"]
        )
        self.timeseries["residual_load"] = pd.DataFrame(data=res_load_lst)

        self.timeseries.index = self.residual_load.index

        return self.timeseries

    def reset_time_series(self):

        self.timeseries = None

        return self.timeseries

    def operate_storage(self, residual_load):
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

        if residual_load >= 0:
            return self.discharge(residual_load)

        elif residual_load < 0:
            return self.charge(residual_load)

    # ===================================================================================
    # Observation Functions
    # ===================================================================================

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

            state_of_charge, residual_load = self.timeseries.iloc[timestamp]

        elif type(timestamp) == str:

            state_of_charge, residual_load = self.timeseries.loc[timestamp]

        else:
            raise ValueError(
                "timestamp needs to be of type int or string. Stringformat: YYYY-MM-DD hh:mm:ss"
            )

        observations = {
            "state_of_charge": state_of_charge,
            "residual_load": residual_load,
            "max_power": self.max_power,
            "max_c": self.max_c,
        }

        return observations

    # ===================================================================================
    # Controlling functions
    # ===================================================================================

    def charge(self, charge):
        """
        Info
        ----
        This function takes the energy [kWh] that should be charged and the timebase as
        parameters. The timebase [minutes] is neccessary to calculate if the maximum
        power is exceeded.

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
        power = charge / (self.environment.timebase / 60)

        if power > self.max_power * self.max_c:
            charge = (self.max_power * self.max_c) * (
                self.environment.timebase / 60
            )
            # TODO: Process residual load when power > max_power * max_c

        if self.state_of_charge < self.capacity:
            # storage has not reached its max capacity

            self.state_of_charge += (
                charge
                * self.charge_efficiency
                * (self.environment.timebase / 60)
                * -1
            )

            # do not overcharge the storage
            if self.state_of_charge > self.capacity:
                charge = (
                    (self.capacity - self.state_of_charge)
                    / self.charge_efficiency
                    / (self.environment.timebase / 60)
                )
                self.state_of_charge = self.capacity

            else:
                charge = 0

        return self.state_of_charge, charge

    def discharge(self, charge):
        """
        Info
        ----
        This function takes the energy [kWh] that should be discharged and the timebase as
        parameters. The timebase [minutes] is neccessary to calculate if the maximum
        power is exceeded.

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

        power = charge / (self.environment.timebase / 60)

        if power > self.max_power * self.max_c:
            charge = (self.max_power * self.max_c) * (
                self.environment.timebase / 60
            )

        if self.state_of_charge > 0:
            # storage is not empty

            self.state_of_charge -= (
                charge
                * self.discharge_efficiency
                * (self.environment.timebase / 60)
            )

            # do not discharge below 0 kWh
            if self.state_of_charge < 0:
                charge = (
                    self.state_of_charge
                    / self.discharge_efficiency
                    / (self.environment.timebase / 60)
                    * -1
                )
                self.state_of_charge = 0

            else:
                charge = 0

        return self.state_of_charge, charge

    # ===================================================================================
    # Balancing Functions
    # ===================================================================================

    # Override balancing function from super class.
    def value_for_timestamp(self, timestamp):

        if type(timestamp) == int:

            return self.timeseries["residual_load"].iloc[timestamp]

        elif type(timestamp) == str:

            return self.timeseries["residual_load"].loc[timestamp]

        else:
            raise ValueError(
                "timestamp needs to be of type int or string. Stringformat: YYYY-MM-DD hh:mm:ss"
            )


class ElectricalEnergyStorageSimses(Component):
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
                 efficiency: float,
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
        self.efficiency = efficiency  # only used if model=='simple'
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
                                   self.environment.start)
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
        # self.simulation_config.set('BATTERY', 'START_SOH', str(self.soh_start))

        self.simses: SimSES = SimSES(
            str(result_path + '\\').replace('\\', '/'),
            simulation_name,
            do_simulation=True,
            do_analysis=True,
            simulation_config=self.simulation_config)
