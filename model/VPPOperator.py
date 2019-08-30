"""
Info
----
The VPPOperator class should be subclassed to implement different
operation stategies. One subclass for example could implement
machine learning to operate the virtual power plant.
Additional functions that help operating the virtual power plant,
like forecasting, should be implemented here.
        
TODO: Setup data type for target data and alter the referencing accordingly!

"""

import traceback
import math
import pandas as pd
import pandapower as pp

class VPPOperator(object):

    def __init__(self, virtualPowerPlant, net, targetData):
        
        """
        Info
        ----
        This function takes two parameters. The first one is the virtual
        power plant, that should be operated by the operator. It must not
        be changed during simulation. The second parameter represents
        the target generation/consumption data. The operator tries
        to operate the virtual power plant in a way, that this target
        output is achieved.
        The VPPOperator class should be subclassed to implement different
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
        self.virtualPowerPlant = virtualPowerPlant
        self.targetData = targetData
        self.net = net #pandapower net object


    def operateVirtualPowerPlant(self):
        
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
        sum = 0
        count = 0
    
    
        # Iterate through timestamps
        for i in range(0, len(self.targetData)):
    
            # Operate at timestamp
            self.operateAtTimestamp(self.targetData[i][0])

    
            # Get balance of virtual power plant
            balance = self.virtualPowerPlant.balanceAtTimestamp(self.targetData[i][0])
            
            # Get target balance
            target = self.targetData[i][1]

    
            # Calculate match
            match = 1 - (abs(target) - abs(balance)) / abs(target)

    
            # Add to sum and count
            sum += match
            count += 1
            
            
        # Calculate average of match
        average = sum / count
        
        
        # Return average
        return average


    def operateAtTimestamp(self, timestamp):
        
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

        raise NotImplementedError("operateAtTimestamp needs to be implemented by child classes!")
        
            
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
        index = self.virtualPowerPlant.components[next(iter(self.virtualPowerPlant.components))].timeseries.index
        res_loads = pd.DataFrame(columns=[self.net.bus.index[self.net.bus.type == 'b']], index=index) #maybe only take buses with storage
        
        for idx in index:
            for component in self.virtualPowerPlant.components.keys():
        
                if 'storage' not in component:
                    
                    valueForTimestamp = self.virtualPowerPlant.components[component].valueForTimestamp(str(idx))
                    
                    if math.isnan(valueForTimestamp):
                        traceback.print_exc(("The value of ", component, "at timestep ", idx, "is NaN!"))
                
                if component in list(self.net.sgen.name):
                    
                    self.net.sgen.p_mw[self.net.sgen.name == component] = valueForTimestamp/-1000 #kW to MW; negative due to generation
                    
                    if math.isnan(self.net.sgen.p_mw[self.net.sgen.name == component]):
                        traceback.print_exc(("The value of ", component, "at timestep ", idx, "is NaN!"))
                
                if component in list(self.net.load.name):
                    
                    self.net.load.p_mw[self.net.load.name == component] = valueForTimestamp/1000 #kW to MW
                
            
            for name in self.net.load.name:
            
                if self.net.load.type[self.net.load.name == name].item() == 'baseload':
                
                    self.net.load.p_mw[self.net.load.name == name] = baseload[str(self.net.load.bus[self.net.load.name == name].item())][str(idx)]/1000000
                    self.net.load.q_mvar[self.net.load.name == name] = 0
                
            if len(self.virtualPowerPlant.buses_with_storage) > 0: 
                for bus in self.net.bus.index[self.net.bus.type == 'b']:
                
                    storage_at_bus = pp.get_connected_elements(self.net, "storage", bus)
                    sgen_at_bus = pp.get_connected_elements(self.net, "sgen", bus)
                    load_at_bus = pp.get_connected_elements(self.net, "load", bus)
                    
                    if len(storage_at_bus) > 0:
                        
                        res_loads.loc[idx][bus] = sum(self.net.load.loc[load_at_bus].p_mw) +  sum(self.net.sgen.loc[sgen_at_bus].p_mw)
                        
                        #set loads and sgen to 0 since they are in res_loads now
                        #reassign values after operate_storage has been executed
                        for l in list(load_at_bus):
                            self.net.load.p_mw[self.net.load.index == l]=0
                            
                        for l in list(sgen_at_bus):
                            self.net.sgen.p_mw[self.net.sgen.index == l]=0
                        
                        
                        #run storage operation with residual load
                        state_of_charge, res_load = self.virtualPowerPlant.components[self.net.storage.loc[storage_at_bus].name.item()].operate_storage(res_loads.loc[idx][bus].item())
                        
                        #save state of charge and residual load in timeseries
                        self.virtualPowerPlant.components[self.net.storage.loc[storage_at_bus].name.item()].timeseries['state_of_charge'][idx] = state_of_charge # state_of_charge_df[idx][bus] = state_of_charge
                        self.virtualPowerPlant.components[self.net.storage.loc[storage_at_bus].name.item()].timeseries['residual_load'][idx] = res_load
                        
                        #assign new residual load to loads and sgen depending on positive/negative values
                        if res_load >0:
        
                            if len(load_at_bus) >0:
                                #TODO: load according to origin of demand (baseload, hp or bev)
                                load_bus = load_at_bus.pop()
                                self.net.load.p_mw[self.net.load.index == load_bus] = res_load
                                
                            else:
                                #assign new residual load to storage
                                storage_bus = storage_at_bus.pop()
                                self.net.storage.p_mw[self.net.storage.index == storage_bus] = res_load
                        
                        else:
        
                            if len(sgen_at_bus) >0:
                                #TODO: assign generation according to origin of energy (PV, wind oder CHP)
                                gen_bus = sgen_at_bus.pop()
                                self.net.sgen.p_mw[self.net.sgen.index == gen_bus] = res_load
                                
                            else:
                                #assign new residual load to storage
                                storage_bus = storage_at_bus.pop()
                                self.net.storage.p_mw[self.net.storage.index == storage_bus] = res_load
                        
                        
            pp.runpp(self.net)
            
            net_dict[idx] = {}
            net_dict[idx]['res_bus'] = self.net.res_bus
            net_dict[idx]['res_line'] = self.net.res_line
            net_dict[idx]['res_trafo'] = self.net.res_trafo
            net_dict[idx]['res_load'] = self.net.res_load
            net_dict[idx]['res_sgen'] = self.net.res_sgen
            net_dict[idx]['res_ext_grid'] = self.net.res_ext_grid
            net_dict[idx]['res_storage'] = self.net.res_storage
            
        #res_loads.dropna(axis=1, inplace=True)
            
        return net_dict #, res_loads #res_loads can be returned for analyses
    
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
            
            ext_grid = ext_grid.append(net_dict[idx]['res_ext_grid'], ignore_index=True)
            line_loading_percent[idx] = net_dict[idx]['res_line'].loading_percent
            bus_vm_pu[idx] = net_dict[idx]['res_bus'].vm_pu
            trafo_loading_percent[idx] = net_dict[idx]['res_trafo'].loading_percent
            sgen_p_mw[idx] = net_dict[idx]['res_sgen'].p_mw
            load_p_mw[idx] = net_dict[idx]['res_load'].p_mw
            storage_p_mw[idx] = net_dict[idx]['res_storage'].p_mw

        #TODO: adjust method to other extractions            
        #ext_grid = ext_grid.T
#        if self.net.ext_grid.name.item() is not None:
#            ext_grid_p_mw.rename(self.net.ext_grid.name, axis='columns', inplace=True)
    
        if len(line_loading_percent.columns) >0:
            line_loading_percent = line_loading_percent.T
            line_loading_percent.rename(self.net['line'].name, axis='columns', inplace=True)
            line_loading_percent.index = pd.to_datetime(line_loading_percent.index)
        
        if len(bus_vm_pu.columns) >0:
            bus_vm_pu = bus_vm_pu.T
            bus_vm_pu.rename(self.net.bus.name, axis='columns', inplace=True)
            bus_vm_pu.index = pd.to_datetime(bus_vm_pu.index)
            
        trafo_loading_percent = trafo_loading_percent.T
        trafo_loading_percent.index = pd.to_datetime(trafo_loading_percent.index)
        if self.net.trafo.name.item() is not None:
            trafo_loading_percent.rename(self.net.trafo.name, axis='columns', inplace=True)
        
        if len(sgen_p_mw.columns) >0:
            sgen_p_mw = sgen_p_mw.T
            sgen_p_mw.rename(self.net.sgen.name, axis='columns', inplace=True)
            sgen_p_mw.index = pd.to_datetime(sgen_p_mw.index)
        
        if len(load_p_mw.columns) >0:
            load_p_mw = load_p_mw.T
            load_p_mw.rename(self.net.load.name, axis='columns', inplace=True)
            load_p_mw.index = pd.to_datetime(load_p_mw.index)
        
        if len(storage_p_mw.columns) >0:
            storage_p_mw = storage_p_mw.T
            storage_p_mw.rename(self.net.storage.name, axis='columns', inplace=True)
            storage_p_mw.index = pd.to_datetime(storage_p_mw.index)
            
        results = {'ext_grid':ext_grid, 
                   'trafo_loading_percent':trafo_loading_percent,
                   'line_loading_percent':line_loading_percent,
                   'bus_vm_pu':bus_vm_pu,
                   'load_p_mw':load_p_mw,
                   'sgen_p_mw':sgen_p_mw,
                   'storage_p_mw':storage_p_mw}
            
        return results
    
    #%% extract results of single component categories
    
    def extract_single_result(self, net_dict, res='load', value='p_mw'):
        
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
            
            single_result[idx] = net_dict[idx]['res_'+res][value]
        
        single_result = single_result.T
        
        if self.net[res].name.item() is not None:
            single_result.rename(self.net[res].name, axis='columns', inplace=True)
            
        single_result.index = pd.to_datetime(single_result.index)
        
        return single_result
    
    def plot_results(self, results):
        
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
        
        results['ext_grid'].plot(figsize=(16,9), title='ext_grid')
        results['trafo_loading_percent'].plot(figsize=(16,9), title='trafo_loading_percent')
        results['line_loading_percent'].plot(figsize=(16,9), title='line_loading_percent')
        results['bus_vm_pu'].plot(figsize=(16,9), title='bus_vm_pu')
        results['load_p_mw'].plot(figsize=(16,9), title='load_p_mw')
        
        if len(self.virtualPowerPlant.buses_with_pv) > 0:
            results['sgen_p_mw'].plot(figsize=(16,9), title='sgen_p_mw')
            
        if len(self.virtualPowerPlant.buses_with_storage) > 0:
            results['storage_p_mw'].plot(figsize=(16,9), title='storage_p_mw')
            
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
        
        for comp in self.virtualPowerPlant.components.keys():
            if 'storage' in comp:
                self.virtualPowerPlant.components[comp].timeseries.plot(figsize=(16,9), title=comp)
                
    

