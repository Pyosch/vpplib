# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 15:16:35 2020

@author: sbirk
"""

import simbench as sb
import pandapower as pp

import pickle
import pandas as pd
import random

start = "2015-03-01 00:00:00"
end = "2015-03-01 23:45:00"

with open(r'Results/thermal_dict.pickle', 'rb') as handle:
    thermal_dict = pickle.load(handle)

with open(r'Results/el_dict_2015.pickle', 'rb') as handle:
    el_dict = pickle.load(handle)
    

net = sb.get_simbench_net("1-LV-semiurb4--0-sw")
print(net)

# plot the grid
pp.plotting.simple_plot(net)

net_dict = dict()

# assign fzj profiles to existing loads
for index in net.load.index:
    net.load.profile[index] = random.sample(el_dict.keys(), 1)[0]

for idx in pd.date_range(start=start, end=end, freq="15 Min"):
    for load in net.load.index:
        net.load.p_mw[load] = el_dict[
            net.load.iloc[
                load
                ].profile
            ].loc[
                idx
                ].item()/1000

        net.load.q_mvar[load] = 0

    for sgen in net.sgen.index:
        net.sgen.p_mw[sgen] = 0
        net.sgen.q_mvar[sgen] = 0

    pp.runpp(net)

    net_dict[idx] = {}
    net_dict[idx]["res_bus"] = net.res_bus
    net_dict[idx]["res_line"] = net.res_line
    net_dict[idx]["res_trafo"] = net.res_trafo
    net_dict[idx]["res_load"] = net.res_load
    net_dict[idx]["res_sgen"] = net.res_sgen
    net_dict[idx]["res_ext_grid"] = net.res_ext_grid
    net_dict[idx]["res_storage"] = net.res_storage


#%%extract results

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
        net["line"].name, axis="columns", inplace=True
    )
    line_loading_percent.index = pd.to_datetime(
        line_loading_percent.index
    )

if len(bus_vm_pu.columns) > 0:
    bus_vm_pu = bus_vm_pu.T
    bus_vm_pu.rename(net.bus.name, axis="columns", inplace=True)
    bus_vm_pu.index = pd.to_datetime(bus_vm_pu.index)

trafo_loading_percent = trafo_loading_percent.T
trafo_loading_percent.index = pd.to_datetime(
    trafo_loading_percent.index
)
if net.trafo.name is not None:
    trafo_loading_percent.rename(
        net.trafo.name, axis="columns", inplace=True
    )

if len(sgen_p_mw.columns) > 0:
    sgen_p_mw = sgen_p_mw.T
    sgen_p_mw.rename(net.sgen.name, axis="columns", inplace=True)
    sgen_p_mw.index = pd.to_datetime(sgen_p_mw.index)

if len(load_p_mw.columns) > 0:
    load_p_mw = load_p_mw.T
    load_p_mw.rename(net.load.name, axis="columns", inplace=True)
    load_p_mw.index = pd.to_datetime(load_p_mw.index)

if len(storage_p_mw.columns) > 0:
    storage_p_mw = storage_p_mw.T
    storage_p_mw.rename(
        net.storage.name, axis="columns", inplace=True
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