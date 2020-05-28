# -*- coding: utf-8 -*-
"""
Created on Tue May 19 16:27:36 2020

@author: sbirk
"""

import pandas as pd
import pickle
import random

from vpplib import UserProfile
from vpplib import Photovoltaic, WindPower, BatteryElectricVehicle
from vpplib import HeatPump, ThermalEnergyStorage, ElectricalEnergyStorage
from vpplib import CombinedHeatAndPower

# UserProfile data
latitude = 50.941357
longitude = 6.958307
target_temperature = 60  # °C
t_0 = 40  # °C

# Year to pick data from COMODO installed capacity
year = [2040] #[2025, 2030, 2035, 2040]

#%% load data
with open(r'./input/input_vise/thermal_dict.pickle', 'rb') as handle:
    thermal_dict = pickle.load(handle)

with open(r'./input/input_vise/el_dict_15min.pickle', 'rb') as handle:
    el_dict = pickle.load(handle)

df_tech_input = pd.read_excel(
    r"./input/input_vise/COMODO/Input_Tech_COMODO_v1.01.xlsx",
    decimal=",",
    index_col="tech")

df_installed_cap = pd.read_excel(
    r"./input/input_vise/COMODO/comodo_results_instaCap.xlsx",
    decimal=",",
    sheet_name="out_INSTCAP",
    index_col=[0,1])

#%% Generate UserProfiles based on fzj profiles and COMODO results


user_profiles_dict = dict()
for house in df_installed_cap.index.get_level_values(0).unique():
    for y in year:
        # Create UserProfile for every buildug type
        user_profile = UserProfile(
            identifier=(house+"_"+str(y)),
            latitude=latitude,
            longitude=longitude,
            thermal_energy_demand_yearly=None,
            building_type=None,
            comfort_factor=None,
            t_0=t_0,
            daily_vehicle_usage=None,
            week_trip_start=[],
            week_trip_end=[],
            weekend_trip_start=[],
            weekend_trip_end=[],
        )
        # Include COMODO results
        if df_installed_cap.loc[house].loc[y].PV:

            pv = Photovoltaic(module_lib="SandiaMod",
                  inverter_lib="SandiaInverter",
                  surface_tilt = random.randrange(start=20, stop=40, step=5),
                  surface_azimuth = random.randrange(start=160, stop=220, step=10),
                  unit="kW",
                  identifier=None,
                  environment=None,
                  user_profile=user_profile,
                  cost=None)

            (modules_per_string,
             strings_per_inverter,
             module, inverter) = pv.pick_pvsystem(
                 min_module_power = 100,
                 max_module_power = 200,
                 pv_power = (df_installed_cap.loc[house].loc[y].PV*1000),
                 inverter_power_range = 100)

            # user_profile.pv_kwp = pv.peak_power
            user_profile.pv_system = pv

        user_profile.chp_kw_th = df_installed_cap.loc[house].loc[y].CHP_Otto
        user_profile.chp_el_eff = df_tech_input.loc["CHP_Otto"].efficiency_el
        user_profile.chp_th_eff = df_tech_input.loc["CHP_Otto"].efficiency_th
        user_profile.chp_kw_el = ((df_tech_input.loc["CHP_Otto"].efficiency_el
                                  /df_tech_input.loc["CHP_Otto"].efficiency_th)
                                  *user_profile.chp_kw_th)
        user_profile.tes = df_installed_cap.loc[house].loc[y].Th_Stor_water_heat
        user_profile.heating_rod = df_installed_cap.loc[house].loc[y].SimplePTH
        user_profile.ees = df_installed_cap.loc[house].loc[y].Batt
    
        # Include fzj profiles
        user_profile.el_profile = random.sample(el_dict.keys(), 1)[0]

        if "HH1a" in user_profile.el_profile:
            if "Winter" in user_profile.el_profile:
                user_profile.th_profile = 'HH1a_vacationWinter'

            if "Summer" in user_profile.el_profile:
                user_profile.th_profile = 'HH1a_vacationSummer'

        elif "HH1b" in user_profile.el_profile:
            if "Dec" in user_profile.el_profile:
                user_profile.th_profile = 'HH1b_vacationWinter'

            if "Summer" in user_profile.el_profile:
                user_profile.th_profile = 'HH1b_vacationSummer'
    
        elif "HH2a" in user_profile.el_profile:
            if "Winter" in user_profile.el_profile:
                user_profile.th_profile = 'HH2a_vacationWinter'
    
            if "Summer" in user_profile.el_profile:
                user_profile.th_profile = 'HH2a_vacationSummer'

        elif "HH2b" in user_profile.el_profile:
            if "Winter" in user_profile.el_profile:
                user_profile.th_profile = 'HH2b_vacationWinter'
    
            if "Summer" in user_profile.el_profile:
                user_profile.th_profile = 'HH2b_vacationSummer'
    
        else:
            print("Profile of", user_profile.identifier, " not propperly assigned!")

        user_profile.electric_energy_demand = el_dict[user_profile.el_profile]
        user_profile.thermal_energy_demand = thermal_dict[user_profile.th_profile]

        user_profiles_dict[user_profile.identifier] = user_profile
