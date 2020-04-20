# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 14:27:30 2020

@author: pyosch
"""

import pandas as pd
import glob
import os
import pickle


#%%collect thermal profiles in one dictionary

therm_path = r'input\input_vise\Heat_profiles' # use your path
all_th_files = glob.glob(os.path.join(therm_path, "*.csv"))

thermal_dict = dict()

for filename in all_th_files:
    df = pd.read_csv(filename, index_col='Time', header=0)
    # df.set_index('Time', inplace=True)
    df.index = pd.to_datetime(df.index)
    thermal_dict[filename[47:-4]] = df

thermal_dict["HH1a_vacationSummer"].HeatDemand.plot(figsize=(16,9), legend=True, title="HH1a_vacationSummer")

#%% collect electrical profiles in one dictionary

el_path = r'input\input_vise\Selected_profiles_LPG'
all_el_files = glob.glob(el_path)

el_dict = dict()

for root, dirs, files in os.walk(el_path, topdown=False):
    for name in files:
        if "Electricity" in name:
            df = pd.read_csv(os.path.join(root, name),
                             index_col=None,
                             header=0,
                             sep=";",
                             decimal=",")
            df.columns = ["Time", "kWh", "NaN"]
            df.drop(columns=["NaN"], inplace=True)
            df.set_index('Time', inplace=True)
            df.index = pd.to_datetime(df.index)
            df = df.resample('15 Min').mean()
            el_dict[root[53:]] = df

#%% save dicts

with open(r'Results/thermal_dict.pickle', 'wb') as handle:
    pickle.dump(thermal_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open(r'Results/el_dict_15min.pickle', 'wb') as handle:
    pickle.dump(el_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

#%% load dicts
with open(r'Results/thermal_dict.pickle', 'rb') as handle:
    thermal_dict_b = pickle.load(handle)

with open(r'Results/el_dict_15min.pickle', 'rb') as handle:
    el_dict_b = pickle.load(handle)

#%% change year of el profiles to 2015

for key in el_dict_b.keys():
    el_dict_b[key].index = pd.date_range(start="2015", periods=len(el_dict_b[key].index), freq="15 min")

# save the new dict

with open(r'Results/el_dict_2015.pickle', 'wb') as handle:
    pickle.dump(el_dict_b, handle, protocol=pickle.HIGHEST_PROTOCOL)

#%% Assign thermal to electrical profiles

for el in el_dict.keys():

    if "HH1a" in el:
        if "Dec" in el:
            print('HH1a_vacationWinter', " belongs to ", el)
        if "Jul" in el:
            print('HH1a_vacationSummer', " belongs to ", el)

    elif "HH1b" in el:
        if "Dec" in el:
            print('HH1b_vacationWinter', " belongs to ", el)
        if "Jul" in el:
            print('HH1b_vacationSummer', " belongs to ", el)

    elif "HH2a" in el:
        if "Dec" in el:
            print('HH2a_vacationWinter', " belongs to ", el)
        if "Jul" in el:
            print('HH2a_vacationSummer', " belongs to ", el)

    elif "HH2b" in el:
        if "Dec" in el:
            print('HH2b_vacationWinter', " belongs to ", el)
        if "Jul" in el:
            print('HH2b_vacationSummer', " belongs to ", el)

    else:
        print("Profile ", el, " not propperly assigned!")

