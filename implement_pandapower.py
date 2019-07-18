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
from model.VirtualPowerPlant import VirtualPowerPlant

latitude = 50.941357
longitude = 6.958307
name = 'pv1'

weather_data = pd.read_csv("./Input_House/PV/20170601_irradiation_15min.csv")
weather_data.set_index("index", inplace = True)

"""
Create virtual Powerplant:
"""
#%% create instance of VirtualPowerPlant and the designated grid
vpp = VirtualPowerPlant("Master")

net = pn.create_kerber_landnetz_kabel_2()

#%% define the amount of components in the grid

pv_percentage = 100
storage_percentage = 0
bev_percentage = 0
hp_percentage = 0
#%% initialize components

pv = VPPPhotovoltaic(timebase=1, identifier=name, latitude=latitude, longitude=longitude, modules_per_string=1, strings_per_inverter=1)
pv.prepareTimeSeries(weather_data)

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

#%% create components and assign components to the Virtual Powerplant

for bus in buses_with_pv:
    
    vpp.addComponent(VPPPhotovoltaic(timebase=1, identifier=(bus + "_PV"), 
                                     latitude=latitude, longitude=longitude, 
                                     modules_per_string=1, strings_per_inverter=1))
    
    vpp.components[list(vpp.components.keys())[-1]].prepareTimeSeries(weather_data)
    
    #access dictionary keys via: vpp.components.keys()
    #access elements: vpp.components['KV_1_2_PV'].prepareTimeSeries(weather_data)
    
#%% create generators in the pandapower.net

for bus in buses_with_pv:
    
    pp.create_gen(net, bus=net.bus[net.bus.name == bus].index[0], p_mw=(pv.module.Vmpo*pv.module.Impo/1000000), vm_pu = 1.0, name=(bus+'_PV'))
  
#%% assign values of generation over time and run powerflow

net_dict = {}
for idx in vpp.components[next(iter(vpp.components))].timeseries.index:
    for component in vpp.components.keys():

        valueForTimestamp = vpp.components[component].valueForTimestamp(idx)
        
        if math.isnan(valueForTimestamp):
            valueForTimestamp = 0
            
        net.gen.p_mw[net.gen.name == component] = valueForTimestamp/-1000000 #W to MW; negative due to generation
        
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
    
    for idx in net_dict.keys():
        
        ext_grid = ext_grid.append(net_dict[idx]['res_ext_grid'], ignore_index=True)
        line_loading_percent[idx] = net_dict[idx]['res_line'].loading_percent
        bus_vm_pu[idx] = net_dict[idx]['res_bus'].vm_pu
        trafo_loading_percent[idx] = net_dict[idx]['res_trafo'].loading_percent
        gen_p_mw[idx] = net_dict[idx]['res_gen'].p_mw
    

    line_loading_percent = line_loading_percent.T
    bus_vm_pu = bus_vm_pu.T
    trafo_loading_percent = trafo_loading_percent.T
    gen_p_mw = gen_p_mw.T
        
    return ext_grid, line_loading_percent, bus_vm_pu, trafo_loading_percent, gen_p_mw


ext_grid, line_loading_percent, bus_vm_pu, trafo_loading_percent, gen_p_mw = extractResults(net_dict)

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


#%% basic powerflow implementations without VirtualPowerPlant class
    
"""
run powerflow and save results:
"""

def saveAllOfNet(net, pv):
    
    net_dict = {}
    for idx in pv.timeseries.index:
    
        pv_gen = pv.valueForTimestamp(idx)
        
        if math.isnan(pv_gen):
            pv_gen = 0
            
        net.gen.p_mw[net.gen.name == pv.identifier] = pv_gen/-1000000 #W to MW; negative due to Generation
        pp.runpp(net)
        net_dict[idx] = net
        
    return net_dict

#net_dict = saveAllOfNet(net, pv)
#access dictionary    
#net_dict[pv.timeseries.index[48]].res_line

def saveNetRes(net, pv):
    
    net_dict = {}
    for idx in pv.timeseries.index:
    
        pv_gen = pv.valueForTimestamp(idx)
        
        if math.isnan(pv_gen):
            pv_gen = 0
            
        net.gen.p_mw[net.gen.name == pv.identifier] = pv_gen/-1000000 #W to MW; negative due to Generation
        pp.runpp(net)
        
        net_dict[idx] = {}
        net_dict[idx]['res_bus'] = net.res_bus
        net_dict[idx]['res_line'] = net.res_line
        net_dict[idx]['res_trafo'] = net.res_trafo
        net_dict[idx]['res_load'] = net.res_load
        net_dict[idx]['res_ext_grid'] = net.res_ext_grid
    
    return net_dict

#net_dict = saveNetRes(net, pv)
##access dictionary    
#net_dict[pv.timeseries.index[48]]['res_line']
