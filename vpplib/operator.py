# -*- coding: utf-8 -*-
"""
Info
----
The Operator class should be subclassed to implement different
operation stategies. One subclass for example could implement
machine learning to operate the virtual power plant.
Additional functions that help operating the virtual power plant,
like forecasting, should be implemented here.
        
TODO: Setup data type for target data and alter the referencing accordingly!

"""

import math
import pandas as pd
import pandapower as pp
import simbench
import matplotlib.pyplot as plt


class Operator(object):
    def __init__(self, virtual_power_plant, net, target_data):

        """
        Info
        ----
        This function takes two parameters. The first one is the virtual
        power plant, that should be operated by the operator. It must not
        be changed during simulation. The second parameter represents
        the target generation/consumption data. The operator tries
        to operate the virtual power plant in a way, that this target
        output is achieved.
        The Operator class should be subclassed to implement different
        operation stategies. One subclass for example could implement
        machine learning to operate the virtual power plant.
        Additional functions that help operating the virtual power plant,
        like forecasting, should be implemented here.
        
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
        self.virtual_power_plant = virtual_power_plant
        self.target_data = target_data
        self.net = net  # pandapower net object

    def operate_virtual_power_plant(self):

        """
        Info
        ----
        Operation handling
    
        This function is the key function for the operation of the virtual
        power plant. It simulates every timestamp given in the target data.
        It returns how good the operation of the virtual power plant matches
        the target data (0: no match, 1: perfect match).
        
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

        # Create result variables
        power_sum = 0
        count = 0

        # Iterate through timestamps
        for i in range(0, len(self.target_data)):

            # Operate at timestamp
            self.operate_at_timestamp(self.target_data[i][0])

            # Get balance of virtual power plant
            balance = self.virtual_power_plant.balance_at_timestamp(
                self.target_data[i][0]
            )

            # Get target balance
            target = self.target_data[i][1]

            # Calculate match
            match = 1 - (abs(target) - abs(balance)) / abs(target)

            # Add to sum and count
            power_sum += match
            count += 1

        # Calculate average of match
        average = power_sum / count

        # Return average
        return average

    def operate_at_timestamp(self, timestamp):

        """
        Info
        ----
        Raises an error since this function needs to be implemented by child classes.
        
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

        raise NotImplementedError(
            "operate_at_timestamp needs to be implemented by child classes!"
        )

    #%% assign values of generation/demand over time and run powerflow
    def run_base_scenario(self, baseload):

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

        net_dict = {}
        index = self.virtual_power_plant.components[
            next(iter(self.virtual_power_plant.components))
        ].timeseries.index
        res_loads = pd.DataFrame(
            columns=[self.net.bus.index[self.net.bus.type == "b"]], index=index
        )  # maybe only take buses with storage

        for idx in index:
            for component in self.virtual_power_plant.components.keys():

                if "storage" not in component:

                    value_for_timestamp = self.virtual_power_plant.components[
                        component
                    ].value_for_timestamp(str(idx))

                    if math.isnan(value_for_timestamp):
                        raise ValueError(
                            (
                                "The value of ",
                                component,
                                "at timestep ",
                                idx,
                                "is NaN!",
                            )
                        )

                if component in list(self.net.sgen.name):

                    self.net.sgen.p_mw[self.net.sgen.name == component] = (
                        value_for_timestamp / -1000
                    )  # kW to MW; negative due to generation

                    if math.isnan(
                        self.net.sgen.p_mw[self.net.sgen.name == component]
                    ):
                        raise ValueError(
                            (
                                "The value of ",
                                component,
                                "at timestep ",
                                idx,
                                "is NaN!",
                            )
                        )

                if component in list(self.net.load.name):

                    self.net.load.p_mw[self.net.load.name == component] = (
                        value_for_timestamp / 1000
                    )  # kW to MW

            for name in self.net.load.name:

                if (
                    self.net.load.type[self.net.load.name == name].item()
                    == "baseload"
                ):

                    self.net.load.p_mw[self.net.load.name == name] = (
                        baseload[
                            str(
                                self.net.load.bus[
                                    self.net.load.name == name
                                ].item()
                            )
                        ][str(idx)]
                        / 1000000
                    )
                    self.net.load.q_mvar[self.net.load.name == name] = 0

            if len(self.virtual_power_plant.buses_with_storage) > 0:
                for bus in self.net.bus.index[self.net.bus.type == "b"]:

                    storage_at_bus = pp.get_connected_elements(
                        self.net, "storage", bus
                    )
                    sgen_at_bus = pp.get_connected_elements(
                        self.net, "sgen", bus
                    )
                    load_at_bus = pp.get_connected_elements(
                        self.net, "load", bus
                    )

                    if len(storage_at_bus) > 0:

                        res_loads.loc[idx][bus] = sum(
                            self.net.load.loc[load_at_bus].p_mw
                        ) + sum(self.net.sgen.loc[sgen_at_bus].p_mw)

                        # set loads and sgen to 0 since they are in res_loads now
                        # reassign values after operate_storage has been executed
                        for l in list(load_at_bus):
                            self.net.load.p_mw[self.net.load.index == l] = 0

                        for l in list(sgen_at_bus):
                            self.net.sgen.p_mw[self.net.sgen.index == l] = 0

                        # run storage operation with residual load
                        state_of_charge, res_load = self.virtual_power_plant.components[
                            self.net.storage.loc[storage_at_bus].name.item()
                        ].operate_storage(
                            res_loads.loc[idx][bus].item()
                        )

                        # save state of charge and residual load in timeseries
                        self.virtual_power_plant.components[
                            self.net.storage.loc[storage_at_bus].name.item()
                        ].timeseries["state_of_charge"][
                            idx
                        ] = (
                            state_of_charge
                        )  # state_of_charge_df[idx][bus] = state_of_charge
                        self.virtual_power_plant.components[
                            self.net.storage.loc[storage_at_bus].name.item()
                        ].timeseries["residual_load"][idx] = res_load

                        # assign new residual load to loads and sgen depending on positive/negative values
                        if res_load > 0:

                            if len(load_at_bus) > 0:
                                # TODO: load according to origin of demand (baseload, hp or bev)
                                load_bus = load_at_bus.pop()
                                self.net.load.p_mw[
                                    self.net.load.index == load_bus
                                ] = res_load

                            else:
                                # assign new residual load to storage
                                storage_bus = storage_at_bus.pop()
                                self.net.storage.p_mw[
                                    self.net.storage.index == storage_bus
                                ] = res_load

                        else:

                            if len(sgen_at_bus) > 0:
                                # TODO: assign generation according to origin of energy (PV, wind oder CHP)
                                gen_bus = sgen_at_bus.pop()
                                self.net.sgen.p_mw[
                                    self.net.sgen.index == gen_bus
                                ] = res_load

                            else:
                                # assign new residual load to storage
                                storage_bus = storage_at_bus.pop()
                                self.net.storage.p_mw[
                                    self.net.storage.index == storage_bus
                                ] = res_load

            pp.runpp(self.net)

            net_dict[idx] = {}
            net_dict[idx]["res_bus"] = self.net.res_bus
            net_dict[idx]["res_line"] = self.net.res_line
            net_dict[idx]["res_trafo"] = self.net.res_trafo
            net_dict[idx]["res_load"] = self.net.res_load
            net_dict[idx]["res_sgen"] = self.net.res_sgen
            net_dict[idx]["res_ext_grid"] = self.net.res_ext_grid
            net_dict[idx]["res_storage"] = self.net.res_storage

        # res_loads.dropna(axis=1, inplace=True)

        return net_dict  # , res_loads #res_loads can be returned for analyses

    #%% define a function to apply absolute values from SimBench profiles

    def apply_absolute_simbench_values(self, absolute_values_dict, case_or_time_step):
        for elm_param in absolute_values_dict.keys():
            if absolute_values_dict[elm_param].shape[1]:
                elm = elm_param[0]
                param = elm_param[1]
                self.net[elm].loc[:, param] = absolute_values_dict[elm_param].loc[case_or_time_step]

        return self.net


    #%% assign values of generation/demand from SimBench and VPPlib
    # over time and run powerflow

    def run_simbench_scenario(self, profiles):

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

        net_dict = {}
        index = self.virtual_power_plant.components[
            next(iter(self.virtual_power_plant.components))
        ].timeseries.index
        res_loads = pd.DataFrame(
            columns=[self.net.bus.index[self.net.bus.type == "b"]], index=index
        )  # maybe only take buses with storage
        
        # # check that all needed profiles existent
        # assert not simbench.profiles_are_missing(self.net)

        # # calculate absolute profiles
        # profiles = simbench.get_absolute_values(self.net, profiles_instead_of_study_cases=True)
        # get datetime index for profiles
        for elm_param in profiles.keys():
            profiles[elm_param].index = pd.date_range(
                start=self.virtual_power_plant.components[
                next(iter(self.virtual_power_plant.components))
                ].environment.start[:4],
                periods=len(profiles[elm_param].index),
                freq=self.virtual_power_plant.components[
                next(iter(self.virtual_power_plant.components))
                ].environment.time_freq)

        for idx in index:

            # assign loadprofiles to simbench components
            self.apply_absolute_simbench_values(profiles, idx)

            for component in self.virtual_power_plant.components.keys():

                if "ees" not in component:
                    if "tes" not in component:

                        value_for_timestamp = self.virtual_power_plant.components[
                            component
                        ].value_for_timestamp(str(idx))
    
                        if math.isnan(value_for_timestamp):
                            raise ValueError(
                                (
                                    "The value of ",
                                    component,
                                    "at timestep ",
                                    idx,
                                    "is NaN!",
                                )
                            )

                if component in list(self.net.sgen.name):

                    self.net.sgen.p_mw[self.net.sgen.name == component] = (
                        value_for_timestamp / -1000
                    )  # kW to MW; negative due to generation

                    self.net.sgen.q_mvar[self.net.sgen.name == component] = 0

                    if math.isnan(
                        self.net.sgen.p_mw[self.net.sgen.name == component]
                    ):
                        raise ValueError(
                            (
                                "The value of ",
                                component,
                                "at timestep ",
                                idx,
                                "is NaN!",
                            )
                        )

                if component in list(self.net.load.name):

                    self.net.load.p_mw[self.net.load.name == component] = (
                        value_for_timestamp / 1000
                    )  # kW to MW

                    self.net.load.q_mvar[self.net.load.name == component] = 0

            if len(self.virtual_power_plant.buses_with_storage) > 0:
                for bus in self.net.bus.index[self.net.bus.type == "b"]:

                    storage_at_bus = pp.get_connected_elements(
                        self.net, "storage", bus
                    )
                    sgen_at_bus = pp.get_connected_elements(
                        self.net, "sgen", bus
                    )
                    load_at_bus = pp.get_connected_elements(
                        self.net, "load", bus
                    )

                    if len(storage_at_bus) > 0:

                        res_loads.loc[idx][bus] = sum(
                            self.net.load.loc[load_at_bus].p_mw
                        ) + sum(self.net.sgen.loc[sgen_at_bus].p_mw)

                        # set loads and sgen to 0 since they are in res_loads now
                        # reassign values after operate_storage has been executed
                        for l in list(load_at_bus):
                            self.net.load.p_mw[self.net.load.index == l] = 0

                        for l in list(sgen_at_bus):
                            self.net.sgen.p_mw[self.net.sgen.index == l] = 0

                        # run storage operation with residual load
                        state_of_charge, res_load = self.virtual_power_plant.components[
                            self.net.storage.loc[storage_at_bus].name.item()
                        ].operate_storage(
                            res_loads.loc[idx][bus].item()
                        )

                        # save state of charge and residual load in timeseries
                        self.virtual_power_plant.components[
                            self.net.storage.loc[storage_at_bus].name.item()
                        ].timeseries["state_of_charge"][
                            idx
                        ] = (
                            state_of_charge
                        )  # state_of_charge_df[idx][bus] = state_of_charge
                        self.virtual_power_plant.components[
                            self.net.storage.loc[storage_at_bus].name.item()
                        ].timeseries["residual_load"][idx] = res_load

                        # assign new residual load to loads and sgen depending on positive/negative values
                        if res_load > 0:

                            if len(load_at_bus) > 0:
                                # TODO: load according to origin of demand (baseload, hp or bev)
                                load_bus = load_at_bus.pop()
                                self.net.load.p_mw[
                                    self.net.load.index == load_bus
                                ] = res_load

                            else:
                                # assign new residual load to storage
                                storage_bus = storage_at_bus.pop()
                                self.net.storage.p_mw[
                                    self.net.storage.index == storage_bus
                                ] = res_load

                        else:

                            if len(sgen_at_bus) > 0:
                                # TODO: assign generation according to origin of energy (PV, wind oder CHP)
                                gen_bus = sgen_at_bus.pop()
                                self.net.sgen.p_mw[
                                    self.net.sgen.index == gen_bus
                                ] = res_load

                            else:
                                # assign new residual load to storage
                                storage_bus = storage_at_bus.pop()
                                self.net.storage.p_mw[
                                    self.net.storage.index == storage_bus
                                ] = res_load

            pp.runpp(self.net)

            net_dict[idx] = {}
            net_dict[idx]["res_bus"] = self.net.res_bus
            net_dict[idx]["res_line"] = self.net.res_line
            net_dict[idx]["res_trafo"] = self.net.res_trafo
            net_dict[idx]["res_load"] = self.net.res_load
            net_dict[idx]["res_sgen"] = self.net.res_sgen
            net_dict[idx]["res_ext_grid"] = self.net.res_ext_grid
            net_dict[idx]["res_storage"] = self.net.res_storage

        # res_loads.dropna(axis=1, inplace=True)

        return net_dict  # , res_loads #res_loads can be returned for analyses

# %% extract all results from pandas powerflow

    def extract_results(self, net_dict):

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

        ext_grid = pd.DataFrame()
        line_loading_percent = pd.DataFrame()
        bus_vm_pu = pd.DataFrame()
        trafo_loading_percent = pd.DataFrame()
        sgen_p_mw = pd.DataFrame()
        load_p_mw = pd.DataFrame()
        storage_p_mw = pd.DataFrame()

        for idx in net_dict.keys():

            ext_grid = ext_grid.append(
                net_dict[idx]["res_ext_grid"], ignore_index=True
            )
            line_loading_percent[idx] = net_dict[idx][
                "res_line"
            ].loading_percent
            bus_vm_pu[idx] = net_dict[idx]["res_bus"].vm_pu
            trafo_loading_percent[idx] = net_dict[idx][
                "res_trafo"
            ].loading_percent
            sgen_p_mw[idx] = net_dict[idx]["res_sgen"].p_mw
            load_p_mw[idx] = net_dict[idx]["res_load"].p_mw
            storage_p_mw[idx] = net_dict[idx]["res_storage"].p_mw

        if len(line_loading_percent.columns) > 0:
            line_loading_percent = line_loading_percent.T
            line_loading_percent.rename(
                self.net["line"].name, axis="columns", inplace=True
            )
            line_loading_percent.index = pd.to_datetime(
                line_loading_percent.index
            )

        if len(bus_vm_pu.columns) > 0:
            bus_vm_pu = bus_vm_pu.T
            bus_vm_pu.rename(self.net.bus.name, axis="columns", inplace=True)
            bus_vm_pu.index = pd.to_datetime(bus_vm_pu.index)

        trafo_loading_percent = trafo_loading_percent.T
        trafo_loading_percent.index = pd.to_datetime(
            trafo_loading_percent.index
        )
        if self.net.trafo.name is not None:
            trafo_loading_percent.rename(
                self.net.trafo.name, axis="columns", inplace=True
            )

        if len(sgen_p_mw.columns) > 0:
            sgen_p_mw = sgen_p_mw.T
            sgen_p_mw.rename(self.net.sgen.name, axis="columns", inplace=True)
            sgen_p_mw.index = pd.to_datetime(sgen_p_mw.index)

        if len(load_p_mw.columns) > 0:
            load_p_mw = load_p_mw.T
            load_p_mw.rename(self.net.load.name, axis="columns", inplace=True)
            load_p_mw.index = pd.to_datetime(load_p_mw.index)

        if len(storage_p_mw.columns) > 0:
            storage_p_mw = storage_p_mw.T
            storage_p_mw.rename(
                self.net.storage.name, axis="columns", inplace=True
            )
            storage_p_mw.index = pd.to_datetime(storage_p_mw.index)

        results = {
            "ext_grid": ext_grid,
            "trafo_loading_percent": trafo_loading_percent,
            "line_loading_percent": line_loading_percent,
            "bus_vm_pu": bus_vm_pu,
            "load_p_mw": load_p_mw,
            "sgen_p_mw": sgen_p_mw,
            "storage_p_mw": storage_p_mw,
        }

        return results

    #%% extract results of single component categories

    def extract_single_result(self, net_dict, res="load", value="p_mw"):

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

        single_result = pd.DataFrame()

        for idx in net_dict.keys():

            single_result[idx] = net_dict[idx]["res_" + res][value]

        single_result = single_result.T

        if self.net[res].name.item() is not None:
            single_result.rename(
                self.net[res].name, axis="columns", inplace=True
            )

        single_result.index = pd.to_datetime(single_result.index)

        return single_result

    def plot_results(self, results, legend=True):

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

        results["ext_grid"].plot(
            figsize=(16, 9), title="ext_grid", legend=legend
        )
        plt.show()
        results["trafo_loading_percent"].plot(
            figsize=(16, 9), title="trafo_loading_percent", legend=legend
        )
        plt.show()
        results["line_loading_percent"].plot(
            figsize=(16, 9), title="line_loading_percent", legend=legend
        )
        plt.show()
        results["bus_vm_pu"].plot(
            figsize=(16, 9), title="bus_vm_pu", legend=legend
        )
        plt.show()
        results["load_p_mw"].plot(
            figsize=(16, 9), title="load_p_mw", legend=legend
        )
        plt.show()

        self.plot_pv(results)

        self.plot_wind(results)

        if len(self.virtual_power_plant.buses_with_storage) > 0:
            results["storage_p_mw"].plot(
                figsize=(16, 9), title="storage_p_mw", legend=legend
            )

    def plot_pv(self, results):

        if len(self.virtual_power_plant.buses_with_pv) > 0:
            for gen in results["sgen_p_mw"].columns:
                if "PV" in gen:
                    results["sgen_p_mw"][gen].plot(
                        figsize=(16, 9), title="PV [MW]"
                    )
            plt.show()

    def plot_wind(self, results):

        if len(self.virtual_power_plant.buses_with_wind) > 0:
            for gen in results["sgen_p_mw"].columns:
                if "WindPower" in gen:
                    results["sgen_p_mw"][gen].plot(
                        figsize=(16, 9), title="WindPower [MW]"
                    )
            plt.show()

    def plot_storages(self):

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

        for comp in self.virtual_power_plant.components.keys():
            if "storage" in comp:
                self.virtual_power_plant.components[comp].timeseries.plot(
                    figsize=(16, 9), title=comp
                )
