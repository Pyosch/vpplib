# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 10:38:17 2019

@author: Sascha Birk
"""

import pandas as pd
import math
import random
import pandapower as pp
import pandapower.networks as pn
from model.VPPPhotovoltaic import VPPPhotovoltaic
from model.VPPBEV import VPPBEV
from model.VirtualPowerPlant import VirtualPowerPlant

latitude = 50.941357
longitude = 6.958307
#name = 'pv1'

start = '2017-06-01 00:00:00'
end = '2017-06-01 23:45:00'
time_freq = "15 min"

weather_data = pd.read_csv("./Input_House/PV/20170601_irradiation_15min.csv")
weather_data.set_index("index", inplace = True)

baseload = pd.read_csv("./Input_House/Base_Szenario/df_S_15min.csv")
baseload.set_index("Time", inplace=True)

"""
Create virtual Powerplant:
"""
#%% create instance of VirtualPowerPlant and the designated grid
vpp = VirtualPowerPlant("Master")

net = pn.create_kerber_landnetz_kabel_2()

#%% define the amount of components in the grid

pv_percentage = 30
storage_percentage = 0
bev_percentage = 30
hp_percentage = 0

#%% assign components to the bus names

#TODO: put in function:
pv_amount = int(round((len(net.bus.name[net.bus.type == 'b']) * (pv_percentage/100)), 0))
buses_with_pv = random.sample(list(net.bus.name[net.bus.type == 'b']), pv_amount)

hp_amount = int(round((len(net.bus.name[net.bus.type == 'b']) * (hp_percentage/100)), 0))
buses_with_hp = random.sample(list(net.bus.name[net.bus.type == 'b']), hp_amount)

bev_amount = int(round((len(net.bus.name[net.bus.type == 'b']) * (bev_percentage/100)), 0))
buses_with_bev = random.sample(list(net.bus.name[net.bus.type == 'b']), bev_amount)

#Distribution of el storage is only done for houses with pv
storage_amount = int(round((len(buses_with_pv) * (storage_percentage/100)), 0))
buses_with_storage = random.sample(buses_with_pv, storage_amount)

#%% assign names and types to baseloads für later p and q assignment

for bus in net.bus.index:
    
    net.load.name[net.load.bus == bus] = net.bus.name[bus]+'_baseload'
    net.load.type[net.load.bus == bus] = 'baseload'

#%% create components and assign components to the Virtual Powerplant

for bus in buses_with_pv:
    
    vpp.addComponent(VPPPhotovoltaic(timebase=1, identifier=(bus+'_PV'), 
                                     latitude=latitude, longitude=longitude, 
                                     modules_per_string=1, strings_per_inverter=1))
    
    vpp.components[list(vpp.components.keys())[-1]].prepareTimeSeries(weather_data)
    
    #access dictionary keys via: vpp.components.keys()
    #access elements: vpp.components['KV_1_2_PV'].prepareTimeSeries(weather_data)
    

for bus in buses_with_bev:
    
    vpp.addComponent(VPPBEV(timebase=15/60, identifier=(bus+'_BEV'),
                            start = start, end = end, time_freq = time_freq, 
                            battery_max = 16, battery_min = 0, battery_usage = 1, 
                            charging_power = 11, chargeEfficiency = 0.98, 
                            environment=None, userProfile=None))
    
    vpp.components[list(vpp.components.keys())[-1]].prepareTimeSeries()

#%% create generators in the pandapower.net

for bus in buses_with_pv:
    
    pp.create_gen(net, bus=net.bus[net.bus.name == bus].index[0], 
                  p_mw=(vpp.components[bus+'_PV'].module.Impo*vpp.components[bus+'_PV'].module.Vmpo/1000000), 
                  vm_pu = 1.0, name=(bus+'_PV'))
  
for bus in buses_with_bev:
    
    pp.create_load(net, bus=net.bus[net.bus.name == bus].index[0], 
                   p_mw=(vpp.components[bus+'_BEV'].charging_power/1000), name=(bus+'_BEV'), type = 'BEV')
#%% assign values of generation/demand over time and run powerflow

net_dict = {}
for idx in vpp.components[next(iter(vpp.components))].timeseries.index:
    for component in vpp.components.keys():

        valueForTimestamp = vpp.components[component].valueForTimestamp(str(idx))
        
        if math.isnan(valueForTimestamp):
            valueForTimestamp = 0
        
        if component in list(net.gen.name):
            
            net.gen.p_mw[net.gen.name == component] = valueForTimestamp/-100 #W to MW; negative due to generation #TODO: Adjust inverter and moules
        
        if component in list(net.load.name):
            
            net.load.p_mw[net.load.name == component] = valueForTimestamp/1000
        
    
    for name in net.load.name:
    
        if net.load.type[net.load.name == name].item() == 'baseload': #adjust if type of baseload load changes; throws an ERR!!!
        
            net.load.p_mw[net.load.name == name] = baseload[str(net.load.bus[net.load.name == name].item())][str(idx)]/1000000
        
        
    pp.runpp(net)
    
    net_dict[idx] = {}
    net_dict[idx]['res_bus'] = net.res_bus
    net_dict[idx]['res_line'] = net.res_line
    net_dict[idx]['res_trafo'] = net.res_trafo
    net_dict[idx]['res_load'] = net.res_load
    net_dict[idx]['res_gen'] = net.res_gen
    net_dict[idx]['res_ext_grid'] = net.res_ext_grid
    
    #access single elements: net_dict[vpp.components[next(iter(vpp.components))].timeseries.index[48]]['res_gen']['p_mw'][0]
    

#%% extract results from powerflow
def extractResults(net_dict):
    
    ext_grid = pd.DataFrame()
    line_loading_percent = pd.DataFrame()
    bus_vm_pu = pd.DataFrame()
    trafo_loading_percent = pd.DataFrame()
    gen_p_mw = pd.DataFrame()
    load_p_mw = pd.DataFrame()
    
    for idx in net_dict.keys():
        
        ext_grid = ext_grid.append(net_dict[idx]['res_ext_grid'], ignore_index=True)
        line_loading_percent[idx] = net_dict[idx]['res_line'].loading_percent
        bus_vm_pu[idx] = net_dict[idx]['res_bus'].vm_pu
        trafo_loading_percent[idx] = net_dict[idx]['res_trafo'].loading_percent
        gen_p_mw[idx] = net_dict[idx]['res_gen'].p_mw
        load_p_mw[idx] = net_dict[idx]['res_load'].p_mw

    line_loading_percent = line_loading_percent.T
    bus_vm_pu = bus_vm_pu.T
    trafo_loading_percent = trafo_loading_percent.T
    gen_p_mw = gen_p_mw.T
    load_p_mw = load_p_mw.T
        
    return ext_grid, line_loading_percent, bus_vm_pu, trafo_loading_percent, gen_p_mw, load_p_mw


ext_grid, line_loading_percent, bus_vm_pu, trafo_loading_percent, gen_p_mw, load_p_mw = extractResults(net_dict)

trafo_loading_percent.plot()
line_loading_percent.plot()
bus_vm_pu.plot()
load_p_mw.plot()

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
