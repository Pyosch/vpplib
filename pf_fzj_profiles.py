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

from vpplib import Operator

start = "2015-03-01 00:00:00"
end = "2015-03-01 23:45:00"

with open(r'Results/thermal_dict.pickle', 'rb') as handle:
    thermal_dict = pickle.load(handle)

with open(r'Results/el_dict_2015.pickle', 'rb') as handle:
    el_dict = pickle.load(handle)
    

net = sb.get_simbench_net("1-LV-semiurb4--0-sw")
print(net)

operator = Operator(virtual_power_plant=None, net=net, target_data=None)

# plot the grid
pp.plotting.simple_plot(net)

net_dict = dict()

# assign fzj profiles to existing loads
for index in net.load.index:
    net.load.profile[index] = random.sample(el_dict.keys(), 1)[0]
    net.load.type[index] = "baseload"

for idx in pd.date_range(start=start, end=end, freq="15 Min"):
    for load in net.load.index:
        if net.load.type[load] == "baseload":
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

results = operator.extract_results(net_dict)
