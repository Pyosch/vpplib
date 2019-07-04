# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 10:38:17 2019

@author: Sascha Birk
"""

import pandas as pd
import math
import pandapower as pp
import pandapower.networks as pn
from model.VPPPhotovoltaic import VPPPhotovoltaic

latitude = 50.941357
longitude = 6.958307
name = 'pv1'

weather_data = pd.read_csv("./Input_House/PV/20170601_irradiation_15min.csv")
weather_data.set_index("index", inplace = True)

pv = VPPPhotovoltaic(timebase=1, identifier=name, latitude=latitude, longitude=longitude, modules_per_string=1, strings_per_inverter=1)

pv.prepareTimeSeries(weather_data)

net = pn.create_kerber_landnetz_kabel_2()
pp.create_gen(net, bus=3, p_mw= (pv.module.Vmpo*pv.module.Impo/1000000), vm_pu = 1.0, name=pv.identifier)




def saveAllOfNet(net, pv):
    
    net_dict = {}
    for pv_gen, idx in zip(pv.timeseries[pv.identifier], pv.timeseries.index):
        
        if math.isnan(pv_gen):
            pv_gen = 0
            
        net.gen.p_mw[net.gen.name == pv.identifier] = pv_gen/-1000000 #W to MW; negative due to Generation
        pp.runpp(net)
        net_dict[idx] = net
        
    return net_dict

#net_dict = saveAllOfNet(net, pv)
##access dictionary    
#net_dict[pv.timeseries.index[48]].res_line

def saveNetRes(net, pv):
    
    net_dict = {}
    for pv_gen, idx in zip(pv.timeseries[pv.identifier], pv.timeseries.index):
        
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

net_dict = saveNetRes(net, pv)
##access dictionary    
net_dict[pv.timeseries.index[48]]['res_line']