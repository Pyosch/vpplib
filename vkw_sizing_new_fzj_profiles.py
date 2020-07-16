# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 14:27:30 2020

@author: pyosch
"""

import pandas as pd
import numpy as np
import glob
import os
import pickle
from tqdm import tqdm

thermal_profile_type = "VGW" #  "standard"
hours_bhkw = 4000

#%%collect thermal profiles in one dictionary

# therm_path = r'input\input_vise\Heat_profiles\Heat Load Profiles VGW' # use your path
# all_th_files = glob.glob(os.path.join(therm_path, "*.csv"))

# thermal_dict = dict()

# for filename in tqdm(all_th_files):
#     df = pd.read_csv(filename, index_col='Time', header=0)
#     # df.set_index('Time', inplace=True)
#     df.index = pd.to_datetime(df.index)
#     thermal_dict[filename[70:-4]] = df
    # thermal_dict[filename[47:-4]] = df

# # thermal_dict["HH1a_vacationSummer"].HeatDemand.plot(figsize=(16,9), legend=True, title="HH1a_vacationSummer")

# #%% collect electrical profiles in one dictionary

# el_path = r'input\input_vise\new_profiles_LPG'
# all_el_files = glob.glob(os.path.join(el_path, "*.csv"))

# el_dict = dict()

# for filename in tqdm(all_el_files):
#     df = pd.read_csv(filename,
#                      index_col='Time',
#                      header=0,
#                      sep=";",
#                      decimal=",")
#     df.drop(columns=["Electricity.Timestep"], inplace=True)
#     # df.set_index('Time', inplace=True)
#     df.index = pd.to_datetime(df.index)
#     df = df.resample('15 Min').sum()
#     el_dict[filename[58:-4]] = df

# #%% save dicts

# with open(r'Results/20200715_thermal_dict.pickle', 'wb') as handle:
#     pickle.dump(thermal_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open(r'Results/20200714_el_dict_15min.pickle', 'wb') as handle:
#     pickle.dump(el_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

#%% load dicts
with open(r'Results/20200715_thermal_dict.pickle', 'rb') as handle:
    thermal_dict = pickle.load(handle)

with open(r'Results/20200714_el_dict_15min.pickle', 'rb') as handle:
    el_dict = pickle.load(handle)

#%% Create house hold DataFrame with el and th profiles

# Use el_profile names as index for the DataFrame

house_holds = pd.DataFrame(index=el_dict.keys(), columns=['thermal_profile',
                                                          'sum_el_kWh',
                                                          'sum_th_kWh',
                                                          'el_peak_kW',
                                                          'th_peak_kW',
                                                          'hp_kW_th',
                                                          'tes_liter',
                                                          'bhkw_kW_th',
                                                          'hr_kW',
                                                          'pv_kWp',
                                                          'ees_kWh',
                                                          'bev_kWh'])

#%% Assign thermal VGW profiles to electrical profiles DataFrame
#  Use thermal peak for heat pump dimension

if thermal_profile_type == "VGW":
    for el in house_holds.index:

        if "HH1" in el:
            if "Winter" in el:
                print('HH1_vacationWinter', " belongs to ", el)
                house_holds['thermal_profile'][el] = 'HH1_vacationWinter'
                house_holds['sum_th_kWh'][el] = thermal_dict['HH1_vacationWinter'].sum()[0]
                house_holds['sum_el_kWh'][el] = el_dict[el].sum()[0]
                house_holds['el_peak_kW'][el] = el_dict[el].max()[0] * 4
                house_holds['th_peak_kW'][el] = thermal_dict['HH1_vacationWinter'].max()[0]
                house_holds['hp_kW_th'][el] = thermal_dict['HH1_vacationWinter'].max()[0]
                house_holds['bhkw_kW_th'][el] = thermal_dict['HH1_vacationWinter'].sort_values(
                    by=['Heat_load_kWh'], ascending=False, ignore_index=True).iloc[hours_bhkw][0].round(1)

            if "Summer" in el:
                print('HH1_vacationSummer', " belongs to ", el)
                house_holds['thermal_profile'][el] = 'HH1_vacationSummer'
                house_holds['sum_th_kWh'][el] = thermal_dict['HH1_vacationSummer'].sum()[0]
                house_holds['sum_el_kWh'][el] = el_dict[el].sum()[0]
                house_holds['el_peak_kW'][el] = el_dict[el].max()[0] * 4
                house_holds['th_peak_kW'][el] = thermal_dict['HH1_vacationSummer'].max()[0]
                house_holds['hp_kW_th'][el] = thermal_dict['HH1_vacationSummer'].max()[0]
                house_holds['bhkw_kW_th'][el] = thermal_dict['HH1_vacationSummer'].sort_values(
                    by=['Heat_load_kWh'], ascending=False, ignore_index=True).iloc[hours_bhkw][0].round(1)

        elif "HH2" in el:
            if "Winter" in el:
                print('HH2_vacationWinter', " belongs to ", el)
                house_holds['thermal_profile'][el] = 'HH2_vacationWinter'
                house_holds['sum_th_kWh'][el] = thermal_dict['HH2_vacationWinter'].sum()[0]
                house_holds['sum_el_kWh'][el] = el_dict[el].sum()[0]
                house_holds['el_peak_kW'][el] = el_dict[el].max()[0] * 4
                house_holds['th_peak_kW'][el] = thermal_dict['HH2_vacationWinter'].max()[0]
                house_holds['hp_kW_th'][el] = thermal_dict['HH2_vacationWinter'].max()[0]
                house_holds['bhkw_kW_th'][el] = thermal_dict['HH2_vacationWinter'].sort_values(
                    by=['Heat_load_kWh'], ascending=False, ignore_index=True).iloc[hours_bhkw][0].round(1)

            if "Summer" in el:
                print('HH2_vacationSummer', " belongs to ", el)
                house_holds['thermal_profile'][el] = 'HH2_vacationSummer'
                house_holds['sum_th_kWh'][el] = thermal_dict['HH2_vacationSummer'].sum()[0]
                house_holds['sum_el_kWh'][el] = el_dict[el].sum()[0]
                house_holds['el_peak_kW'][el] = el_dict[el].max()[0] * 4
                house_holds['th_peak_kW'][el] = thermal_dict['HH2_vacationSummer'].max()[0]
                house_holds['hp_kW_th'][el] = thermal_dict['HH2_vacationSummer'].max()[0]
                house_holds['bhkw_kW_th'][el] = thermal_dict['HH2_vacationSummer'].sort_values(
                    by=['Heat_load_kWh'], ascending=False, ignore_index=True).iloc[hours_bhkw][0].round(1)

        else:
            print("Profile ", el, " not propperly assigned!")
            
    house_holds['hp_kW_th'] = house_holds['hp_kW_th'].apply(np.ceil)

#%% Dimension of thermal energy storage dependent on heat pump size
#  To bridge shut down times of heat pumps of up to two hours/day, 
#  60l/kW of hp power is suggested in the literature.
#
#  Dimension of PV system dependent on yearly el demand
#  Dimension of battery system dependent on yearly el demand

for el in house_holds.index:
    house_holds['tes_liter'][el] = house_holds['hp_kW_th'][el] * 60
    house_holds['pv_kWp'][el] = (house_holds['sum_el_kWh'][el] / 1000 * 1.5).round(1)
    house_holds['ees_kWh'][el] = (house_holds['sum_el_kWh'][el] / 1000 * 1.5).round(1)
    house_holds['hr_kW'][el] = (house_holds['th_peak_kW'][el] - house_holds['bhkw_kW_th'][el]).round(1)

