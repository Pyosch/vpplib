# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 08:24:21 2020

@author: sbirk

Reengineering a grid from EASE results if net object is lost
"""

import pandas as pd
import pickle
import sqlite3
from tqdm import tqdm
import random
import time
import os

import pandapower as pp
import simbench as sb

start = "2015-01-01 00:00:00"
end = "2015-12-31 23:45:00"

timestamp = "20200731-163950"
sql_file = r"./Results/"+timestamp+"/"+timestamp+"_vpp_export.sqlite"
net_load = pd.read_csv(r"./Results/"+timestamp+"/"+timestamp+"_net_load.csv", index_col=([0]))

with open(r'Results/20200714_el_dict_15min.pickle', 'rb') as handle:
    el_dict = pickle.load(handle)

for load in el_dict.keys():
    el_dict[load]['Sum [kWh]'] *= 4 #  Convert kWh to kW
    el_dict[load].columns = ['kW'] #  Rename columns from kWh to kW

connection = sqlite3.connect(sql_file)
components = pd.read_sql_query("select * from component_values;", connection)
connection.close()


#%% Simbench grid configuration

with open(r'Results/SimBench_grids/1-MVLV-semiurb-all-0-sw_1015_lvbuses.pickle', 'rb') as handle:
    net = pickle.load(handle)

# calculate the absolute values:
sb_profiles = sb.get_absolute_values(net, profiles_instead_of_study_cases=True)

net.load = net_load

drop_lst = list()
for idx in net.sgen.index:
    if 'PV' in net.sgen.type[idx]:
        drop_lst.append(idx)
    elif 'Wind_MV' in net.sgen.type[idx]:
        drop_lst.append(idx)   
    elif 'PV_MV' in net.sgen.type[idx]:
        drop_lst.append(idx)
net.sgen.drop(drop_lst, inplace=True)

# Shorten simbench profiles from 35136 (Schaltjahr) to 35040
# Delete February 29 -> (January + 28 days) * 96 Timesteps = 02-29 00:00:00
delete_from = (31+28)*96 #  2015-02-29 00:00:00
delete_to = (31+28)*96 + 95 #  2015-02-29 23:45:00
drop_list = list(range(delete_from, (delete_to + 1)))

print("Assigning new index to sb_profiles:")
for elm_param in tqdm(sb_profiles.keys()):
    if sb_profiles[elm_param].shape[1]:
        sb_profiles[elm_param] = sb_profiles[elm_param].drop(drop_list)
        # Change index to 0-35039
        # sb_profiles[elm_param].index = list(range(0, len(sb_profiles[elm_param])))
        sb_profiles[elm_param].index = el_dict[list(el_dict.keys())[0]].index

# Save fzj Profile name in simbench net.load and profile in sb_profiles for pf
# print("Combine FZJ and SimBench profiles:")
# for idx in tqdm(net.load.index):
#     if "LV" in net.load.name[idx]:
#         net.load.profile[idx] = random.sample(el_dict.keys(), 1)[0]
#         net.load.type[idx] = "baseload"

#     if net.load.profile[idx] in el_dict.keys():
#         sb_profiles[('load', 'p_mw')][idx] = el_dict[net.load.profile[idx]]/1000
#         sb_profiles[('load', 'q_mvar')][idx] = 0.0 #  F@***** never use 0!!

# Write ease components to grid
unassigned_lst = list()

print("Generating components in grid:")
for idx in tqdm(components.index):
    
    if "pv" in components.name[idx]:

        pp.create_sgen(
            net,
            bus=net.bus[net.bus.name == components.bus[idx]].index[0],
            p_mw=(
                components.power_kW[idx] / 1000
            ),
            q_mvar = 0,
            name=(components),
            type="pv",
        )

        sb_profiles[('sgen', 'p_mw')][net.sgen.index[-1]] = 0.0

    elif "wea" in components.name[idx]:

        pp.create_sgen(
            net,
            bus=net.bus[net.bus.name == components.bus[idx]].index[0],
            p_mw=(
                components.power_kW[idx] / 1000
            ),
            q_mvar = 0,
            name=(components.name[idx]),
            type="wea",
        )

        sb_profiles[('sgen', 'p_mw')][net.sgen.index[-1]] = 0.0

    elif "chp" in components.name[idx]:

        pp.create_sgen(
            net,
            bus=net.bus[net.bus.name == components.bus[idx]].index[0],
            p_mw=(
                components.power_kW[idx] / 1000
            ),
            q_mvar = 0,
            name=(components.name[idx]),
            type="chp",
        )

        sb_profiles[('sgen', 'p_mw')][net.sgen.index[-1]] = 0.0

    elif "hr" in components.name[idx]:

        pp.create_load(
            net,
            bus=net.bus[net.bus.name == components.bus[idx]].index[0],
            p_mw=(
                components.power_kW[idx] / 1000
            ),
            q_mvar = 0,
            name=(components.name[idx]),
            type="hr",
        )

        sb_profiles[('load', 'p_mw')][net.sgen.index[-1]] = 0.0
        sb_profiles[('load', 'q_mvar')][net.sgen.index[-1]] = 0.0

    elif "hp" in components.name[idx]:

        pp.create_load(
            net,
            bus=net.bus[net.bus.name == components.bus[idx]].index[0],
            p_mw=(
                components.power_kW[idx] / 1000
            ),
            q_mvar = 0,
            name=(components.name[idx]),
            type="hp",
        )

        sb_profiles[('load', 'p_mw')][net.sgen.index[-1]] = 0.0
        sb_profiles[('load', 'q_mvar')][net.sgen.index[-1]] = 0.0

    # if "tes" in up_dict[up_id].__dict__.keys():
    #     up_dict[up_id].tes.identifier = up_id+'_tes'
    #     vpp.add_component(up_dict[up_id].tes)
    #     # Thermal component, no equivalent in pandapower

    elif "ees" in components.name[idx]:

        pp.create_storage(
            net,
            bus=net.bus[net.bus.name == components.bus[idx]].index[0],
            p_mw=0,
            q_mvar = 0,
            max_e_mwh=components.capacity_kWh[idx] / 1000,
            name=(components.name[idx]),
            type="ees",
        )

        sb_profiles[('storage', 'p_mw')][net.sgen.index[-1]] = 0.0

    elif "bev" in components.name[idx]:

        pp.create_load(
            net,
            bus=net.bus[net.bus.name == components.bus[idx]].index[0],
            p_mw=(
                components.power_kW[idx] / 1000
            ),
            q_mvar = 0,
            name=(components.name[idx]),
            type="bev",
        )

        sb_profiles[('load', 'p_mw')][net.sgen.index[-1]] = 0.0
        sb_profiles[('load', 'q_mvar')][net.sgen.index[-1]] = 0.0

    else:
        unassigned_lst.append(components.name[idx])

#%% Save results

savety_timestamp = time.strftime("%Y%m%d-%H%M%S",time.localtime())

newpath = (r'./Results/'+savety_timestamp) 
if not os.path.exists(newpath):
    os.makedirs(newpath)

with open((r"./Results/"+savety_timestamp+"_net_export"+".pickle"),"wb") as handle:
    pickle.dump(net, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open((r"./Results/"+savety_timestamp+"_sb_profiles"+".pickle"),"wb") as handle:
    pickle.dump(sb_profiles, handle, protocol=pickle.HIGHEST_PROTOCOL)