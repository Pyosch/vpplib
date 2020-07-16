# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 15:16:35 2020

@author: sbirk

Run powerflow with el profiles from fzj, to generate basic load profiles for
MV buses without detailed lv grid attached

"""

import simbench as sb
import pandapower as pp

import pickle
import pandas as pd
import random

from vpplib import Operator

start = "2015-03-01 00:00:00"
end = "2015-03-01 23:45:00"

with open(r'Results/20200714_el_dict_15min.pickle', 'rb') as handle:
    el_dict = pickle.load(handle)

for load in el_dict.keys():
    el_dict[load]['Sum [kWh]'] *= 4 #  Convert kWh to kW
    el_dict[load].columns = ['kW'] #  Rename columns from kWh to kW

net = sb.get_simbench_net("1-MVLV-semiurb-all-0-sw")
print(net)

# calculate the absolute values:
loadcases = sb.get_absolute_values(net, profiles_instead_of_study_cases=True)

# define a function to apply absolute values
def apply_absolute_values(net, absolute_values_dict, case_or_time_step):
    for elm_param in absolute_values_dict.keys():
        if absolute_values_dict[elm_param].shape[1]:
            elm = elm_param[0]
            param = elm_param[1]
            net[elm].loc[:, param] = absolute_values_dict[elm_param].loc[case_or_time_step]

#apply_absolute_values(net, profiles, time_step)

operator = Operator(virtual_power_plant=None, net=net, target_data=None)

# plot the grid
pp.plotting.simple_plot(net)

net_dict = dict()

# assign fzj profiles to existing loads
for index in net.load.index:
    if "LV" in index:
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
                    ].item()/1000 #  Convert loadprofile to MWh for pandapower

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
