# -*- coding: utf-8 -*-
"""
Created on Tue May 19 16:27:36 2020

@author: sbirk
"""

import pandas as pd
import pickle
import random
import math
import time

from vpplib import UserProfile, Environment
from vpplib import Photovoltaic, WindPower, BatteryElectricVehicle
from vpplib import HeatPump, ThermalEnergyStorage, ElectricalEnergyStorage
from vpplib import CombinedHeatAndPower, HeatingRod

# UserProfile data
latitude = 50.941357
longitude = 6.958307
target_temperature = 60  # °C
t_0 = 40  # °C

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

#chp data
ramp_up_time = 1 / 15  # timesteps
ramp_down_time = 1 / 15  # timesteps
min_runtime = 1  # timesteps
min_stop_time = 2  # timesteps

# Values for Thermal Storage
target_temperature = 60  # °C
hysteresis = 10  # °K
cp = 4.2
thermal_energy_loss_per_day = 0.13

#Values for HeatingRod
ramp_up_time_hr = 1/15 #timesteps
ramp_down_time_hr = 1 / 15  # timesteps
min_runtime_hr = 0  # timesteps
min_stop_time_hr = 0  # timesteps

# Values for electrical storage
max_c = 1  # factor between 0.5 and 1.2

# Year to pick data from COMODO installed capacity
year = [2025, 2030, 2035, 2040]

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

#%% environment to prevent errors

environment = Environment(
    timebase=timebase,
    timezone="Europe/Berlin",
    start=start,
    end=end,
    year=year,
    time_freq=time_freq,
)

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

        # Include fzj profiles
        user_profile.environment = environment
        user_profile.el_profile = random.sample(el_dict.keys(), 1)[0]

        if "HH1a" in user_profile.el_profile:
            if "Winter" in user_profile.el_profile:
                user_profile.th_profile = 'HH1a_vacationWinter'

            if "Summer" in user_profile.el_profile:
                user_profile.th_profile = 'HH1a_vacationSummer'

        elif "HH1b" in user_profile.el_profile:
            if "Winter" in user_profile.el_profile:
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

        # Include COMODO results
        if math.isnan(df_installed_cap.loc[house].loc[y].PV) == False:

            ### PV ###
            pv = Photovoltaic(module_lib="SandiaMod",
                              inverter_lib="SandiaInverter",
                              surface_tilt = random.randrange(start=20, stop=40, step=5),
                              surface_azimuth = random.randrange(start=160, stop=220, step=10),
                              unit="kW",
                              identifier=(user_profile.identifier+'_pv'),
                              environment=environment,
                              user_profile=user_profile,
                              cost=None)

            pv.pick_pvsystem(
                  min_module_power = 100,
                  max_module_power = 200,
                  pv_power = (df_installed_cap.loc[house].loc[y].PV*1000),
                  inverter_power_range = 100)

            # user_profile.pv_kwp = pv.peak_power
            user_profile.pv_system = pv

        ### CHP ###
        if math.isnan(df_installed_cap.loc[house].loc[y].CHP_Otto) == False:
            chp = CombinedHeatAndPower(
                unit="kW",
                identifier=(user_profile.identifier+'_chp'),
                environment=environment,
                user_profile=user_profile,
                el_power=((df_tech_input.loc["CHP_Otto"].efficiency_el
                              /df_tech_input.loc["CHP_Otto"].efficiency_th)
                              *df_installed_cap.loc[house].loc[y].CHP_Otto),
                th_power=df_installed_cap.loc[house].loc[y].CHP_Otto,
                overall_efficiency=None,
                efficiency_el=df_tech_input.loc["CHP_Otto"].efficiency_el,
                efficiency_th=df_tech_input.loc["CHP_Otto"].efficiency_th,
                ramp_up_time=ramp_up_time,
                ramp_down_time=ramp_down_time,
                min_runtime=min_runtime,
                min_stop_time=min_stop_time,
            )

            user_profile.chp = chp

        if math.isnan(df_installed_cap.loc[house].loc[y].Th_Stor_water_heat) == False:

            tes = ThermalEnergyStorage(
                identifier=(user_profile.identifier+'_tes'),
                environment=environment,
                user_profile=user_profile,
                unit="kWh",
                # E = m * cp * dT <-> m = E/cp*dT
                mass=(df_installed_cap.loc[house].loc[y].Th_Stor_water_heat
                      *3600
                      /(cp*(hysteresis*2))
                      ),
                hysteresis=hysteresis,
                target_temperature=target_temperature,
                cp=cp,
                thermal_energy_loss_per_day=thermal_energy_loss_per_day,
            )

            tes.efficiency_th = df_tech_input.loc["Th_Stor_water_heat"].efficiency_th

            user_profile.tes = tes

        if math.isnan(df_installed_cap.loc[house].loc[y].SimplePTH) == False:

            hr = HeatingRod(identifier=(user_profile.identifier+'_hr'),
                         environment=environment,
                         user_profile = user_profile,
                         el_power = df_installed_cap.loc[house].loc[y].SimplePTH,
                         efficiency = df_tech_input.loc["SimplePTH"].efficiency_th,
                         rampUpTime = ramp_up_time_hr, 
                         rampDownTime = ramp_down_time_hr, 
                         min_runtime = min_runtime_hr, 
                         min_stop_time = min_stop_time_hr)

            user_profile.hr = hr

        if math.isnan(df_installed_cap.loc[house].loc[y].Batt) == False:

            ees = ElectricalEnergyStorage(
                unit="kWh",
                identifier=(user_profile.identifier + "_ees"),
                environment=environment,
                user_profile=user_profile,
                capacity=df_installed_cap.loc[house].loc[y].Batt,
                charge_efficiency=df_tech_input.loc["Batt"].efficiency_el,
                discharge_efficiency=df_tech_input.loc["Batt"].efficiency_el,
                max_power=df_installed_cap.loc[house].loc[y].Batt,
                max_c=max_c,
            )

            user_profile.ees = ees

        user_profiles_dict[user_profile.identifier] = user_profile

with open(r'Results/'
          + time.strftime("%Y%m%d-%H%M%S",time.localtime())
          + '_up_dummy_profiles.pickle', 'wb') as handle:
    pickle.dump(user_profiles_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
