# -*- coding: utf-8 -*-
"""
Info
----
This file contains the basic functionalities of the VirtualPowerPlant class.
This is the overall aggregator of the technologies used.

"""

import random
import pandas as pd
import sqlite3
from tqdm import tqdm

from vpplib.photovoltaic import Photovoltaic
from vpplib.battery_electric_vehicle import BatteryElectricVehicle
from vpplib.heat_pump import HeatPump
from vpplib.electrical_energy_storage import ElectricalEnergyStorage
from vpplib.wind_power import WindPower
from vpplib.combined_heat_and_power import CombinedHeatAndPower
from vpplib.thermal_energy_storage import ThermalEnergyStorage

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

        """
        Info
        ----
        This function returns two DataFrames with the component values and
        the timeseries of the components of the virtual power plant.
        
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

        # dataframes for exporting timeseries and component values
        df_timeseries = pd.DataFrame(
            index=pd.date_range(start=environment.start,
                                end=environment.end,
                                freq=environment.time_freq,
                                name="time")
        )

        df_component_values = pd.DataFrame(index=[0])

        print("Exporting components:")
        for component in tqdm(self.components.keys()):
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
                #TODO: timeseries vereinheitlichen!!
                df_timeseries[self.components[component].identifier] = self.components[
                    component].timeseries["car_charger"]

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


    def export_component_values(self):

        """
        Info
        ----
        This function returns two DataFrames with the component values and
        the timeseries of the components of the virtual power plant.
        
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

        # dataframe for exporting component values

        df_component_values = pd.DataFrame(
            columns=("name",
                     "technology",
                     "bus",
                     "arrival_soc",
                     "capacity_kWh",
                     "power_kW",
                     "th_power_kW",
                     "efficiency_el",
                     "efficiency_th"))

        print("Exporting component values:")
        
        for component in tqdm(self.components.keys()):
            if '_pv' in component:
                df_component_values = df_component_values.append(
                    {"name": component,
                     "technology": "pv",
                     "bus": self.components[component].user_profile.bus,
                     "power_kW": (self.components[component].module.Impo
                     * self.components[component].module.Vmpo
                     / 1000
                     * self.components[component].system.modules_per_string
                     * self.components[component].system.strings_per_inverter)},
                    ignore_index=True)

            elif '_ees' in component:
                df_component_values = df_component_values.append(
                    {"name": component,
                     "technology": "ees",
                     "bus": self.components[component].user_profile.bus,
                     "capacity_kWh": self.components[component].capacity,
                     "power_kW": self.components[component].max_power,
                     "efficiency_el": self.components[component].charge_efficiency},
                    ignore_index=True)


            elif '_wea' in component:
                df_component_values = df_component_values.append(
                    {"name": component,
                     "technology": "wea",
                     "bus": self.components[component].user_profile.bus,
                     "power_kW": self.components[component].ModelChain.power_plant.nominal_power
                    / 1000},
                    ignore_index=True)


            elif '_bev' in component:
                df_component_values = df_component_values.append(
                    {"name": component,
                     "technology": "bev",
                     "bus": self.components[component].user_profile.bus,
                     "arrival_soc": random.uniform(
                         self.components[component].battery_min,
                         self.components[component].battery_max
                         ),
                     "capacity_kWh": self.components[component].battery_max,
                     "power_kW": self.components[component].charging_power,
                     "efficiency_el": self.components[component].charge_efficiency},
                    ignore_index=True)

            elif '_hp' in component:
                df_component_values = df_component_values.append(
                    {"name": component,
                     "technology": "hp",
                     "bus": self.components[component].user_profile.bus,
                     "power_kW": self.components[component].el_power},
                    ignore_index=True)

            elif '_tes' in component:
                # Formula: E = m * cp * dT
                df_component_values = df_component_values.append(
                    {"name": component,
                     "technology": "tes",
                     "bus": self.components[component].user_profile.bus,
                     "capacity_kWh": (self.components[component].mass
                            * self.components[component].cp
                            * (self.components[component].hysteresis * 2)  #dT
                            / 3600),  # convert KJ to kW,
                     "efficiency_th": self.components[component].efficiency_th},
                    ignore_index=True)

            elif '_chp' in component:
                df_component_values = df_component_values.append(
                    {"name": component,
                     "technology": "chp",
                     "bus": self.components[component].user_profile.bus,
                     "power_kW": self.components[component].el_power,
                     "th_power_kW": self.components[component].th_power,
                     "efficiency_el": self.components[component].efficiency_el,
                     "efficiency_th": self.components[component].efficiency_th},
                    ignore_index=True)

            elif '_hr' in component:
                df_component_values = df_component_values.append(
                    {"name": component,
                     "technology": "hr",
                     "bus": self.components[component].user_profile.bus,
                     "th_power_kW": self.components[component].el_power, #TODO: change to power_kW after the Project
                     "efficiency_th": self.components[component].efficiency}, #TODO: Change to el_efficiency after the Project
                    ignore_index=True)


        return df_component_values

    def export_component_timeseries(self):

        ts_dict = dict()

        #List to catch components without timeseries. Usually only tes
        no_timeseries_lst = list()

        print("Export component timeseries:")
        for component in self.components:

            if isinstance(self.components[component], (Photovoltaic)):

                ts_dict[component] = self.components[component].timeseries.loc[:, component]
                
            elif isinstance(self.components[component], (WindPower)):

                ts_dict[component] = self.components[component].timeseries


            elif isinstance(self.components[component], BatteryElectricVehicle):

                ts_dict[component] = self.components[component].timeseries.loc[:,'car_charger']

            elif isinstance(self.components[component], HeatPump):
                    
                ts_dict[component] = self.components[component].timeseries.loc[:,'el_demand']

            elif isinstance(self.components[component], CombinedHeatAndPower):
                    
                ts_dict[component] = self.components[component].timeseries.loc[:,'el_demand']
                
            elif isinstance(self.components[component], ElectricalEnergyStorage):
                        
                    ts_dict[component] = self.components[component].timeseries.loc[:,'residual_load']

            elif isinstance(self.components[component], ThermalEnergyStorage):
                # Thermal energy storage has no timeseries
                no_timeseries_lst.append(component)

            else:
                no_timeseries_lst.append(component)

        df_timeseries = pd.DataFrame(ts_dict)

        return df_timeseries, no_timeseries_lst


    def export_components_to_sql(self, name = "export"):

        """
        Info
        ----
        This function exports the component values and the timeseries of the
        components of the virtual power plant to a sql database.
        
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

        # create connection
        conn = sqlite3.connect((r'./Results/' + name + '.sqlite'))

        # create curser object
        c = conn.cursor()

        # Create table
        c.execute("CREATE TABLE component_values ("
                  +"name, "
                  +"technology, "
                  +"bus, "
                  +"arrival_soc, "
                  +"capacity_kWh, "
                  +"power_kW, "
                  +"th_power_kW, "
                  +"efficiency_el ,"
                  +"efficiency_th)")

        # Create table
        c.execute("CREATE TABLE timeseries ("
                  +"time, "
                  +"name, "
                  +"cop, "
                  +"feed_in, "
                  +"th_energy)")

        # Insert data of the components into the component_values table
        print("Exporting components to sql:")
        for component in tqdm(self.components.keys()):

            if '_pv' in component:
                c.execute("INSERT INTO component_values "
                          +"(name, "
                          +"technology, "
                          +"bus, "
                          +"power_kW) "
                          +"VALUES (?, ?, ?, ?)",
                          (component,
                           "pv",
                           self.components[component].user_profile.bus,
                           (self.components[component].module.Impo
                            * self.components[component].module.Vmpo
                            / 1000
                            * self.components[component].system.modules_per_string
                            * self.components[component].system.strings_per_inverter
                            )
                           )
                          )

                conn.commit()

            elif '_ees' in component:
                c.execute("INSERT INTO component_values "
                          +"(name, "
                          +"technology, "
                          +"bus, "
                          +"capacity_kWh, "
                          +"power_kW, "
                          +"efficiency_el) "
                          +"VALUES (?, ?, ?, ?, ?, ?)",
                          (component,
                           "ees",
                           self.components[component].user_profile.bus,
                           self.components[component].capacity,
                           self.components[component].max_power,
                           self.components[component].charge_efficiency)
                          )

                conn.commit()

            elif '_wea' in component:
                c.execute("INSERT INTO component_values "
                          +"(name, "
                          +"technology, "
                          +"bus, "
                          +"power_kW) "
                          +"VALUES (?, ?, ?, ?)",
                          (component,
                           "wea",
                           self.components[component].user_profile.bus, # used to be: component[:-4],
                           (self.components[
                               component].ModelChain.power_plant.nominal_power
                               / 1000)
                           )
                          )

                conn.commit()

            elif '_bev' in component:
                c.execute("INSERT INTO component_values "
                          +"(name, "
                          +"technology, "
                          +"bus, "
                          +"power_kW, "
                          +"capacity_kWh, "
                          +"efficiency_el, "
                          +"arrival_soc) "
                          +"VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (component,
                           "bev",
                           self.components[component].user_profile.bus,
                           self.components[component].charging_power,
                           self.components[component].battery_max,
                           self.components[component].charge_efficiency,
                           random.uniform(self.components[component].battery_min,
                                        self.components[component].battery_max)
                           )
                          )

                conn.commit()

            elif '_hp' in component:
                c.execute("INSERT INTO component_values "
                          +"(name, "
                          +"technology, "
                          +"bus, "
                          +"power_kW) "
                          +"VALUES (?, ?, ?, ?)",
                          (component,
                           "hp",
                           self.components[component].user_profile.bus,
                           self.components[component].el_power
                           )
                          )

                conn.commit()

            elif '_chp' in component:
                c.execute("INSERT INTO component_values "
                          +"(name, "
                          +"technology, "
                          +"bus, "
                          +"power_kW, "
                          +"th_power_kW, "
                          +"efficiency_el, "
                          +"efficiency_th) "
                          +"VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (component,
                           "chp",
                           self.components[component].user_profile.bus,
                           self.components[component].el_power,
                           self.components[component].th_power,
                           self.components[component].efficiency_el,
                           self.components[component].efficiency_th
                           )
                          )

                conn.commit()

            elif '_hr' in component:
                c.execute("INSERT INTO component_values "
                          +"(name, "
                          +"technology, "
                          +"bus, "
                          +"th_power_kW, "
                          +"efficiency_th) "
                          +"VALUES (?, ?, ?, ?, ?)",
                          (component,
                           "hr",
                           self.components[component].user_profile.bus,
                           self.components[component].el_power,
                           self.components[component].efficiency
                           )
                          )
    
                conn.commit()

            elif '_tes' in component:
                # Formula: E = m * cp * dT
                c.execute("INSERT INTO component_values "
                          +"(name, "
                          +"technology, "
                          +"bus, "
                          +"capacity_kWh, "
                          +"efficiency_th) "
                          +"VALUES (?, ?, ?, ?, ?)",
                          (component,
                           "tes",
                           self.components[component].user_profile.bus,
                           (self.components[component].mass
                            * self.components[component].cp
                            * (self.components[component].hysteresis * 2)  #dT
                            / 3600),  # convert KJ to kW
                           self.components[component].efficiency_th
                           )
                          )

                conn.commit()

        # Save (commit) the changes
        conn.commit()

        # Save timeseries of each component for each timestep to the table timeseries
        # Log components which do not have a timeseries
        no_timeseries_lst = list()

        for idx in self.components[next(iter(self.components.keys()))].timeseries.index:
            for component in self.components.keys():

                if '_pv' in component:

                    c.execute("INSERT INTO timeseries "
                              +"(time, "
                              +"name, "
                              +"feed_in) "
                              +"VALUES (?, ?, ?)",
                              (str(idx),
                               component,
                               (self.components[component].value_for_timestamp(str(idx)) * -1)
                               )
                              )

                    conn.commit()

                elif '_wea' in component:
                    c.execute("INSERT INTO timeseries "
                              +"(time, "
                              +"name, "
                              +"feed_in) "
                              +"VALUES (?, ?, ?)",
                              (str(idx),
                               component,
                               (self.components[component].value_for_timestamp(str(idx)) * -1)
                               )
                              )

                    conn.commit()


                elif '_bev' in component:
                    c.execute("INSERT INTO timeseries "
                              +"(time, "
                              +"name, "
                              +"feed_in) "
                              +"VALUES (?, ?, ?)",
                              (str(idx),
                               component,
                               float(self.components[component].timeseries.iloc[str(idx), "at_home"])
                               )
                              )

                    conn.commit()


                elif '_hp' in component:

                    # Check if the variable cop exists.
                    # COP is the same for all heat pumps!
                    if 'cop' not in locals():
                        cop = pd.DataFrame(
                            index = self.components[
                                next(iter(self.components.keys()))
                                ].timeseries.index,
                            columns=["cop"])

                        cop.cop = self.components[component].get_cop().cop
                        cop.interpolate(inplace=True)

                    c.execute("INSERT INTO timeseries "
                              +"(time, "
                              +"name, "
                              +"cop, "
                              +"th_energy) "
                              +"VALUES (?, ?, ?, ?)",
                              (str(idx),
                               component,
                               cop.cop[str(idx)],
                               self.components[component].user_profile.thermal_energy_demand.Heat_load_kWh.loc[str(idx)].item() #TODO: used to be HeatDemand
                               )
                              )

                    conn.commit()

                elif '_chp' in component:
                    c.execute("INSERT INTO timeseries "
                              +"(time, "
                              +"name, "
                              +"th_energy) "
                              +"VALUES (?, ?, ?)",
                              (str(idx),
                               component,
                               self.components[component].user_profile.thermal_energy_demand.Heat_load_kWh.loc[str(idx)].item() #TODO: used to be HeatDemand
                               )
                              )

                    conn.commit()

                elif '_tes' in component:
                    # Thermal energy storage has no timeseries
                    no_timeseries_lst.append(component)

                else:
                    no_timeseries_lst.append(component)

        # Close the connection
        c.close()
        conn.close()

        return no_timeseries_lst


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
