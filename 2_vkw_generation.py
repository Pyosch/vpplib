# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 15:35:09 2020

Generate a virtual power plant based on predefined user_profiles

Export timeseries and component values to sql at the end
Save vpp and corresponding grid to pickle

@author: pyosch
"""

import pandas as pd
import random
import time
import pickle
from tqdm import tqdm
import copy
import os

import simbench as sb
import pandapower as pp

from vpplib import VirtualPowerPlant, Environment, UserProfile
from vpplib import Photovoltaic, WindPower

# define virtual power plant
#2015
# nr_bev = 0
# nr_ahp = 13
# nr_whp = 10
# nr_hp = nr_whp + nr_ahp
# nr_chp = 1
# nr_pv = 186
# nr_storage = 40

#2030
nr_bev = 316
nr_ahp = 246
nr_whp = 97
nr_hp = nr_whp + nr_ahp
nr_chp = 8
nr_pv = 557
nr_storage = 250

# Values for environment
start = "2015-04-01 00:00:00"
end = "2015-04-01 23:45:00"
year = "2015"
time_freq = "15 min"
index_year = pd.date_range(
    start=year, periods=35040, freq=time_freq, name="time"
)
index_hours = pd.date_range(start=start, end=end, freq="h", name="time")
timebase = 15  # for calculations from kW to kWh
timezone="Europe/Berlin"

# UserProfile data
latitude = 50.941357
longitude = 6.958307

# WindTurbine data
fetch_curve = "power_curve"
data_source = "oedb"

# ModelChain data
# possible wind_speed_model: 'logarithmic', 'hellman',
#'interpolation_extrapolation', 'log_interpolation_extrapolation'
wind_speed_model = "logarithmic"
density_model = "ideal_gas"
temperature_model = "linear_gradient"
power_output_model = "power_coefficient_curve"  #'power_curve'
density_correction = True
obstacle_height = 0
hellman_exp = None

# Values for bev
# power and capacity will be randomly assigned during component generation
battery_min = 4
battery_usage = 1
bev_charge_efficiency = 0.98
load_degradation_begin = 0.8

#%% load dicts with electrical and thermal profiles
with open(r'Results/20200730-151519_up_dena_profiles.pickle', 'rb') as handle:
    user_profiles_dict = pickle.load(handle)

print(time.asctime( time.localtime(time.time()) ))
print("Loaded input\n")

#%% SimBench Grids


# Simbench Network parameters
# Preconfigured Grid:
with open(r'Results/SimBench_grids/1-MVLV-semiurb-all-0-sw_1015_lvbuses.pickle', 'rb') as handle:
    net = pickle.load(handle)

# Standard SimBench grid:
# sb_code = "1-LV-semiurb5--0-sw" #"1-MVLV-semiurb-all-0-sw" # "1-MVLV-semiurb-5.220-0-sw" #
# net = sb.get_simbench_net(sb_code)

# plot the grid
# pp.plotting.simple_plot(net)

# drop preconfigured electricity generators  and loads from the grid
# net.sgen.drop(net.sgen.index, inplace = True)
# net.load.drop(net.load.index, inplace = True)

# Get preconfigured SimBench profiles:
sb_profiles = sb.get_absolute_values(net, profiles_instead_of_study_cases=True)

# sb_profiles[('load', 'p_mw')]
# ('load', 'q_mvar')
# ('sgen', 'p_mw')
# ('gen', 'p_mw')
# ('storage', 'p_mw')

# Shorten simbench profiles from 35136 (Schaltjahr) to 35040
# Delete February 29 -> (January + 28 days) * 96 Timesteps = 02-29 00:00:00
delete_from = (31+28)*96 #  2015-02-29 00:00:00
delete_to = (31+28)*96 + 95 #  2015-02-29 23:45:00
drop_list = list(range(delete_from, (delete_to + 1)))

print("Assigning new index to sb_profiles:")
for elm_param in tqdm(sb_profiles.keys()):
    if sb_profiles[elm_param].shape[0]:
        sb_profiles[elm_param] = sb_profiles[elm_param].drop(drop_list)

        sb_profiles[elm_param].index = user_profiles_dict[
            list(user_profiles_dict.keys())[0]
            ].electric_energy_demand.index

# Initialize Index for storage timeseries
sb_profiles[('storage', 'p_mw')] = pd.DataFrame(index = user_profiles_dict[
            list(user_profiles_dict.keys())[0]
            ].electric_energy_demand.index)

#%% Adjust the values of the environments in the user_profiles_dict with the
#   current values. Since the environment is stored in one place
#   (eg. 0x158c9b24c08) and all components have the same, it only has to be
#   changed once!

user_profiles_dict[list(user_profiles_dict.keys())[0]].environment.start = start
user_profiles_dict[list(user_profiles_dict.keys())[0]].environment.end = end
user_profiles_dict[list(user_profiles_dict.keys())[0]].environment.timebase = timebase
user_profiles_dict[list(user_profiles_dict.keys())[0]].environment.timezone = timezone
user_profiles_dict[list(user_profiles_dict.keys())[0]].environment.year = year
user_profiles_dict[list(user_profiles_dict.keys())[0]].environment.time_freq = time_freq

# get data for timeseries calculations
user_profiles_dict[list(user_profiles_dict.keys())[0]].environment.get_mean_temp_days()
user_profiles_dict[list(user_profiles_dict.keys())[0]].environment.get_mean_temp_hours()
user_profiles_dict[list(user_profiles_dict.keys())[0]].environment.get_pv_data()
user_profiles_dict[list(user_profiles_dict.keys())[0]].environment.get_wind_data()

#%% Get timeseries of the households

for house in user_profiles_dict.keys():
    if "pv" in list(user_profiles_dict[house].__dict__.keys()):
        user_profiles_dict[house].pv.prepare_time_series()
        
        # TODO
        # Somehow in some pvlib timeseries the inverter losses during night hours
        # are not complete. Once we find out how to solve this problem we can
        # delete this part:
        if user_profiles_dict[house].pv.timeseries.isnull().values.any():
                user_profiles_dict[house].pv.timeseries.fillna(
                    value=0,
                    inplace=True)
                
    if "chp" in list(user_profiles_dict[house].__dict__.keys()):
        user_profiles_dict[house].chp.reset_time_series()

    if "bev" in list(user_profiles_dict[house].__dict__.keys()):
        user_profiles_dict[house].bev.timeseries = pd.DataFrame(
            index = pd.date_range(
                start=user_profiles_dict[house].bev.environment.start,
                end=user_profiles_dict[house].bev.environment.end,
                freq=user_profiles_dict[house].bev.environment.time_freq,
                name="Time",
            )
        )

        user_profiles_dict[house].bev.split_time()
        user_profiles_dict[house].bev.set_weekday()
        user_profiles_dict[house].bev.set_at_home()
        user_profiles_dict[house].bev.timeseries["at_home"] = user_profiles_dict[house].bev.at_home["at home"]

# %% virtual power plant

vpp = VirtualPowerPlant("vpp")

print(time.asctime(time.localtime(time.time())))
print("Initialized environment, vpp and net\n")

#%% Assign new pv profiles to existing pv plants in lv grid

environment = Environment(
    timebase=timebase,
    timezone="Europe/Berlin",
    start=start,
    end=end,
    year=year,
    time_freq=time_freq,
)

environment.get_pv_data()
environment.get_wind_data()

print("Reassign generation to existing sgen:")
for idx in tqdm(net.sgen.index):
    # if "LV" in net.sgen.name[idx]:
    #TODO: Save SimBench user_profiles in up_dict
    #(does not influence export in vpp,
    #just in case, up_dict is needed again)
    user_profile = UserProfile(
        identifier=net.sgen.name[idx],
        latitude=latitude,
        longitude=longitude,
        thermal_energy_demand_yearly=None,
        building_type=None,
        comfort_factor=None,
        t_0=None,
        daily_vehicle_usage=None,
        week_trip_start=[],
        week_trip_end=[],
        weekend_trip_start=[],
        weekend_trip_end=[],
    )
    # Bus name is saved during export in vpp
    user_profile.bus = net.bus.name[net.sgen.bus[idx]]

    if "PV" in net.sgen.type[idx]:

        pv = Photovoltaic(module_lib="SandiaMod",
                      inverter_lib="SandiaInverter",
                      surface_tilt = random.randrange(start=20, stop=40, step=5),
                      surface_azimuth = random.randrange(start=160, stop=220, step=10),
                      unit="kW",
                      identifier=(net.sgen.name[idx]+'_pv'),
                      environment=environment,
                      user_profile=user_profile,
                      cost=None)

        pv.pick_pvsystem(
              min_module_power = 100,
              max_module_power = 200,
              pv_power = net.sgen.p_mw[idx]*1000000, # Watt
              inverter_power_range = 100)


        # Create timeseries for pv
        pv.prepare_time_series()

        # TODO
        # Somehow in some pvlib timeseries the inverter losses during night hours
        # are not complete. Once we find out how to solve this problem we can
        # delete this part:
        if pv.timeseries.isnull().values.any():
                pv.timeseries.fillna(
                    value=0,
                    inplace=True)

        #TODO: Find out why this pv generators profile is wrong
        if net.sgen.name[idx] == "MV2.101 MV SGen 9":
            pv.timeseries *= -1

        # Add profile to simbench profiles
        sb_profiles[("sgen", "p_mw")][idx] = pv.timeseries

        # Add Componentn in vpp
        vpp.add_component(pv)

        if "LV" in net.sgen.name[idx]:
            nr_pv -= 1


    elif "Wind" in net.sgen.type[idx]:
#wea = windpowerlib.wind_turbine.load_turbine_data_from_oedb(schema='supply', table='wind_turbine_library')
#wea.sort_values(by=["nominal_power"], ignore_index=True).iloc[3]
        if net.sgen.p_mw[idx] == 1.5:
            # turbine_type = "VS82/1500" # no power_curve
            # hub_height = 85
            # rotor_diameter = 82
            turbine_type = "V100/1800"
            hub_height = 85
            rotor_diameter = 100

        elif net.sgen.p_mw[idx] == 1.7:
            turbine_type = "V100/1800"
            hub_height = 85
            rotor_diameter = 100

        elif net.sgen.p_mw[idx] == 1.8:
            turbine_type = "V100/1800"
            hub_height = 85
            rotor_diameter = 100

        elif net.sgen.p_mw[idx] == 2.0:
            turbine_type = "E-82/2000"
            hub_height = 85
            rotor_diameter = 82

        elif net.sgen.p_mw[idx] == 2.1:
            turbine_type = "ENO100/2200"
            hub_height = 99
            rotor_diameter = 100

        wind = WindPower(
            unit="kW",
            identifier=(net.sgen.name[idx]+"_wea"),
            environment=environment,
            user_profile=user_profile,
            turbine_type=turbine_type,
            hub_height=hub_height,
            rotor_diameter=rotor_diameter,
            fetch_curve=fetch_curve,
            data_source=data_source,
            wind_speed_model=wind_speed_model,
            density_model=density_model,
            temperature_model=temperature_model,
            power_output_model=power_output_model,
            density_correction=density_correction,
            obstacle_height=obstacle_height,
            hellman_exp=hellman_exp,
        )

        wind.prepare_time_series()

        # Add profile to simbench profiles
        sb_profiles[("sgen", "p_mw")][idx] = wind.timeseries

        # Add Componentn in vpp
        vpp.add_component(wind)


#%% helper functions

def add_pv(up_id, up_dict, vpp, net, sb_profiles):
    up_dict[up_id].pv.identifier = up_id+'_pv'
    
    vpp.add_component(up_dict[up_id].pv)
    # Adjust column name of timeseries to match new identifier of 
    # component
    vpp.components[
        up_dict[up_id].pv.identifier
        ].timeseries.columns = [
            vpp.components[
                up_dict[up_id].pv.identifier].identifier]

    pp.create_sgen(
        net,
        bus=net.bus[net.bus.name == bus].index[0], #TODO: use net.load.bus[load_idx]
        p_mw=(
            vpp.components[up_id + "_pv"].module.Impo
            * vpp.components[up_id + "_pv"].module.Vmpo
            / 1000000
        ),
        q_mvar = 0,
        name=(up_id + "_pv"),
        type="pv",
    )

    sb_profiles[('sgen', 'p_mw')][net.sgen.index[-1]] = vpp.components[up_id + "_pv"].timeseries * -1

def add_storage(up_id, up_dict, vpp, net, sb_profiles):
    
    up_dict[up_id].ees.identifier = up_id+'_ees'

    vpp.add_component(up_dict[up_id].ees)

    pp.create_storage(
        net,
        bus=net.bus[net.bus.name == bus].index[0],
        p_mw=0,
        q_mvar = 0,
        max_e_mwh=vpp.components[up_id + "_ees"].capacity / 1000,
        name=(up_id + "_ees"),
        type="ees",
    )
    # EES recieves timeseries after optimization
    sb_profiles[('storage', 'p_mw')][net.storage.index[-1]] = 0.0

#%% Assign remaining components to the grid
if (nr_pv+nr_chp) >0:

    up_dict = dict()
    unequipped_lst = list() # to catch errors
    #Assure only lv loads are considered
    mv_lst = list()
    for load in net.load.name:
        if "MV" in load:
            mv_lst.append(load)

    # Sample lv loads. MV loads are at the end of the list
    load_bus_lst = random.sample(list(
        net.load.index[:-(len(mv_lst))]
        ),
        (nr_pv+nr_chp))
    # Shuffle, so components of the same type are not all in one area
    random.shuffle(load_bus_lst)

    for load_idx in tqdm(load_bus_lst):

        if nr_chp > 0:
            
            house = random.sample(user_profiles_dict.keys(), 1)[0]
            bus = net.bus.name[net.load.bus[load_idx]]
            up_id = bus+'_'+house
            
            net.load.profile[load_idx] = house
            net.load.p_mw[load_idx] = 0.0
            net.load.q_mvar[load_idx] = 0.0
            net.load.sn_mva[load_idx] = 0.0
    
            sb_profiles[('load', 'p_mw')][load_idx] = user_profiles_dict[
                house
                ].electric_energy_demand/1000
    
            # In this place we need a deep copy to recieve independent users.
            # Otherwise changes in one up would impact multiple up's
            up_dict[up_id] = copy.deepcopy(user_profiles_dict[house])
            up_dict[up_id].bus = bus
    
            # Adjust the identifier of the user_profile itself
            up_dict[up_id].identifier = up_id

            #TODO This way, all chps will be in the same district. Improvement?
            up_dict[up_id].chp.identifier = up_id+'_chp'
            vpp.add_component(up_dict[up_id].chp)

            pp.create_sgen(
                net,
                bus=net.bus[net.bus.name == bus].index[0],
                p_mw=(vpp.components[up_id + "_chp"].el_power / 1000),
                q_mvar = 0,
                name=(up_id + "_chp"),
                type="chp",
            )

            # CHP recieves timeseries after optimization
            sb_profiles[('sgen', 'p_mw')][net.sgen.index[-1]] = 0.0

            up_dict[up_id].hr.identifier = up_id+'_hr'
            vpp.add_component(up_dict[up_id].hr)
            
            pp.create_load(
                net,
                bus=net.bus[net.bus.name == bus].index[0],
                p_mw=(vpp.components[up_id + "_hr"].el_power / 1000),
                q_mvar = 0,
                name=(up_id + "_hr"),
                type="hr",
            )
            # HR recieves timeseries after optimization
            sb_profiles[('load', 'p_mw')][net.load.index[-1]] = 0.0
            sb_profiles[('load', 'q_mvar')][net.load.index[-1]] = 0.0

            nr_chp -= 1
            
            # Thermal Energy Storage
            up_dict[up_id].tes.identifier = up_id+'_tes'
            vpp.add_component(up_dict[up_id].tes)
            # Thermal component, no equivalent in pandapower

            if nr_bev > 0:
                if random.choice([True, False]):
                    # bev yes or no
                
                    up_dict[up_id].bev.identifier = up_id+'_bev'
    
                    vpp.add_component(up_dict[up_id].bev)
    
                    pp.create_load(
                        net,
                        bus=net.bus[net.bus.name == bus].index[0],
                        p_mw=(vpp.components[up_id + "_bev"].charging_power / 1000),
                        q_mvar = 0,
                        name=(up_id + "_bev"),
                        type="bev",
                    )
                    # BEV recieves timeseries after optimization
                    sb_profiles[('load', 'p_mw')][net.load.index[-1]] = 0.0
                    sb_profiles[('load', 'q_mvar')][net.load.index[-1]] = 0.0

                    nr_bev -= 1

            up_dict[up_id].pv = None
            up_dict[up_id].hp = None

            #### chp end ####

        elif nr_hp > 0:

            house = random.sample(user_profiles_dict.keys(), 1)[0]
            bus = net.bus.name[net.load.bus[load_idx]]
            up_id = bus+'_'+house

            net.load.profile[load_idx] = house
            net.load.p_mw[load_idx] = 0.0
            net.load.q_mvar[load_idx] = 0.0
            net.load.sn_mva[load_idx] = 0.0

            sb_profiles[('load', 'p_mw')][load_idx] = user_profiles_dict[
                house
                ].electric_energy_demand/1000

            # In this place we need a deep copy to recieve independent users.
            # Otherwise changes in one up would impact multiple up's
            up_dict[up_id] = copy.deepcopy(user_profiles_dict[house])
            up_dict[up_id].bus = bus

            # Adjust the identifier of the user_profile itself
            up_dict[up_id].identifier = up_id

            up_dict[up_id].hp.identifier = up_id+'_hp'
            vpp.add_component(up_dict[up_id].hp)

            pp.create_load(
                net,
                bus=net.bus[net.bus.name == bus].index[0],
                p_mw=(vpp.components[up_id + "_hp"].el_power / 1000),
                q_mvar = 0,
                name=(up_id + "_hp"),
                type="hp",
            )
            # HP recieves timeseries after optimization
            sb_profiles[('load', 'p_mw')][net.load.index[-1]] = 0.0
            sb_profiles[('load', 'q_mvar')][net.load.index[-1]] = 0.0

            # Thermal Energy Storage
            up_dict[up_id].tes.identifier = up_id+'_tes'
            vpp.add_component(up_dict[up_id].tes)
            # Thermal component, no equivalent in pandapower

            nr_hp -= 1

            up_dict[up_id].tes.identifier = up_id+'_tes'
            vpp.add_component(up_dict[up_id].tes)
            # Thermal component, no equivalent in pandapower
            
            up_dict[up_id].chp = None
            up_dict[up_id].hr = None

            if nr_bev > 0:
                # if random.choice([True, False]):
                #     # bev yes or no
                
                up_dict[up_id].bev.identifier = up_id+'_bev'

                vpp.add_component(up_dict[up_id].bev)

                pp.create_load(
                    net,
                    bus=net.bus[net.bus.name == bus].index[0],
                    p_mw=(vpp.components[up_id + "_bev"].charging_power / 1000),
                    q_mvar = 0,
                    name=(up_id + "_bev"),
                    type="bev",
                )
                # BEV recieves timeseries after optimization
                sb_profiles[('load', 'p_mw')][net.load.index[-1]] = 0.0
                sb_profiles[('load', 'q_mvar')][net.load.index[-1]] = 0.0

                nr_bev -= 1

            if nr_pv > 0:
                add_pv(up_id, up_dict, vpp, net, sb_profiles)
                nr_pv -= 1

                if nr_storage > 0:
                    if random.choice([True, False]):
                        # storage yes or no
                        add_storage(up_id, up_dict, vpp, net, sb_profiles)
                        nr_storage -= 1

                ###### heat pump end #####

        elif nr_bev > 0:

            house = net.load.name[load_idx]
            bus = net.bus.name[net.load.bus[load_idx]]
            up_id = bus+'_'+house
            
            # In this place we need a deep copy to recieve independent users.
            # Otherwise changes in one up would impact multiple up's
            up_dict[up_id] = copy.deepcopy(user_profiles_dict[
                random.sample(user_profiles_dict.keys(), 1)[0]
                ])
            up_dict[up_id].bus = bus
    
            # Adjust the identifier of the user_profile itself
            up_dict[up_id].identifier = up_id

            up_dict[up_id].bev.identifier = up_id+'_bev'

            vpp.add_component(up_dict[up_id].bev)

            pp.create_load(
                net,
                bus=net.bus[net.bus.name == bus].index[0],
                p_mw=(vpp.components[up_id + "_bev"].charging_power / 1000),
                q_mvar = 0,
                name=(up_id + "_bev"),
                type="bev",
            )
            # BEV recieves timeseries after optimization
            sb_profiles[('load', 'p_mw')][net.load.index[-1]] = 0.0
            sb_profiles[('load', 'q_mvar')][net.load.index[-1]] = 0.0

            nr_bev -= 1

            if nr_pv > 0:
                add_pv(up_id, up_dict, vpp, net, sb_profiles)
                nr_pv -= 1

                if nr_storage > 0:

                    add_storage(up_id, up_dict, vpp, net, sb_profiles)
                    nr_storage -= 1
            
            up_dict[up_id].chp = None
            up_dict[up_id].hr = None

        elif nr_pv > 0:

            house = net.load.name[load_idx]
            bus = net.bus.name[net.load.bus[load_idx]]
            up_id = bus+'_'+house

            # In this place we need a deep copy to recieve independent users.
            # Otherwise changes in one up would impact multiple up's
            up_dict[up_id] = copy.deepcopy(user_profiles_dict[
                random.sample(user_profiles_dict.keys(), 1)[0]
                ])
            up_dict[up_id].bus = bus
    
            # Adjust the identifier of the user_profile itself
            up_dict[up_id].identifier = up_id

            add_pv(up_id, up_dict, vpp, net, sb_profiles)
            nr_pv -= 1
    
            if nr_storage > 0:

                add_storage(up_id, up_dict, vpp, net, sb_profiles)
                nr_storage -= 1

            up_dict[up_id].chp = None
            up_dict[up_id].hr = None
            up_dict[up_id].tes = None
            up_dict[up_id].bev = None

        else:
            unequipped_lst.append(load_idx)

print("Unequippend loadbuses:")
print(unequipped_lst)

# #%% Assign user_profiles to load buses

# print("Assign user_profiles to load buses:\n")
# up_dict = dict()
# for load_idx in tqdm(net.load.index):
#     if "LV" in net.load.name[load_idx]:

#         house = random.sample(user_profiles_dict.keys(), 1)[0]
#         bus = net.bus.name[net.load.bus[load_idx]]
#         up_id = bus+'_'+house
        
#         net.load.profile[load_idx] = house
#         net.load.p_mw[load_idx] = 0.0
#         net.load.q_mvar[load_idx] = 0.0
#         net.load.sn_mva[load_idx] = 0.0

#         sb_profiles[('load', 'p_mw')][load_idx] = user_profiles_dict[
#             house
#             ].electric_energy_demand/1000

#         # In this place we need a deep copy to recieve independent users.
#         # Otherwise changes in one up would impact multiple up's
#         up_dict[up_id] = copy.deepcopy(user_profiles_dict[house])
#         up_dict[up_id].bus = bus

#         # Adjust the identifier of the user_profile itself
#         up_dict[up_id].identifier = up_id

#         # Adjust the identifier of the components
#         # Add components to vpp and pandapower network
#         if "pv" in up_dict[up_id].__dict__.keys():
#             up_dict[up_id].pv.identifier = up_id+'_pv'

#             vpp.add_component(up_dict[up_id].pv)
#             # Adjust column name of timeseries to match new identifier of 
#             # component
#             vpp.components[
#                 up_dict[up_id].pv.identifier
#                 ].timeseries.columns = [
#                     vpp.components[
#                         up_dict[up_id].pv.identifier].identifier]

#             pp.create_sgen(
#                 net,
#                 bus=net.bus[net.bus.name == bus].index[0], #TODO: use net.load.bus[load_idx]
#                 p_mw=(
#                     vpp.components[up_id + "_pv"].module.Impo
#                     * vpp.components[up_id + "_pv"].module.Vmpo
#                     / 1000000
#                 ),
#                 q_mvar = 0,
#                 name=(up_id + "_pv"),
#                 type="pv",
#             )

#             sb_profiles[('sgen', 'p_mw')][net.sgen.index[-1]] = vpp.components[up_id + "_pv"].timeseries * -1 #TODO: Check in results if correct

#         if "chp" in up_dict[up_id].__dict__.keys():
#             up_dict[up_id].chp.identifier = up_id+'_chp'
#             vpp.add_component(up_dict[up_id].chp)
            
#             pp.create_sgen(
#                 net,
#                 bus=net.bus[net.bus.name == bus].index[0],
#                 p_mw=(vpp.components[up_id + "_chp"].el_power / 1000),
#                 q_mvar = 0,
#                 name=(up_id + "_chp"),
#                 type="chp",
#             )
            
#             # CHP recieves timeseries after optimization
#             sb_profiles[('sgen', 'p_mw')][net.sgen.index[-1]] = 0.0

#         if "hr" in up_dict[up_id].__dict__.keys():
#             up_dict[up_id].hr.identifier = up_id+'_hr'
#             vpp.add_component(up_dict[up_id].hr)
            
#             pp.create_load(
#                 net,
#                 bus=net.bus[net.bus.name == bus].index[0],
#                 p_mw=(vpp.components[up_id + "_hr"].el_power / 1000),
#                 q_mvar = 0,
#                 name=(up_id + "_hr"),
#                 type="hr",
#             )
#             # HR recieves timeseries after optimization
#             sb_profiles[('load', 'p_mw')][net.load.index[-1]] = 0.0
#             sb_profiles[('load', 'q_mvar')][net.load.index[-1]] = 0.0

#         if "hp" in up_dict[up_id].__dict__.keys():
#             up_dict[up_id].hp.identifier = up_id+'_hp'
#             vpp.add_component(up_dict[up_id].hp)
            
#             pp.create_load(
#                 net,
#                 bus=net.bus[net.bus.name == bus].index[0],
#                 p_mw=(vpp.components[up_id + "_hp"].el_power / 1000),
#                 q_mvar = 0,
#                 name=(up_id + "_hp"),
#                 type="hp",
#             )
#             # HP recieves timeseries after optimization
#             sb_profiles[('load', 'p_mw')][net.load.index[-1]] = 0.0
#             sb_profiles[('load', 'q_mvar')][net.load.index[-1]] = 0.0

#         if "tes" in up_dict[up_id].__dict__.keys():
#             up_dict[up_id].tes.identifier = up_id+'_tes'
#             vpp.add_component(up_dict[up_id].tes)
#             # Thermal component, no equivalent in pandapower

#         if "ees" in up_dict[up_id].__dict__.keys():
#             up_dict[up_id].ees.identifier = up_id+'_ees'

#             vpp.add_component(up_dict[up_id].ees)

#             pp.create_storage(
#                 net,
#                 bus=net.bus[net.bus.name == bus].index[0],
#                 p_mw=0,
#                 q_mvar = 0,
#                 max_e_mwh=vpp.components[up_id + "_ees"].capacity / 1000,
#                 name=(up_id + "_ees"),
#                 type="ees",
#             )
#             # EES recieves timeseries after optimization
#             sb_profiles[('storage', 'p_mw')][net.storage.index[-1]] = 0.0

#         if "bev" in up_dict[up_id].__dict__.keys():
#             up_dict[up_id].bev.identifier = up_id+'_bev'

#             vpp.add_component(up_dict[up_id].bev)
            
#             pp.create_load(
#                 net,
#                 bus=net.bus[net.bus.name == bus].index[0],
#                 p_mw=(vpp.components[up_id + "_bev"].charging_power / 1000),
#                 q_mvar = 0,
#                 name=(up_id + "_bev"),
#                 type="bev",
#             )
#             # BEV recieves timeseries after optimization
#             sb_profiles[('load', 'p_mw')][net.load.index[-1]] = 0.0
#             sb_profiles[('load', 'q_mvar')][net.load.index[-1]] = 0.0

print(time.asctime(time.localtime(time.time())))
print("Assigned user profiles to vpp and net\n")


#%% Save vpp and net to pickle for later powerflow analysis

savety_timestamp = time.strftime("%Y%m%d-%H%M%S",time.localtime())

#TODO: Create Folder for results every time
newpath = (r'./Results/'+savety_timestamp) 
if not os.path.exists(newpath):
    os.makedirs(newpath)

with open((newpath+"/"+savety_timestamp+"_up_dict"+".pickle"),"wb") as handle:
    pickle.dump(up_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open((newpath+"/"+savety_timestamp+"_vpp_export"+".pickle"),"wb") as handle:
    pickle.dump(vpp, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open((newpath+"/"+savety_timestamp+"_net_export"+".pickle"),"wb") as handle:
    pickle.dump(net, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open((newpath+"/"+savety_timestamp+"_sb_profiles"+".pickle"),"wb") as handle:
    pickle.dump(sb_profiles, handle, protocol=pickle.HIGHEST_PROTOCOL)

net.load.to_csv(newpath+"/"+savety_timestamp+"_net_load"+".csv")

print(time.asctime(time.localtime(time.time())))
print("Saved vpp and net to pickle\n")

# %% Export vpp to sql

vpp.export_components_to_sql((savety_timestamp+"/"+savety_timestamp+"_vpp_export"))

print(time.asctime(time.localtime(time.time())))
print("Exported component values and timeseries to sql\n")

# Unnecessary
# profiles = pd.DataFrame(columns=["load", "load_profile_nr"], index=net.load.index)
# for idx in net.load.index:
#     profiles["load"][idx]= net.load.name[idx]
#     profiles["load_profile_nr"][idx]= idx
    
# profiles.to_csv((newpath+"/"+savety_timestamp+"_profilzuordnung.csv"))
