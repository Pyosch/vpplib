# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 10:38:17 2019

@author: Sascha Birk
"""

import pandas as pd
import math
import random
import traceback
import pandapower as pp
import pandapower.networks as pn
from model.VPPPhotovoltaic import VPPPhotovoltaic
from model.VPPBEV import VPPBEV
from model.VPPHeatPump import VPPHeatPump
from model.VPPEnergyStorage import VPPEnergyStorage
from model.VirtualPowerPlant import VirtualPowerPlant


latitude = 50.941357
longitude = 6.958307

start = '2017-06-01 00:00:00'
end = '2017-06-01 23:45:00'
year = '2017'
time_freq = "15 min"
timebase=15/60
index=pd.date_range(start=start, end=end, freq=time_freq)

weather_data = pd.read_csv("./Input_House/PV/2017_irradiation_15min.csv")
weather_data.set_index("index", inplace = True)

baseload = pd.read_csv("./Input_House/Base_Szenario/df_S_15min.csv")
baseload.set_index("Time", inplace=True)

#storage
timebase = 15/60
chargeEfficiency = 0.98
dischargeEfficiency = 0.98
maxPower = 4 #kW
capacity = 4 #kWh
maxC = 1 #factor between 0.5 and 1.2

"""
Create virtual Powerplant:
"""
#%% create instance of VirtualPowerPlant and the designated grid
vpp = VirtualPowerPlant("Master")

net = pn.panda_four_load_branch()

#%% define the amount of components in the grid
#
#pv_percentage = 50
#storage_percentage = 0
#bev_percentage = 50
#hp_percentage = 20
#
#%% assign components to the bus names
#
##TODO: put in function:
#pv_amount = int(round((len(net.bus.name[net.bus.type == 'b']) * (pv_percentage/100)), 0))
#buses_with_pv = random.sample(list(net.bus.name[net.bus.type == 'b']), pv_amount)
#
#hp_amount = int(round((len(net.bus.name[net.bus.type == 'b']) * (hp_percentage/100)), 0))
#buses_with_hp = random.sample(list(net.bus.name[net.bus.type == 'b']), hp_amount)
#
#bev_amount = int(round((len(net.bus.name[net.bus.type == 'b']) * (bev_percentage/100)), 0))
#buses_with_bev = random.sample(list(net.bus.name[net.bus.type == 'b']), bev_amount)
#
##Distribution of el storage is only done for houses with pv
#storage_amount = int(round((len(buses_with_pv) * (storage_percentage/100)), 0))
#buses_with_storage = random.sample(buses_with_pv, storage_amount)

#%% assign components to the bus names

#TODO: put in function:
buses_with_pv = ['bus3', 'bus4', 'bus5', 'bus6']

buses_with_hp = ['bus4']

buses_with_bev = ['bus5']#, 'bus4', 'bus5', 'bus6']

#Distribution of el storage is only done for houses with pv
buses_with_storage = ['bus5']

#%% assign components to the loadbuses
#
#bus_lst = []
#for b in net.bus.name:
#    if 'loadbus' in b:
#        bus_lst.append(b)
#        
##TODO: put in function:
#pv_amount = int(round((len(bus_lst) * (pv_percentage/100)), 0))
#buses_with_pv = random.sample(bus_lst, pv_amount)
#
#hp_amount = int(round((len(bus_lst) * (hp_percentage/100)), 0))
#buses_with_hp = random.sample(bus_lst, hp_amount)
#
#bev_amount = int(round((len(bus_lst) * (bev_percentage/100)), 0))
#buses_with_bev = random.sample(bus_lst, bev_amount)
#
##Distribution of el storage is only done for houses with pv
#storage_amount = int(round((len(buses_with_pv) * (storage_percentage/100)), 0))
#buses_with_storage = random.sample(buses_with_pv, storage_amount)
#%% assign names and types to baseloads für later p and q assignment

for bus in net.bus.index:
    
    net.load.name[net.load.bus == bus] = net.bus.name[bus]+'_baseload'
    net.load.type[net.load.bus == bus] = 'baseload'

#%% create components and assign components to the Virtual Powerplant

for bus in buses_with_pv:
    
    vpp.addComponent(VPPPhotovoltaic(timebase=timebase, identifier=(bus+'_PV'), 
                                     latitude=latitude, longitude=longitude, 
                                     environment = None, userProfile = None,
                                     start = start, end = end,
                                     module_lib = 'SandiaMod', module = 'Canadian_Solar_CS5P_220M___2009_', 
                                     inverter_lib = 'cecinverter', inverter = 'ABB__PVI_4_2_OUTD_S_US_Z_M_A__208_V__208V__CEC_2014_',
                                     surface_tilt = 20, surface_azimuth = 200,
                                     modules_per_string = 4, strings_per_inverter = 2))
    
    vpp.components[list(vpp.components.keys())[-1]].prepareTimeSeries(weather_data)
    
    
for bus in buses_with_storage:
    
    vpp.addComponent(VPPEnergyStorage(timebase = timebase, 
                                      identifier=(bus+'_storage'), capacity=capacity, 
                                      chargeEfficiency=chargeEfficiency, 
                                      dischargeEfficiency=dischargeEfficiency, 
                                      maxPower=maxPower, maxC=maxC, 
                                      environment = None, userProfile = None))
    
    vpp.components[list(vpp.components.keys())[-1]].timeseries = pd.DataFrame(columns=['state_of_charge','residual_load'], index=pd.date_range(start=start, end=end, freq=time_freq))
    
    
for bus in buses_with_bev:
    
    vpp.addComponent(VPPBEV(timebase=timebase, identifier=(bus+'_BEV'),
                            start = start, end = end, time_freq = time_freq, 
                            battery_max = 16, battery_min = 0, battery_usage = 1, 
                            charging_power = 11, chargeEfficiency = 0.98, 
                            environment=None, userProfile=None))
    
    vpp.components[list(vpp.components.keys())[-1]].prepareTimeSeries()
    
    
for bus in buses_with_hp:
    
    vpp.addComponent(VPPHeatPump(identifier=(bus+'_HP'), timebase=timebase, heatpump_type="Air", 
                                 heat_sys_temp=60, environment=None, userProfile=None, 
                                 heatpump_power=5, full_load_hours=2100, 
                                 building_type = 'DE_HEF33', start=start,
                                 end=end, year = year))
    
    vpp.components[list(vpp.components.keys())[-1]].prepareTimeSeries()

#%% create elements in the pandapower.net

for bus in buses_with_pv:
    
    pp.create_sgen(net, bus=net.bus[net.bus.name == bus].index[0], 
                  p_mw=(vpp.components[bus+'_PV'].module.Impo*vpp.components[bus+'_PV'].module.Vmpo/1000000),
                  name=(bus+'_PV'), type = 'PV')    

for bus in buses_with_storage:
    
    pp.create_storage(net, bus=net.bus[net.bus.name == bus].index[0],
                      p_mw=0, max_e_mwh=capacity, name=(bus+'_storage'), type='LiIon')
  
for bus in buses_with_bev:
    
    pp.create_load(net, bus=net.bus[net.bus.name == bus].index[0], 
                   p_mw=(vpp.components[bus+'_BEV'].charging_power/1000), name=(bus+'_BEV'), type='BEV')
    
for bus in buses_with_hp:
    
    pp.create_load(net, bus=net.bus[net.bus.name == bus].index[0], 
                   p_mw=(vpp.components[bus+'_HP'].heatpump_power/1000), name=(bus+'_HP'), type='HP')
    
#%% assign values of generation/demand over time and run powerflow

net_dict = {}
res_loads = pd.DataFrame(columns=[net.bus.index[net.bus.type == 'b']], index=pd.date_range(start=start, end=end, freq=time_freq)) #maybe only take buses with storage
state_of_charge_df = pd.DataFrame(columns=[net.bus.index[net.bus.type == 'b']], index=pd.date_range(start=start, end=end, freq=time_freq))

#for idx in vpp.components[next(iter(vpp.components))].timeseries.index:
for idx in index:
    for component in vpp.components.keys():

        if 'storage' not in component:
            
            valueForTimestamp = vpp.components[component].valueForTimestamp(str(idx))
            
            if math.isnan(valueForTimestamp):
                traceback.print_exc("The value of ", component, "at timestep ", idx, "is NaN!")
        
        if component in list(net.sgen.name):
            
            net.sgen.p_mw[net.sgen.name == component] = valueForTimestamp/-1000 #kW to MW; negative due to generation
        
        if component in list(net.load.name):
            
            net.load.p_mw[net.load.name == component] = valueForTimestamp/1000 #kW to MW
        
    
    for name in net.load.name:
    
        if net.load.type[net.load.name == name].item() == 'baseload':
        
            net.load.p_mw[net.load.name == name] = baseload[str(net.load.bus[net.load.name == name].item())][str(idx)]/1000000
        
    if len(buses_with_storage) > 0: 
        for bus in net.bus.index[net.bus.type == 'b']:
        
            storage_at_bus = pp.get_connected_elements(net, "storage", bus)
            sgen_at_bus = pp.get_connected_elements(net, "sgen", bus)
            load_at_bus = pp.get_connected_elements(net, "load", bus)
            
            if len(storage_at_bus) > 0:
                res_loads.loc[idx][bus] = sum(net.load.loc[load_at_bus].p_mw) +  sum(net.sgen.loc[sgen_at_bus].p_mw)
                #set loads and sgen to 0 since they are in res_loads now
                #reassign values after operate_storage has been executed
                for l in list(load_at_bus):
                    net.load.p_mw[net.load.index == l]=0
                    
                for l in list(sgen_at_bus):
                    net.sgen.p_mw[net.sgen.index == l]=0
                
                
                #run storage operation with residual load
                state_of_charge, res_load = vpp.components[net.storage.loc[storage_at_bus].name.item()].operate_storage(res_loads.loc[idx][bus].item())
                
                #save state of charge and residual load in timeseries
                vpp.components[net.storage.loc[storage_at_bus].name.item()].timeseries['state_of_charge'][idx] = state_of_charge # state_of_charge_df[idx][bus] = state_of_charge
                vpp.components[net.storage.loc[storage_at_bus].name.item()].timeseries['residual_load'][idx] = res_load
                
                #assign new residual load to loads and sgen depending on positive/negative values
                if res_load >0:

                    if len(load_at_bus) >0:
                        #TODO: load according to origin of demand (baseload, hp or bev)
                        load_bus = load_at_bus.pop()
                        net.load.p_mw[net.load.index == load_bus] = res_load
                        
                    else:
                        #assign new residual load to storage
                        storage_bus = storage_at_bus.pop()
                        net.storage.p_mw[net.storage.index == storage_bus] = res_load
                
                else:

                    if len(sgen_at_bus) >0:
                        #TODO: assign generation according to origin of energy (PV oder CHP)
                        gen_bus = sgen_at_bus.pop()
                        net.sgen.p_mw[net.sgen.index == gen_bus] = res_load
                        
                    else:
                        #assign new residual load to storage
                        storage_bus = storage_at_bus.pop()
                        net.storage.p_mw[net.storage.index == storage_bus] = res_load
                
    
    pp.runpp(net)
    
    net_dict[idx] = {}
    net_dict[idx]['res_bus'] = net.res_bus
    net_dict[idx]['res_line'] = net.res_line
    net_dict[idx]['res_trafo'] = net.res_trafo
    net_dict[idx]['res_load'] = net.res_load
    net_dict[idx]['res_sgen'] = net.res_sgen
    net_dict[idx]['res_ext_grid'] = net.res_ext_grid
    net_dict[idx]['res_storage'] = net.res_storage
    

#%% extract results from powerflow
def extractResults(net_dict):
    
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

    if len(line_loading_percent.columns) >0:
        line_loading_percent = line_loading_percent.T
        line_loading_percent.rename(net['line'].name, axis='columns', inplace=True)
    
    if len(bus_vm_pu.columns) >0:
        bus_vm_pu = bus_vm_pu.T
        bus_vm_pu.rename(net.bus.name, axis='columns', inplace=True)
        
    trafo_loading_percent = trafo_loading_percent.T
    
    if len(sgen_p_mw.columns) >0:
        sgen_p_mw = sgen_p_mw.T
        sgen_p_mw.rename(net.sgen.name, axis='columns', inplace=True)
    
    if len(load_p_mw.columns) >0:
        load_p_mw = load_p_mw.T
        load_p_mw.rename(net.load.name, axis='columns', inplace=True)
    
    if len(storage_p_mw.columns) >0:
        storage_p_mw = storage_p_mw.T
        storage_p_mw.rename(net.storage.name, axis='columns', inplace=True)
        
        
    return ext_grid, line_loading_percent, bus_vm_pu, trafo_loading_percent, sgen_p_mw, load_p_mw, storage_p_mw


ext_grid, line_loading_percent, bus_vm_pu, trafo_loading_percent, gen_p_mw, load_p_mw, storage_p_mw = extractResults(net_dict)

trafo_loading_percent.plot(figsize=(16,9), title='trafo_loading_percent')
line_loading_percent.plot(figsize=(16,9), title='line_loading_percent')
bus_vm_pu.plot(figsize=(16,9), title='bus_vm_pu')
load_p_mw.plot(figsize=(16,9), title='load_p_mw')

if len(buses_with_pv) > 0:
    gen_p_mw.plot(figsize=(16,9), title='gen_p_mw')
    
if len(buses_with_storage) > 0:
    storage_p_mw.plot(figsize=(16,9), title='storage_p_mw')
    res_loads.plot(figsize=(16,9), title='res_loads')

#%%

def plot_storages(vpp):
    for comp in vpp.components.keys():
        if 'storage' in comp:
            vpp.components[comp].timeseries.plot(figsize=(16,9), title=comp)
            
plot_storages(vpp)

#%% extract results of single component categories

def extract_ext_grid(net_dict):
    
    ext_grid = pd.DataFrame()
    
    for idx in net_dict.keys():
        
        ext_grid = ext_grid.append(net_dict[idx]['res_ext_grid'], ignore_index=True)
        
        
    return ext_grid


def extract_line(net_dict):
    
    line = pd.DataFrame()
    
    for idx in net_dict.keys():
        
        line[idx] = net_dict[idx]['res_line'].loading_percent
    
    line = line.T
    
    return line


def extract_bus(net_dict):
    
    bus = pd.DataFrame()
    
    for idx in net_dict.keys():
        
        bus[idx] = net_dict[idx]['res_bus'].vm_pu
        
    bus = bus.T
    
    return bus


def extract_trafo(net_dict):
    
    trafo_loading_percent = pd.DataFrame()
    
    for idx in net_dict.keys():
        
        trafo_loading_percent[idx] = net_dict[idx]['res_trafo'].loading_percent
    
    trafo_loading_percent = trafo_loading_percent.T
    
    return trafo_loading_percent

def extract_load(net_dict):
    
    load_p_mw = pd.DataFrame()
    
    for idx in net_dict.keys():
        
        load_p_mw[idx] = net_dict[idx]['res_load'].p_mw
    
    load_p_mw = load_p_mw.T
    
    return load_p_mw
