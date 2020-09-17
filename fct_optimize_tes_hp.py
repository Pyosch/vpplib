# -*- coding: utf-8 -*-
"""
Created on Sun May 24 11:59:44 2020

@author: andre

function to determine correct size for thermal energy storage
"""
#import thermal_energy_storage
import pandas as pd

def optimize_tes_hp(tes, hp, mode, user_profile):
    if mode == "optimize runtime":
        factor = 20
    elif mode == "overcome shutdown":
        factor = 60
    else:
        raise ValueError("mode needs to be 'optimize runtime' or 'overcome shutdown'.")

    th_demand = user_profile.thermal_energy_demand
    temps = pd.read_csv("./input/thermal/dwd_temp_15min_2015.csv",
                              index_col="time")
    
    dataframe = pd.concat([th_demand, temps], axis = 1)
    dataframe.sort_values(by = ['thermal_energy_demand'], ascending = False, inplace = True)
    
    hp.th_power = round(float(dataframe['thermal_energy_demand'][0]), 1)
    hp.el_power = round(float(hp.th_power / hp.get_current_cop(dataframe['temperature'][0])), 1)
    hp.el_power *= 1.3
    
    density = 1  #kg/l
        
    tes.mass = hp.th_power * factor * density
    
