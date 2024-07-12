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

try:
    import pysam.BatteryStateful as battery
except:
    import PySAM.BatteryStateful as battery
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

            return self.timeseries.iloc[timestamp]["residual_load"]

        elif type(timestamp) == str:

            return self.timeseries.loc[timestamp, "residual_load"]

        else:
            raise ValueError(
                "timestamp needs to be of type int or string. Stringformat: YYYY-MM-DD hh:mm:ss"
            )


class PySAMBatteryStateful(Component):
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
                 identifier=None,
                 result_path: str = None,
                 environment=None,
                 user_profile=None,
                 unit=None,
                 cost=None
                 ):

        # Call to super class
        super().__init__(
            unit, environment, user_profile, cost
        )
        
    def init_battery_stateful(self, nominal_energy,
                            nominal_voltage=500,
                            Vnom_default=3.600, resistance=0.0001,
                            Vfull=4.100, Vexp=4.050, Vnom=3.400,
                            Qfull=2.250, Qexp=0.040, Qnom=2.000,
                            C_rate=0.200, Vcut=2,
                            initial_SOC=50.0, maximum_SOC=95.0, minimum_SOC=5.0):

        self.battery_config = {
            # Control using current (0) or power (1) [0/1]
            "control_mode": 1,
            # Power at which to run battery [kW]
            # Required: True if control_mode=1
            # Set zero as initial, during operation this value is updated
            "input_power": 0,
            # Time step in hours [hr]
            # Required: True
            "dt_hr": 1/4,
            # From
            # available_chems = 0:'leadacid', 1:'lfpgraphite',
            #                     2:'nmcgraphite', 3:'lmolto'
            # From https://nrel-pysam.readthedocs.io/en/master/modules/BatteryStateful.html
            # Lead Acid (0), Li Ion (1), Vanadium Redox (2), Iron Flow (3) [0/1/2/3]
            #TODO
            # Check which one is right?
            "chem": 1,

            ### setup size ###
            # Nominal installed energy [kWh]
            # Required: True
            "nominal_energy": nominal_energy,
            # Nominal DC voltage [V]
            # Required: True
            "nominal_voltage": nominal_voltage,

            ### initial conditions ###
            # Initial state-of-charge [%]
            # Required: True
            "initial_SOC": initial_SOC,
            # Maximum allowed state-of-charge [%]
            # Required: True
            "maximum_SOC": maximum_SOC,
            # Minimum allowed state-of-charge [%]
            # Required: True
            "minimum_SOC": minimum_SOC,

            ### voltage parameters ###
            # Battery voltage input option [0/1]
            # Options: 0=Model,1=Table
            # Required: If not provided, assumed to be 0
            "voltage_choice": 0,
            # Default nominal cell voltage [V]
            # Required: True
            "Vnom_default": Vnom_default,
            # Internal resistance [Ohm]
            # Required: True
            "resistance": resistance,
            # Fully charged cell voltage [V]
            # Required: True if voltage_choice=0 & chem~2
            "Vfull": Vfull,
            # Cell voltage at end of exponential zone [V]
            # Required: True if voltage_choice=0 & chem~2
            "Vexp": Vexp,
            # Cell voltage at end of nominal zone [V]
            # Required: True if voltage_choice=0 & chem~2
            "Vnom": Vnom,
            # Fully charged cell capacity [Ah]
            # Required: True if voltage_choice=0 & chem~2
            "Qfull": Qfull,
            # Cell capacity at end of exponential zone [Ah]
            # Required: True if voltage_choice=0&chem~2
            "Qexp": Qexp,
            # Cell capacity at end of nominal zone [Ah]
            # Required: True if voltage_choice=0 & chem~2
            "Qnom": Qnom,
            # Rate at which voltage vs. capacity curve input
            # Required: True if voltage_choice=0 & chem~2
            "C_rate": C_rate,
            # Cell cutoff voltage [V]
            # Required: True if voltage_choice=0 & chem~2
            "Vcut": Vcut,

            ### thermal parameters ###
            # Battery mass [kg]
            # Required: True
            "mass": 507.000,
            # Battery surface area [m^2]
            # Required: True
            "surface_area": 2.018,
            # Battery specific heat capacity [J/KgK]
            # Required: True
            "Cp": 1004.000,
            # Heat transfer between battery and environment [W/m2K]
            # Required: True
            "h": 20.000,
            # Table with Temperature and Capacity % as columns [[[C,%]]]
            # Required: True if life_model=0
            "cap_vs_temp": [[-10, 60], [0, 80], [25, 1E+2], [40, 1E+2]],
            # Temperature of storage room [C]
            # Required: True
            "T_room_init": 20,

            ### cycling fade ###
            # Battery life model specifier [0/1/2]
            # Options: 0=calendar/cycle, 1=NMC, 2=LMO/LTO
            "life_model": 0,
            # Table with DOD %, Cycle #, and Capacity % columns [[[%, #, %]]]
            # Required: True if life_model=0
            "cycling_matrix": [[20, 0, 1E+2], [20, 5E+3, 80], [20, 1E+4, 60],
                                [80, 0, 1E+2], [80, 1E+3, 80], [80, 2E+3, 60]],

            ### calendar fade ###
            # calender_choice: 0=None,1=LithiumIonModel,2=InputLossTable
            # Required: True if life_model=0
            "calendar_choice": 1,
            # Calendar life model initial capacity cofficient
            # Required: True if life_model=0 & calendar_choice=1
            "calendar_q0": 1.020,
            # Calendar life model coefficient [1/sqrt(day)]
            # Required: True if life_model=0&calendar_choice=1
            "calendar_a": 0.003,
            # calendar_b: Calendar life model coefficient [K]
            # Required: True if life_model=0&calendar_choice=1
            "calendar_b": -7280.000,
            # Calendar life model coefficient [K]
            # Required: True if life_model=0&calendar_choice=1
            "calendar_c": 930.000,
            # calendar_matrix: Table with Day # and Capacity % columns [[[#, %]]]
            # Required if life_model=0 & calendar_choice=2
            "calendar_matrix": [[-3.1E+231]],
            # Loss power input option [0/1]
            # Options: 0=Monthly,1=TimeSeries
            # Required: If not provided, assumed to be 0
            "loss_choice": 0,
            # Battery system losses at each timestep [[kW]]
            # Required: If not provided, assumed to be 0
            "schedule_loss": [0],
            # Capacity replacement option
            # none (0), by capacity (1), or schedule (2) [0=none,1=capacity limit,2=yearly schedule]
            # Constraints: INTEGER,MIN=0,MAX=2
            # Required: If not provided, assumed to be 0
            "replacement_option": 0,
            # Capacity degradation at which to replace battery [%]
            # Required: True if replacement_option=1
            # "replacement_capacity": 80

            # Percentage of battery capacity to replace in each year [[%/year]]
            # Options: length <= analysis_period
            # Required: True if replacement_option=2
            # "replacement_schedule_percent": 0
            }
        
        self.battery_stateful = battery.new()

        for k, v in self.battery_config.items():
            self.battery_stateful.value(k, v)

        self.battery_stateful.setup()  # Setup parameters in simulation
        self.battery_stateful.execute()
        
        return self.battery_stateful, self.battery_config
    
    def operate_storage(self, load):
        """.

        Parameters
        ----------
        load : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        self.battery_stateful.Controls.input_power = load
        self.battery_stateful.execute()
        

        return self.battery_stateful.StatePack.SOC, self.battery_stateful.StatePack.P

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
            "max_chargeable_power": self.battery_stateful.StatePack.P_chargeable,
            "max_dischargeable_power": self.battery_stateful.StatePack.P_dischargeable,
            "max_capacity": self.battery_stateful.StatePack.Q_max,
            "capacity": self.battery_stateful.StatePack.Q,
        }

        return observations