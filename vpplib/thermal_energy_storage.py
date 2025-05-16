# -*- coding: utf-8 -*-
"""
Thermal Energy Storage Module
----------------------------
This module contains the ThermalEnergyStorage class which models a thermal energy storage system
in a virtual power plant environment.

The thermal storage system maintains a target temperature within a specified hysteresis range
and accounts for thermal energy losses over time. It can be used in conjunction with thermal
energy generators like heat pumps, heating rods, or combined heat and power units.
"""

import pandas as pd
from vpplib.component import Component


class ThermalEnergyStorage(Component):
    """
    A class representing a thermal energy storage component in a virtual power plant.
    
    The thermal energy storage maintains a temperature within a specified range around a target
    temperature. It accounts for thermal energy losses over time and can signal when it needs
    to be loaded (heated) based on its current temperature relative to the target temperature.
    
    Attributes
    ----------
    identifier : str, optional
        Unique identifier for the thermal energy storage
    target_temperature : float
        Target temperature in degrees Celsius that the storage aims to maintain
    current_temperature : float
        Current temperature of the storage in degrees Celsius
    min_temperature : float
        Minimum allowable temperature in degrees Celsius
    hysteresis : float
        Temperature range around the target temperature that defines the control band
    mass : float
        Mass of the storage medium in kg
    cp : float
        Specific heat capacity of the storage medium in J/(kg·K)
    state_of_charge : float
        Current thermal energy content of the storage in Joules
    thermal_energy_loss_per_day : float
        Fraction of thermal energy lost per day (e.g., 0.1 for 10% loss)
    efficiency_per_timestep : float
        Calculated efficiency factor applied at each timestep to account for thermal losses
    needs_loading : bool
        Flag indicating whether the storage needs to be loaded (heated)
    timeseries : pandas.DataFrame
        Time series of storage temperature for the simulation period
    """
    
    def __init__(
        self,
        target_temperature,
        min_temperature,
        hysteresis,
        mass,
        cp,
        thermal_energy_loss_per_day,
        unit,
        identifier=None,
        environment=None,
    ):
        """
        Initialize a ThermalEnergyStorage object.
        
        Parameters
        ----------
        target_temperature : float
            Target temperature in degrees Celsius that the storage aims to maintain
        min_temperature : float
            Minimum allowable temperature in degrees Celsius
        hysteresis : float
            Temperature range around the target temperature that defines the control band
        mass : float
            Mass of the storage medium in kg
        cp : float
            Specific heat capacity of the storage medium in J/(kg·K)
        thermal_energy_loss_per_day : float
            Fraction of thermal energy lost per day (e.g., 0.1 for 10% loss)
        unit : str
            Unit of energy measurement (e.g., "kWh")
        identifier : str, optional
            Unique identifier for the thermal energy storage
        environment : Environment, optional
            Environment object containing simulation parameters and weather data
            
        Notes
        -----
        The storage is initialized at (target_temperature - hysteresis), which is the
        lower threshold that triggers loading. The state of charge is calculated based
        on the initial temperature, mass, and specific heat capacity.
        """

        # Call to super class
        super(ThermalEnergyStorage, self).__init__(
            unit, environment
        )

        # Configure attributes
        self.identifier = identifier
        self.target_temperature = target_temperature
        self.current_temperature = target_temperature - hysteresis
        self.min_temperature = min_temperature
        self.timeseries = pd.DataFrame(
            columns=["temperature"],
            index=pd.date_range(
                start=self.environment.start,
                end=self.environment.end,
                freq=self.environment.time_freq,
                name="time",
            ),
        )
        self.hysteresis = hysteresis
        self.mass = mass
        self.cp = cp
        self.state_of_charge = mass * cp * (self.current_temperature + 273.15)
        # Aus Datenblättern ergibt sich, dass ein Wärmespeicher je Tag rund 10%
        # Bereitschaftsverluste hat (ohne Rohrleitungen!!)
        self.thermal_energy_loss_per_day = thermal_energy_loss_per_day
        self.efficiency_per_timestep = 1 - (
            thermal_energy_loss_per_day
            / (24 * (60 / self.environment.timebase))
        )
        self.needs_loading = None

    def operate_storage(self, timestamp, thermal_energy_generator):
        """
        Operate the thermal energy storage for a specific timestamp.
        
        This method controls the thermal energy generator based on the storage's needs,
        updates the state of charge and temperature of the storage, and logs the results.
        
        Parameters
        ----------
        timestamp : str or pandas.Timestamp
            The timestamp for which to operate the storage
        thermal_energy_generator : Component
            A thermal energy generator component (e.g., heat pump, heating rod, CHP)
            that can be controlled to heat the storage
            
        Returns
        -------
        tuple
            A tuple containing:
            - current_temperature (float): The updated temperature of the storage in °C
            - el_load (float): The electrical load of the thermal energy generator
            
        Notes
        -----
        The method performs the following steps:
        1. Control the thermal energy generator based on storage needs
        2. Calculate the energy balance (demand vs. production)
        3. Update the state of charge accounting for energy balance and losses
        4. Calculate the new temperature
        5. Log the temperature in the timeseries
        6. Log the generator's operation
        """
        if self.get_needs_loading():
            thermal_energy_generator.ramp_up(timestamp)
        else:
            thermal_energy_generator.ramp_down(timestamp)

        thermal_energy_demand = thermal_energy_generator.thermal_energy_demand.loc[
            timestamp, "thermal_energy_demand"
        ]
        observation = thermal_energy_generator.observations_for_timestamp(
            timestamp
        )
        thermal_production = observation["thermal_energy_output"]

        # Formula: E = m * cp * T
        #     <=> T = E / (m * cp)
        self.state_of_charge -= (
            (thermal_energy_demand - thermal_production)
            * 1000  # kWh to Wh ?? Why?
            / (60 / self.environment.timebase)
        )
        self.state_of_charge *= self.efficiency_per_timestep
        self.current_temperature = (
            self.state_of_charge
#            * 3600  # kWh to KJ
            / (self.mass * self.cp)
        ) - 273.15

        if thermal_energy_generator.is_running:
            el_load = observation["el_demand"]
        else:
            el_load = 0

        self.timeseries.loc[timestamp, "temperature"] = self.current_temperature

        # log timeseries of thermal_energy_generator_class:
        thermal_energy_generator.log_observation(observation, timestamp)

        return self.current_temperature, el_load

    def get_needs_loading(self):
        """
        Determine if the thermal energy storage needs to be loaded (heated).
        
        This method checks the current temperature against the target temperature
        and hysteresis band to determine if the storage needs heating. It also
        verifies that the temperature hasn't fallen below the minimum allowable value.
        
        Returns
        -------
        bool
            True if the storage needs to be loaded (heated), False otherwise
            
        Raises
        ------
        ValueError
            If the current temperature falls below the minimum allowable temperature,
            indicating insufficient thermal energy production
            
        Notes
        -----
        The method implements hysteresis control:
        - If temperature <= (target - hysteresis), set needs_loading to True
        - If temperature >= (target + hysteresis), set needs_loading to False
        - Otherwise, maintain the previous state
        """
        if self.current_temperature <= (
            self.target_temperature - self.hysteresis
        ):
            self.needs_loading = True

        if self.current_temperature >= (
            self.target_temperature + self.hysteresis
        ):
            self.needs_loading = False

        if self.current_temperature < self.min_temperature:
            raise ValueError(
                "Thermal energy production to low to maintain "
                + "heat storage temperature!"
            )

        return self.needs_loading

    def value_for_timestamp(self, timestamp):
        """
        Get the energy value for a specific timestamp.
        
        This method is required by the Component interface but is not implemented
        for the ThermalEnergyStorage class as it doesn't directly contribute to
        the electrical balance of the virtual power plant.
        
        Parameters
        ----------
        timestamp : str, int, or pandas.Timestamp
            The timestamp for which to retrieve the value
            
        Raises
        ------
        NotImplementedError
            This method must be implemented by child classes that need to
            contribute to the electrical balance
            
        Notes
        -----
        In the context of a virtual power plant, this method typically returns:
        - Positive values for loads (consumption)
        - Negative values for generation
        """
        raise NotImplementedError(
            "value_for_timestamp needs to be implemented by child classes!"
        )

    def observations_for_timestamp(self, timestamp):
        """
        Get detailed observations for a specific timestamp.
        
        This method returns a dictionary of key-value pairs representing
        the state of the thermal energy storage at the specified timestamp.
        
        Parameters
        ----------
        timestamp : str, int, or pandas.Timestamp
            The timestamp for which to retrieve observations
            
        Returns
        -------
        dict
            An empty dictionary in the base implementation. Child classes
            should override this to provide relevant observations.
            
        Notes
        -----
        For thermal energy storage, relevant observations might include:
        - current_temperature
        - state_of_charge
        - needs_loading
        
        This base implementation returns an empty dictionary as the
        ThermalEnergyStorage class doesn't implement specific observations.
        """
        return {}

    def prepare_time_series(self):
        """
        Prepare the time series data for the simulation period.
        
        This method initializes the timeseries DataFrame with a temperature column
        and appropriate time index based on the environment settings.
        
        Returns
        -------
        pandas.DataFrame
            The initialized timeseries DataFrame with a temperature column
            
        Notes
        -----
        This method currently has the same implementation as reset_time_series.
        It may be extended in future versions to include additional preparation steps.
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
        Reset the time series data to its initial state.
        
        This method clears all recorded temperature data and reinitializes
        the timeseries DataFrame with the appropriate time index.
        
        Returns
        -------
        pandas.DataFrame
            The reset timeseries DataFrame with a temperature column
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

    def get_energy_loss(self):
        """
        Calculate the energy loss of the thermal energy storage.
        
        This method calculates the thermal energy loss based on the difference
        between the target temperature and current temperature, the thermal
        properties of the storage medium, and the daily loss rate.
        
        Returns
        -------
        float
            The calculated energy loss in the same units as used for state_of_charge
            
        Notes
        -----
        The energy loss is calculated as:
        energy_loss = mass * specific_heat_capacity * temperature_difference * daily_loss_rate
        
        This represents the amount of energy needed to compensate for thermal losses
        and maintain the target temperature.
        """
        energy_loss = self.mass * self.cp * (self.target_temperature - self.current_temperature) * self.thermal_energy_loss_per_day
        return energy_loss
