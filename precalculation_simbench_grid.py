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
from tqdm import tqdm

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
sb_profiles = sb.get_absolute_values(net, profiles_instead_of_study_cases=True)

# MV sgens set to zero generation, so generators doesn't infuence MV loadprofiles
# get a list of mv sgen to set timeseries to 0
mv_sgen = list()
for idx in net.sgen.index:
    if "MV" in net.sgen["name"][idx]:
        # mv_sgen.append(idx)
        sb_profiles[('sgen', 'p_mw')][idx] = 0

# Shorten simbench profiles from 35136 (Schaltjahr) to 35040
# Delete February 29 -> (January + 28 days) * 96 Timesteps = 02-29 00:00:00
delete_from = (31+28)*96 #  2015-02-29 00:00:00
delete_to = (31+28)*96 + 95 #  2015-02-29 23:45:00
drop_list = list(range(delete_from, (delete_to + 1)))

for elm_param in tqdm(sb_profiles.keys(), desc="Assigning new index to sb_profiles"):
    if sb_profiles[elm_param].shape[1]:
        sb_profiles[elm_param] = sb_profiles[elm_param].drop(drop_list)
        # Change index to 0-35039
        # sb_profiles[elm_param].index = list(range(0, len(sb_profiles[elm_param])))
        sb_profiles[elm_param].index = el_dict[list(el_dict.keys())[0]].index

# Save fzj Profile name in simbench net.load
for idx in tqdm(net.load.index, desc="Writing FZJ profile names in net.load.profile"):
    if "LV" in net.load.name[idx]:
        net.load.profile[idx] = random.sample(el_dict.keys(), 1)[0]
        net.load.type[idx] = "baseload"

# Save fzj profiles in preconfigured simbench dict -> Result causes MEMORY ERROR!
# Solution?
for idx in tqdm(net.load.index, desc="Save fzj profiles in preconfigured simbench dict"):
    if net.load.profile[idx] in el_dict.keys():
        sb_profiles[('load', 'p_mw')][idx] = el_dict[net.load.profile[idx]]/1000

for idx in tqdm(net.load.index, desc="Set q_mvar to zero for lv"):
    if net.load.profile[idx] in el_dict.keys():
        sb_profiles[('load', 'q_mvar')][idx] = 0.0


# define a function to apply absolute simbench values
def apply_absolute_values(net, absolute_values_dict, case_or_time_step):
    for elm_param in absolute_values_dict.keys():
        if absolute_values_dict[elm_param].shape[1]:
            elm = elm_param[0]
            param = elm_param[1]
            net[elm].loc[:, param] = absolute_values_dict[elm_param].loc[case_or_time_step]

operator = Operator(virtual_power_plant=None, net=net, target_data=None)

# plot the grid
pp.plotting.simple_plot(net)

#%% Powerflow V1

# net_dict = dict()

# for idx in tqdm(pd.date_range(start=start, end=end, freq="15 Min"), desc="Powerflow calculation"):

#     apply_absolute_values(net, sb_profiles, idx)

#     for load in net.load.index:
#         if net.load.type[load] == "baseload":
#             net.load.p_mw[load] = el_dict[
#                 net.load.iloc[
#                     load
#                     ].profile
#                 ].loc[
#                     idx
#                     ].item()/1000 #  Convert loadprofile to MW for pandapower

#             net.load.q_mvar[load] = 0

#     for sgen in net.sgen.index:
#         net.sgen.p_mw[sgen] = 0
#         net.sgen.q_mvar[sgen] = 0

#     pp.runpp(net)

#     net_dict[idx] = {}
#     net_dict[idx]["res_bus"] = net.res_bus
#     net_dict[idx]["res_line"] = net.res_line
#     net_dict[idx]["res_trafo"] = net.res_trafo
#     net_dict[idx]["res_load"] = net.res_load
#     net_dict[idx]["res_sgen"] = net.res_sgen
#     net_dict[idx]["res_ext_grid"] = net.res_ext_grid
#     net_dict[idx]["res_storage"] = net.res_storage

#%% Powerflow V2

net_dict = dict()

for idx in tqdm(pd.date_range(start=start, end=end, freq="15 Min"), desc="Powerflow calculation"):

    apply_absolute_values(net, sb_profiles, idx)

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

# Plot results in long calculation times!!
#operator.plot_results(results, legend=False)

