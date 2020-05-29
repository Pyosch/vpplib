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

import simbench as sb
import pandapower as pp

from vpplib import VirtualPowerPlant  #, Operator, UserProfile, Environment,
from vpplib import Photovoltaic, WindPower, BatteryElectricVehicle
from vpplib import HeatPump, ThermalEnergyStorage, ElectricalEnergyStorage
from vpplib import CombinedHeatAndPower

# define virtual power plant
wind_number = 0
bev_number = 0

# Simbench Network parameters
sb_code = "1-LV-semiurb4--0-sw" #"1-MVLV-semiurb-all-0-sw" # "1-MVLV-semiurb-5.220-0-sw" # 

# Values for environment
start = "2015-01-01 00:00:00"
end = "2015-01-01 23:45:00"
year = "2015"
time_freq = "15 min"
index_year = pd.date_range(
    start=year, periods=35040, freq=time_freq, name="time"
)
index_hours = pd.date_range(start=start, end=end, freq="h", name="time")
timebase = 15  # for calculations from kW to kWh
timezone="Europe/Berlin"

# WindTurbine data
wea_list = [
        "E-53/800",
        "E48/800",
        "V100/1800",
        "E-82/2000",
        "V90/2000"]  # randomly choose windturbine
hub_height = 135
rotor_diameter = 127
fetch_curve = "power_curve"
data_source = "oedb"

# Wind ModelChain data
# possible wind_speed_model: 'logarithmic', 'hellman',
# 'interpolation_extrapolation', 'log_interpolation_extrapolation'
wind_speed_model = "logarithmic"
density_model = "ideal_gas"
temperature_model = "linear_gradient"
power_output_model = "power_coefficient_curve"  # alt.: 'power_curve'
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
with open(r'Results/20200529-152558_up_dummy_profiles.pickle', 'rb') as handle:
    household_dict = pickle.load(handle)

print(time.asctime( time.localtime(time.time()) ))
print("Loaded input\n")


#%% Adjust the values of the environments in the household_dict with the
#   current values. Since the environment is stored in one place
#   (eg. 0x158c9b24c08) and all components have the same, it only has to be
#   changed once!

household_dict[list(household_dict.keys())[0]].environment.start = start
household_dict[list(household_dict.keys())[0]].environment.end = end
household_dict[list(household_dict.keys())[0]].environment.timebase = timebase
household_dict[list(household_dict.keys())[0]].environment.timezone = timezone
household_dict[list(household_dict.keys())[0]].environment.year = year
household_dict[list(household_dict.keys())[0]].environment.time_freq = time_freq

# get data for timeseries calculations
household_dict[list(household_dict.keys())[0]].environment.get_mean_temp_days()
household_dict[list(household_dict.keys())[0]].environment.get_mean_temp_hours()
household_dict[list(household_dict.keys())[0]].environment.get_pv_data()
household_dict[list(household_dict.keys())[0]].environment.get_wind_data()

#%% Get timeseries of the households

for house in household_dict.keys():
    if "pv_system" in list(household_dict[house].__dict__.keys()):
        household_dict[house].pv_system.prepare_time_series()
        
        # TODO
        # Somehow in some pvlib timeseries the inverter losses during night hours
        # are not complete. Once we find out how to solve this problem we can
        # delete this part:
        if household_dict[house].pv_system.timeseries.isnull().values.any():
                household_dict[house].pv_system.timeseries.fillna(
                    value=0,
                    inplace=True)

# %% virtual power plant

vpp = VirtualPowerPlant("vpp")

# %% Simbench network

net = sb.get_simbench_net(sb_code)

# plot the grid
pp.plotting.simple_plot(net)

# drop preconfigured electricity generators  and loads from the grid
net.sgen.drop(net.sgen.index, inplace = True)
net.load.drop(net.load.index, inplace = True)

print(time.asctime(time.localtime(time.time())))
print("Initialized environment, vpp and net\n")


#%% Assign user_profiles to buses
up_dict = dict()
for bus in tqdm(net.bus.name):
    if "LV" in bus:

        house = random.sample(household_dict.keys(), 1)[0]
        up_id = bus+'_'+house

        # In this place we need a deep copy to recieve independent users.
        # Otherwise changes in one up would impact multiple up's
        up_dict[up_id] = copy.deepcopy(household_dict[house])
        up_dict[up_id].bus = bus

        # Adjust the identifier of the user_profile itself
        up_dict[up_id].identifier = up_id

        # Adjust the identifier of the components
        # Add components to vpp and pandapower network
        if "pv_system" in up_dict[up_id].__dict__.keys():
            up_dict[up_id].pv_system.identifier = up_id+'_pv'

            vpp.add_component(up_dict[up_id].pv_system)
            # Adjust column name of timeseries to match new identifier of 
            # component
            vpp.components[
                up_dict[up_id].pv_system.identifier
                ].timeseries.columns = [
                    vpp.components[
                        up_dict[up_id].pv_system.identifier].identifier]

            pp.create_sgen(
                net,
                bus=net.bus[net.bus.name == bus].index[0],
                p_mw=(
                    vpp.components[up_id + "_pv"].module.Impo
                    * vpp.components[up_id + "_pv"].module.Vmpo
                    / 1000000
                ),
                q_mvar = 0,
                name=(up_id + "_pv"),
                type="pv",
            )

        if "chp" in up_dict[up_id].__dict__.keys():
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

        if "hr" in up_dict[up_id].__dict__.keys():
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

        if "hp" in up_dict[up_id].__dict__.keys():
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

        if "tes" in up_dict[up_id].__dict__.keys():
            up_dict[up_id].tes.identifier = up_id+'_tes'
            vpp.add_component(up_dict[up_id].tes)
            # Thermal component, no equivalent in pandapower

        if "ees" in up_dict[up_id].__dict__.keys():
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

        if "bev" in up_dict[up_id].__dict__.keys():
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

print(time.asctime(time.localtime(time.time())))
print("Assigned user profiles to vpp and net\n")


# %% Export vpp to sql

savety_timestamp = time.strftime("%Y%m%d-%H%M%S",time.localtime())

vpp.export_components_to_sql(savety_timestamp+"_vpp_export")

print(time.asctime(time.localtime(time.time())))
print("Exported component values and timeseries to sql\n")
#%% Save vpp and net to pickle for later powerflow analysis


with open((r"./Results/"+savety_timestamp+"_vpp_export"+".pickle"),"wb") as handle:
    pickle.dump(vpp, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open((r"./Results/"+savety_timestamp+"_net_export"+".pickle"),"wb") as handle:
    pickle.dump(net, handle, protocol=pickle.HIGHEST_PROTOCOL)

print(time.asctime(time.localtime(time.time())))
print("Saved vpp and net to pickle\n")

