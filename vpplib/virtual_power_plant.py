# -*- coding: utf-8 -*-
"""
Info
----
This file contains the basic functionalities of the VirtualPowerPlant class.
This is the overall aggregator of the technologies used.

"""

import random
import pandas as pd

class VirtualPowerPlant(object):
    def __init__(self, name):

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

        # Configure attributes
        self.name = name

        self.components = {}

        self.buses_with_pv = []
        self.buses_with_hp = []
        self.buses_with_bev = []
        self.buses_with_wind = []
        self.buses_with_storage = []

    def add_component(self, component):

        """
        Info
        ----
        Component handling
        
        This function takes a component of type Component and appends it to the
        components of the virtual power plant.
        
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

        # Append component
        # self.components.append(component)
        self.components[component.identifier] = component

    def remove_component(self, component):

        """
        Info
        ----
        This function removes a component from the components of the virtual power
        plant.
        
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

        # Remove component
        self.components.pop(component)

    def export_components(self, environment):

        # dataframes for exporting timeseries and component values
        df_timeseries = pd.DataFrame(
            index=pd.date_range(start=environment.start,
                                end=environment.end,
                                freq=environment.time_freq,
                                name="time")
        )

        df_component_values = pd.DataFrame(index=[0])

        for component in self.components.keys():
            if '_pv' in component:
                df_component_values[self.components[component].identifier + "_kWp"] = (
                    self.components[component].module.Impo
                    * self.components[component].module.Vmpo
                    / 1000
                    * self.components[component].system.modules_per_string
                    * self.components[component].system.strings_per_inverter
                )
                df_timeseries[self.components[component].identifier] = self.components[component].timeseries * -1

            elif '_ees' in component:
                df_component_values[
                self.components[component].identifier + "_capacity"
                ] = self.components[component].capacity

                df_component_values[
                    self.components[component].identifier + "_power"
                    ] = self.components[component].max_power

                df_component_values[
                    self.components[component].identifier + "_charge_efficiency"
                    ] = self.components[component].charge_efficiency

                df_component_values[
                    self.components[component].identifier + "_discharge_efficiency"
                ] = self.components[component].discharge_efficiency

            elif '_wea' in component:
                df_timeseries[
                    self.components[component].identifier] = self.components[
                        component].timeseries * -1

                df_component_values[self.components[component].identifier + "_kW"] = (
                    self.components[component].ModelChain.power_plant.nominal_power
                    / 1000
                )

            elif '_bev' in component:
                df_component_values[
                    self.components[component].identifier + "_charger_kW"
                    ] = self.components[component].charging_power
                df_component_values[
                    self.components[component].identifier + "_battery_max"
                    ] = self.components[component].battery_max
                df_component_values[
                    self.components[component].identifier + "_efficiency"
                    ] = self.components[component].charge_efficiency
                df_component_values[
                    self.components[component].identifier + "_arrival_soc"
                    ] = random.uniform(self.components[component].battery_min,
                                       self.components[component].battery_max)

                df_timeseries[self.components[component].identifier] = self.components[
                    component].timeseries

            elif '_hp' in component:
                if '_tes' in component:
                    # Formula: E = m * cp * dT
                    df_component_values[
                        self.components[component].identifier
                        + "_therm_storage_capacity"] = (
                        self.components[component].mass
                        * self.components[component].cp
                        * (self.components[component].hysteresis * 2)  #dT
                        / 3600  # convert KJ to kW
                        )

                    df_component_values[
                        self.components[component].identifier
                        + "_efficiency_per_timestep"] =(
                        self.components[component].efficiency_per_timestep
                        )
                else:
                    df_component_values[
                        self.components[component].identifier + "_kW_el"
                        ] = self.components[component].el_power

                    df_timeseries[
                        self.components[component].identifier + "_thermal_energy_demand"
                        ] = self.components[component].user_profile.thermal_energy_demand

                    df_timeseries[
                        self.components[component].identifier
                        + "_cop"] = self.components[component].get_cop()

                    df_timeseries[self.components[component].identifier
                                  + "_cop"].interpolate(inplace=True)

            elif '_chp' in component:
                if '_tes' in component:
                    # Formula: E = m * cp * dT
                    df_component_values[
                        self.components[component].identifier
                        + "_therm_storage_capacity"] = (
                        self.components[component].mass
                        * self.components[component].cp
                        * (self.components[component].hysteresis * 2)  #dT
                        / 3600  # convert KJ to kW
                        )

                    df_component_values[
                        self.components[component].identifier
                        + "_efficiency_per_timestep"] =(
                        self.components[component].efficiency_per_timestep
                        )

                else:
                    df_timeseries[
                        self.components[component].identifier + "_thermal_energy_demand"
                        ] = self.components[component].user_profile.thermal_energy_demand

                    df_component_values[self.components[component].identifier
                                        + "_power_therm"] = self.components[
                                            component].th_power

                    df_component_values[self.components[component].identifier
                                        + "_kW_el"] = self.components[
                                            component].el_power

                    df_component_values[self.components[component].identifier
                                        + "_efficiency"] = self.components[
                                            component].overall_efficiency

        return df_component_values, df_timeseries

    def get_buses_with_components(
        self,
        net,
        method="random",
        pv_percentage=0,
        hp_percentage=0,
        bev_percentage=0,
        wind_percentage=0,
        storage_percentage=0,
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

        if method == "random":

            pv_amount = int(
                round(
                    (
                        len(net.bus.name[net.bus.type == "b"])
                        * (pv_percentage / 100)
                    ),
                    0,
                )
            )
            self.buses_with_pv = random.sample(
                list(net.bus.name[net.bus.type == "b"]), pv_amount
            )

            hp_amount = int(
                round(
                    (
                        len(net.bus.name[net.bus.type == "b"])
                        * (hp_percentage / 100)
                    ),
                    0,
                )
            )
            self.buses_with_hp = random.sample(
                list(net.bus.name[net.bus.type == "b"]), hp_amount
            )

            bev_amount = int(
                round(
                    (
                        len(net.bus.name[net.bus.type == "b"])
                        * (bev_percentage / 100)
                    ),
                    0,
                )
            )
            self.buses_with_bev = random.sample(
                list(net.bus.name[net.bus.type == "b"]), bev_amount
            )

            wind_amount = int(
                round(
                    (
                        len(net.bus.name[net.bus.type == "b"])
                        * (wind_percentage / 100)
                    ),
                    0,
                )
            )
            self.buses_with_wind = random.sample(
                list(net.bus.name[net.bus.type == "b"]), wind_amount
            )

            # Distribution of el storage is only done for houses with pv
            storage_amount = int(
                round(
                    (len(self.buses_with_pv) * (storage_percentage / 100)), 0
                )
            )
            self.buses_with_storage = random.sample(
                self.buses_with_pv, storage_amount
            )

            return (
                self.buses_with_pv,
                self.buses_with_hp,
                self.buses_with_bev,
                self.buses_with_wind,
                self.buses_with_storage,
            )

        elif method == "random_loadbus":

            bus_lst = []
            for bus in net.bus.index:
                if bus in list(net.load.bus):
                    bus_lst.append(net.bus.name[bus])

            pv_amount = int(round((len(bus_lst) * (pv_percentage / 100)), 0))
            self.buses_with_pv = random.sample(bus_lst, pv_amount)

            hp_amount = int(round((len(bus_lst) * (hp_percentage / 100)), 0))
            self.buses_with_hp = random.sample(bus_lst, hp_amount)

            bev_amount = int(round((len(bus_lst) * (bev_percentage / 100)), 0))
            self.buses_with_bev = random.sample(bus_lst, bev_amount)

            wind_amount = int(
                round((len(bus_lst) * (wind_percentage / 100)), 0)
            )
            self.buses_with_wind = random.sample(bus_lst, wind_amount)

            # Distribution of el storage is only done for houses with pv
            storage_amount = int(
                round(
                    (len(self.buses_with_pv) * (storage_percentage / 100)), 0
                )
            )
            self.buses_with_storage = random.sample(
                self.buses_with_pv, storage_amount
            )

            return (
                self.buses_with_pv,
                self.buses_with_hp,
                self.buses_with_bev,
                self.buses_with_wind,
                self.buses_with_storage,
            )

        else:
            raise ValueError("method ", method, " is invalid")

    def balance_at_timestamp(self, timestamp):

        """
        Info
        ----
        Simulation handling
    
        This function calculates the balance of all generation and consumption at a
        given timestamp and returns the result.
        
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

        # Create result variable
        result = 0

        # Iterate through all components
        for i in range(0, len(self.components)):

            # Get balance for component at timestamp
            balance = self.components[i].value_for_timestamp(timestamp)

            # Add balance to result
            result += balance

        # Return result
        return result
