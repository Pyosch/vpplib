# -*- coding: utf-8 -*-
"""
Operator Module
--------------
This module contains the Operator class which is responsible for operating
a virtual power plant (VPP) according to different strategies.

The Operator class serves as a base class that should be subclassed to implement
different operation strategies. For example, a subclass could implement machine
learning algorithms to optimize the operation of the virtual power plant.

The module also provides functionality for running power flow simulations using
pandapower, analyzing results, and visualizing the performance of the virtual
power plant components.

TODO: Setup data type for target data and alter the referencing accordingly!
"""

import math
import pandas as pd
import pandapower as pp
import matplotlib.pyplot as plt
from tqdm import tqdm


class Operator(object):
    """
    A class for operating a virtual power plant according to different strategies.
    
    The Operator class is responsible for controlling the components of a virtual
    power plant to achieve a target generation/consumption profile. It provides
    methods for simulating the operation of the virtual power plant, running power
    flow calculations, and analyzing the results.
    
    This class is designed to be subclassed to implement different operation
    strategies. The base class provides common functionality, while specific
    operation algorithms should be implemented in subclasses.
    
    Attributes
    ----------
    virtual_power_plant : VirtualPowerPlant
        The virtual power plant to be operated
    target_data : list of tuples
        Target generation/consumption data as a list of (timestamp, value) tuples
    net : pandapower.pandapowerNet
        Pandapower network model for power flow calculations
    environment : Environment, optional
        Environment object containing weather data and simulation parameters
    
    Notes
    -----
    The operate_at_timestamp method must be implemented by subclasses to define
    the specific operation strategy.
    """
    
    def __init__(self,
                 virtual_power_plant,
                 net,
                 target_data,
                 environment=None):
        """
        Initialize an Operator object.
        
        Parameters
        ----------
        virtual_power_plant : VirtualPowerPlant
            The virtual power plant to be operated. This object must not be
            changed during simulation.
        net : pandapower.pandapowerNet
            Pandapower network model for power flow calculations
        target_data : list of tuples
            Target generation/consumption data as a list of (timestamp, value) tuples.
            The operator tries to operate the virtual power plant to match this target.
        environment : Environment, optional
            Environment object containing weather data and simulation parameters
            
        Notes
        -----
        The target_data parameter should be a list of tuples, where each tuple
        contains a timestamp and a target value. The timestamp can be either a
        string in the format 'YYYY-MM-DD hh:mm:ss' or an integer index.
        """

        # Configure attributes
        self.virtual_power_plant = virtual_power_plant
        self.target_data = target_data
        self.net = net  # pandapower net object
        self.environment = environment

    def operate_virtual_power_plant(self):
        """
        Operate the virtual power plant according to the target data.
        
        This method is the key function for the operation of the virtual power plant.
        It iterates through all timestamps in the target data, calls the
        operate_at_timestamp method for each timestamp, and calculates how well
        the operation of the virtual power plant matches the target data.
        
        The match is calculated as:
        match = 1 - (abs(target) - abs(balance)) / abs(target)
        
        A value of 1 indicates a perfect match, while a value of 0 indicates
        no match at all. Negative values can occur if the balance is far from
        the target.
        
        Returns
        -------
        float
            Average match between the virtual power plant operation and the target data.
            A value of 1 indicates a perfect match, while a value of 0 indicates
            no match at all.
            
        Notes
        -----
        This method relies on the operate_at_timestamp method, which must be
        implemented by subclasses to define the specific operation strategy.
        
        The match calculation assumes that the target values are non-zero.
        If a target value is zero, the match calculation may result in a
        division by zero error.
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
        Operate the virtual power plant at a specific timestamp.
        
        This method should be implemented by subclasses to define the specific
        operation strategy for the virtual power plant at a given timestamp.
        The base implementation raises a NotImplementedError.
        
        Parameters
        ----------
        timestamp : str or int
            The timestamp at which to operate the virtual power plant.
            If str: timestamp in format 'YYYY-MM-DD hh:mm:ss'
            If int: index position in the timeseries
            
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
            
        Notes
        -----
        This method should control the components of the virtual power plant
        to achieve the target generation/consumption at the specified timestamp.
        Typical operations might include:
        - Adjusting power output of controllable generators
        - Charging or discharging storage systems
        - Controlling flexible loads
        """
        raise NotImplementedError(
            "operate_at_timestamp needs to be implemented by child classes!"
        )

    # %% assign values of generation/demand over time and run powerflow
    def run_base_scenario(self, baseload):
        """
        Run a base scenario simulation with power flow calculations.
        
        This method assigns the generation and demand values from the virtual power plant
        components to the pandapower network model, runs power flow calculations for each
        timestamp, and returns the results. It also handles the operation of storage
        components based on the residual load at each bus.
        
        Parameters
        ----------
        baseload : dict
            Dictionary containing baseload profiles for each bus in the network.
            The keys should be bus IDs as strings, and the values should be
            pandas Series with timestamps as index and load values in W.
            
        Returns
        -------
        dict
            Dictionary containing the power flow results for each timestamp.
            The keys are timestamps, and the values are dictionaries containing
            the pandapower result tables (res_bus, res_line, res_trafo, etc.).
            
        Notes
        -----
        This method performs the following steps for each timestamp:
        1. Assign generation and demand values from VPP components to the network
        2. Assign baseload values to the network
        3. Calculate residual load at buses with storage
        4. Operate storage components based on residual load
        5. Run power flow calculation
        6. Store results
        
        The method handles both generation (negative values) and consumption
        (positive values) components, as well as storage components that can
        both consume and generate power depending on the residual load.
        """

        net_dict = {}
        index = self.virtual_power_plant.components[
            next(iter(self.virtual_power_plant.components))
        ].timeseries.index
        res_loads = pd.DataFrame(
            columns=[self.net.bus.index[self.net.bus.type == "b"]], index=index
        )  # maybe only take buses with storage

        for idx in tqdm(index):
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

                    self.net.sgen.loc[self.net.sgen.name == component, 'p_mw'] = (
                        value_for_timestamp / -1000
                    )  # kW to MW; negative due to generation

                    if math.isnan(
                        self.net.sgen.loc[self.net.sgen.name == component, 'p_mw'].iloc[0]
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

                    self.net.load.loc[self.net.load.name == component, 'p_mw'] = (
                        value_for_timestamp / 1000
                    )  # kW to MW

            for name in self.net.load.name:

                if (
                    self.net.load.loc[self.net.load.name == name, 'type'].item()
                    == "baseload"
                ):

                    self.net.load.loc[self.net.load.name == name, 'p_mw'] = (
                        baseload[
                            str(
                                self.net.load.loc[
                                    self.net.load.name == name, 'bus'
                                ].item()
                            )
                        ][str(idx)]
                        / 1000000
                    )
                    self.net.load.loc[self.net.load.name == name, 'q_mvar'] = 0

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

                        res_loads.loc[(idx, bus)] = sum(
                            [self.net.load.loc[load, 'p_mw'] for load in load_at_bus]
                            ) + sum([self.net.sgen.loc[sgen, 'p_mw'] for sgen in sgen_at_bus])

                        # set loads and sgen to 0 since they are in res_loads now
                        # reassign values after operate_storage has been executed
                        for l in list(load_at_bus):
                            self.net.load.loc[self.net.load.index == l, 'p_mw'] = 0

                        for l in list(sgen_at_bus):
                            self.net.sgen.loc[self.net.sgen.index == l, 'p_mw'] = 0

                        # run storage operation with residual load
                        state_of_charge, res_load = self.virtual_power_plant.components[
                            self.net.storage.loc[list(storage_at_bus), 'name'].item()
                        ].operate_storage(
                            res_loads.loc[(idx, bus)].item()
                        )

                        # save state of charge and residual load in timeseries
                        component_name = self.net.storage.loc[list(storage_at_bus), 'name'].item()
                        self.virtual_power_plant.components[component_name].timeseries.loc[idx, "state_of_charge"] = state_of_charge
                        self.virtual_power_plant.components[component_name].timeseries.loc[idx, "residual_load"] = res_load

                        # assign new residual load to loads and sgen depending on positive/negative values
                        if res_load > 0:

                            if len(load_at_bus) > 0:
                                # TODO: load according to origin of demand (baseload, hp or bev)
                                load_bus = load_at_bus.pop()
                                self.net.load.loc[
                                    self.net.load.index == load_bus, 'p_mw'
                                ] = res_load

                            else:
                                # assign new residual load to storage
                                storage_bus = storage_at_bus.pop()
                                self.net.storage.loc[
                                    self.net.storage.index == storage_bus, 'p_mw'
                                ] = res_load

                        else:

                            if len(sgen_at_bus) > 0:
                                # TODO: assign generation according to origin of energy (PV, wind oder CHP)
                                gen_bus = sgen_at_bus.pop()
                                self.net.sgen.loc[
                                    self.net.sgen.index == gen_bus, 'p_mw'
                                ] = res_load

                            else:
                                # assign new residual load to storage
                                storage_bus = storage_at_bus.pop()
                                self.net.storage.loc[
                                    self.net.storage.index == storage_bus, 'p_mw'
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

        return net_dict  # , res_loads #res_loads can be returned for analyses

    # %% define a function to apply absolute values from SimBench profiles
    def apply_absolute_simbench_values(self, absolute_values_dict, case_or_time_step):
        """
        Apply absolute values from SimBench profiles to the network model.
        
        This method assigns values from SimBench profiles to the corresponding
        elements and parameters in the pandapower network model for a specific
        timestamp or case.
        
        Parameters
        ----------
        absolute_values_dict : dict
            Dictionary containing SimBench profiles. The keys are tuples of
            (element_type, parameter_name), and the values are pandas DataFrames
            with timestamps as index and parameter values as columns.
        case_or_time_step : str or pandas.Timestamp
            The timestamp or case for which to apply the values
            
        Returns
        -------
        pandapower.pandapowerNet
            The updated pandapower network model
            
        Notes
        -----
        This method is used by the run_simbench_scenario method to apply
        SimBench profiles to the network model before running power flow
        calculations.
        """
        for elm_param in absolute_values_dict.keys():
            if absolute_values_dict[elm_param].shape[1]:
                elm = elm_param[0]
                param = elm_param[1]
                self.net[elm].loc[:,
                                  param] = absolute_values_dict[elm_param].loc[case_or_time_step]

        return self.net

    # %% assign values of generation/demand from SimBench and VPPlib
    # over time and run powerflow
    def run_simbench_scenario(self, profiles):
        """
        Run a SimBench scenario simulation with power flow calculations.
        
        This method is similar to run_base_scenario but uses SimBench profiles
        for the network components in addition to the virtual power plant components.
        It assigns the generation and demand values from both sources to the
        pandapower network model, runs power flow calculations for each timestamp,
        and returns the results.
        
        Parameters
        ----------
        profiles : dict
            Dictionary containing SimBench profiles. The keys are tuples of
            (element_type, parameter_name), and the values are pandas DataFrames
            with timestamps as index and parameter values as columns.
            
        Returns
        -------
        dict
            Dictionary containing the power flow results for each timestamp.
            The keys are timestamps, and the values are dictionaries containing
            the pandapower result tables (res_bus, res_line, res_trafo, etc.).
            
        Notes
        -----
        This method performs the following steps for each timestamp:
        1. Apply SimBench profiles to the network model
        2. Assign generation and demand values from VPP components to the network
        3. Calculate residual load at buses with storage
        4. Operate storage components based on residual load
        5. Run power flow calculation
        6. Store results
        
        The method handles both generation (negative values) and consumption
        (positive values) components, as well as storage components that can
        both consume and generate power depending on the residual load.
        
        References
        ----------
        SimBench: https://simbench.de/en/
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

        for idx in tqdm(index):

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

                    self.net.sgen.loc[self.net.sgen.name == component, 'p_mw'] = (
                        value_for_timestamp / -1000
                    )  # kW to MW; negative due to generation

                    self.net.sgen.loc[self.net.sgen.name == component, 'q_mvar'] = 0

                    if math.isnan(
                        self.net.sgen.loc[self.net.sgen.name == component, 'p_mw']
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

                    self.net.load.loc[self.net.load.name == component, 'p_mw'] = (
                        value_for_timestamp / 1000
                    )  # kW to MW

                    self.net.load.loc[self.net.load.name == component, 'q_mvar'] = 0

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

                        res_loads.loc[(idx, bus)] = sum(
                            self.net.load.loc[load_at_bus].p_mw
                        ) + sum(self.net.sgen.loc[sgen_at_bus].p_mw)

                        # set loads and sgen to 0 since they are in res_loads now
                        # reassign values after operate_storage has been executed
                        for l in list(load_at_bus):
                            self.net.load.loc[self.net.load.index == l, 'p_mw'] = 0

                        for l in list(sgen_at_bus):
                            self.net.sgen.loc[self.net.sgen.index == l, 'p_mw'] = 0

                        # run storage operation with residual load
                        state_of_charge, res_load = self.virtual_power_plant.components[
                            self.net.storage.loc[storage_at_bus, 'name'].item()
                        ].operate_storage(
                            res_loads.loc[(idx, bus)]
                        )

                        # save state of charge and residual load in timeseries
                        self.virtual_power_plant.components[
                            self.net.storage.loc[storage_at_bus, 'name'].item()
                        ].timeseries["state_of_charge"][
                            idx
                        ] = (
                            state_of_charge
                        )  # state_of_charge_df[idx][bus] = state_of_charge
                        self.virtual_power_plant.components[
                            self.net.storage.loc[storage_at_bus, 'name'].item()
                        ].timeseries["residual_load"][idx] = res_load

                        # assign new residual load to loads and sgen depending on positive/negative values
                        if res_load > 0:

                            if len(load_at_bus) > 0:
                                # TODO: load according to origin of demand (baseload, hp or bev)
                                load_bus = load_at_bus.pop()
                                self.net.load.loc[
                                    self.net.load.index == load_bus, 'p_mw'
                                ] = res_load

                            else:
                                # assign new residual load to storage
                                storage_bus = storage_at_bus.pop()
                                self.net.storage.loc[
                                    self.net.storage.index == storage_bus, 'p_mw'
                                ] = res_load

                        else:

                            if len(sgen_at_bus) > 0:
                                # TODO: assign generation according to origin of energy (PV, wind oder CHP)
                                gen_bus = sgen_at_bus.pop()
                                self.net.sgen.loc[
                                    self.net.sgen.index == gen_bus, 'p_mw'
                                ] = res_load

                            else:
                                # assign new residual load to storage
                                storage_bus = storage_at_bus.pop()
                                self.net.storage.loc[
                                    self.net.storage.index == storage_bus, 'p_mw'
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

        return net_dict  # , res_loads #res_loads can be returned for analyses


# %% extract all results from pandas powerflow

    def extract_results(self, net_dict):
        """
        Extract and organize power flow results from the simulation.
        
        This method extracts the power flow results from the simulation and
        organizes them into a dictionary of pandas DataFrames, with one DataFrame
        for each result type (bus, line, load, etc.) and parameter (p_mw, q_mvar, etc.).
        
        Parameters
        ----------
        net_dict : dict
            Dictionary containing the power flow results for each timestamp,
            as returned by run_base_scenario or run_simbench_scenario.
            
        Returns
        -------
        dict
            Dictionary containing the extracted results. The keys are tuples of
            (result_type, parameter_name, element_index), and the values are
            pandas Series with timestamps as index and parameter values as values.
            
        Notes
        -----
        This method extracts the following result types:
        - res_bus: Bus results (vm_pu, va_degree, p_mw, q_mvar)
        - res_line: Line results (p_from_mw, q_from_mvar, p_to_mw, q_to_mvar, pl_mw, ql_mvar, i_ka, loading_percent)
        - res_trafo: Transformer results (p_hv_mw, q_hv_mvar, p_lv_mw, q_lv_mvar, pl_mw, ql_mvar, i_hv_ka, i_lv_ka, loading_percent)
        - res_load: Load results (p_mw, q_mvar)
        - res_sgen: Static generator results (p_mw, q_mvar)
        - res_ext_grid: External grid results (p_mw, q_mvar)
        - res_storage: Storage results (p_mw, q_mvar)
        
        The extracted results can be used for analysis and visualization.
        """

        # Create DataFrames for later export
        ext_grid = pd.DataFrame()
        line_loading_percent = pd.DataFrame()
        bus_vm_pu = pd.DataFrame()
        bus_p_mw = pd.DataFrame()
        bus_q_mvr = pd.DataFrame()
        trafo_loading_percent = pd.DataFrame()
        sgen_p_mw = pd.DataFrame()
        load_p_mw = pd.DataFrame()
        storage_p_mw = pd.DataFrame()

        # The net_dic contains the data of the grid. The timestamps are the
        # keys of the dictionary. First, extract the information to the df
        for idx in tqdm(net_dict.keys()):

            ext_grid = pd.concat(
                [ext_grid,
                 net_dict[pd.to_datetime(idx)]["res_ext_grid"]
                 ], ignore_index=True)

            line_loading_percent[idx] = net_dict[idx][
                "res_line"
            ].loading_percent

            bus_vm_pu[idx] = net_dict[idx]["res_bus"].vm_pu
            bus_p_mw[idx] = net_dict[idx]["res_bus"].p_mw
            bus_q_mvr[idx] = net_dict[idx]["res_bus"].q_mvar
            trafo_loading_percent[idx] = net_dict[idx][
                "res_trafo"
            ].loading_percent

            sgen_p_mw[idx] = net_dict[idx]["res_sgen"].p_mw
            load_p_mw[idx] = net_dict[idx]["res_load"].p_mw
            storage_p_mw[idx] = net_dict[idx]["res_storage"].p_mw

        # Since the columns are now named after the timesteps, the df needs to
        # be transposed and restructured
        if len(line_loading_percent.columns) > 0:
            line_loading_percent = line_loading_percent.T
            line_loading_percent.rename(
                self.net.line.name, axis="columns", inplace=True
            )
            line_loading_percent.index = pd.to_datetime(
                line_loading_percent.index
            )

        if len(bus_vm_pu.columns) > 0:
            bus_vm_pu = bus_vm_pu.T
            bus_vm_pu.rename(self.net.bus.name, axis="columns", inplace=True)
            bus_vm_pu.index = pd.to_datetime(bus_vm_pu.index)

        if len(bus_p_mw.columns) > 0:
            bus_p_mw = bus_p_mw.T
            bus_p_mw.rename(self.net.bus.name, axis="columns", inplace=True)
            bus_p_mw.index = pd.to_datetime(bus_p_mw.index)

        if len(bus_q_mvr.columns) > 0:
            bus_q_mvr = bus_q_mvr.T
            bus_q_mvr.rename(self.net.bus.name, axis="columns", inplace=True)
            bus_q_mvr.index = pd.to_datetime(bus_q_mvr.index)

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
            "bus_p_mw": bus_p_mw,
            "bus_q_mvr": bus_q_mvr,
            "load_p_mw": load_p_mw,
            "sgen_p_mw": sgen_p_mw,
            "storage_p_mw": storage_p_mw,
        }

        return results

    # %% extract results of single component categories

    def extract_single_result(self, net_dict, res="load", value="p_mw"):
        """
        Extract a specific result type and parameter from the simulation.
        
        This method extracts a specific result type and parameter from the
        power flow results and returns it as a pandas DataFrame with timestamps
        as index and element indices as columns.
        
        Parameters
        ----------
        net_dict : dict
            Dictionary containing the power flow results for each timestamp,
            as returned by run_base_scenario or run_simbench_scenario.
        res : str, optional
            Result type to extract (default: "load").
            Options: "bus", "line", "trafo", "load", "sgen", "ext_grid", "storage"
        value : str, optional
            Parameter name to extract (default: "p_mw").
            Options depend on the result type, e.g., "p_mw", "q_mvar", "vm_pu", etc.
            
        Returns
        -------
        pandas.DataFrame
            DataFrame containing the extracted result, with timestamps as index
            and element indices as columns.
            
        Notes
        -----
        This method is useful for extracting specific results for analysis and
        visualization. For example, to extract the active power of all loads,
        use res="load" and value="p_mw".
        
        The method automatically prepends "res_" to the result type, so "load"
        becomes "res_load" when accessing the result in the net_dict.
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
        Plot the power flow results.
        
        This method creates a plot of the power flow results, with one line
        for each element and parameter combination. It is useful for visualizing
        the results of the simulation.
        
        Parameters
        ----------
        results : dict or pandas.DataFrame
            Results to plot. If dict, it should be the output of extract_results
            or extract_single_result. If DataFrame, it should have timestamps as
            index and element indices as columns.
        legend : bool, optional
            Whether to show the legend (default: True)
            
        Returns
        -------
        matplotlib.figure.Figure
            The created figure object
            
        Notes
        -----
        This method creates a figure with a single subplot and plots all results
        on the same axes. The x-axis represents time, and the y-axis represents
        the parameter values.
        
        If the results contain many elements, the plot may become cluttered.
        In such cases, it may be better to use extract_single_result to extract
        specific results and plot them separately.
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
        """
        Plot the power output of all PV components from simulation results.
        
        This method creates a plot of the power output of all PV components
        from the simulation results. It is useful for visualizing the generation
        profile of PV systems after a power flow simulation.
        
        Parameters
        ----------
        results : dict
            Dictionary containing the extracted results, as returned by
            extract_results or extract_single_result. Should contain a key
            "sgen_p_mw" with a DataFrame of static generator active power.
            
        Notes
        -----
        This method creates a figure with a single subplot and plots the power
        output of all PV components on the same axes. The x-axis represents time,
        and the y-axis represents power in MW.
        
        The method identifies PV components by checking if the component name
        contains the string "PV".
        
        If there are no buses with PV components in the virtual power plant,
        the method does nothing.
        """
        if len(self.virtual_power_plant.buses_with_pv) > 0:
            for gen in results["sgen_p_mw"].columns:
                if "PV" in gen:
                    results["sgen_p_mw"][gen].plot(
                        figsize=(16, 9), title="PV [MW]"
                    )
            plt.show()

    def plot_wind(self, results):
        """
        Plot the power output of all wind components from simulation results.
        
        This method creates a plot of the power output of all wind components
        from the simulation results. It is useful for visualizing the generation
        profile of wind turbines after a power flow simulation.
        
        Parameters
        ----------
        results : dict
            Dictionary containing the extracted results, as returned by
            extract_results or extract_single_result. Should contain a key
            "sgen_p_mw" with a DataFrame of static generator active power.
            
        Notes
        -----
        This method creates a figure with a single subplot and plots the power
        output of all wind components on the same axes. The x-axis represents time,
        and the y-axis represents power in MW.
        
        The method identifies wind components by checking if the component name
        contains the string "WindPower".
        
        If there are no buses with wind components in the virtual power plant,
        the method does nothing.
        """
        if len(self.virtual_power_plant.buses_with_wind) > 0:
            for gen in results["sgen_p_mw"].columns:
                if "WindPower" in gen:
                    results["sgen_p_mw"][gen].plot(
                        figsize=(16, 9), title="WindPower [MW]"
                    )
            plt.show()

    def plot_storages(self):
        """
        Plot the timeseries data of all storage components.
        
        This method creates a plot of the timeseries data of all storage components
        in the virtual power plant. It is useful for visualizing the state of charge,
        power input/output, and other parameters of storage systems.
        
        Returns
        -------
        None
            This method does not return anything, but displays the plots.
            
        Notes
        -----
        This method creates a separate figure for each storage component and plots
        all columns of its timeseries data. The x-axis represents time, and the
        y-axis represents the parameter values.
        
        The method identifies storage components by checking if the component name
        contains the string "storage".
        
        The plots include all data in the timeseries DataFrame of each storage
        component, which may include state of charge, power input/output, and
        other parameters depending on the storage component implementation.
        """

        for comp in self.virtual_power_plant.components.keys():
            if "storage" in comp:
                self.virtual_power_plant.components[comp].timeseries.plot(
                    figsize=(16, 9), title=comp
                )
