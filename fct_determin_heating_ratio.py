# -*- coding: utf-8 -*-
"""
Created on Sun May 10 13:51:38 2020

@author: andre
function to determin the heating ratio. heating ratio = amount of energy output
by hr / yearly heating demand
argument passed is the dataframe wich is returned from run_hp_hr
"""

import pandas as pd

def determin_heating_ratio(dataframe):
    heating_demand = dataframe['thermal_energy_demand'].values
    sum_energy = 0
    for i in range(len(dataframe)):
        sum_energy += heating_demand[i]
    # divide by 4 (because time steps are 1/4 hour) for correct result in [kWh]
    sum_energy = sum_energy / 4
    
    output_hr = dataframe['th_output_hr'].values
    sum_output = 0
    for i in range(len(dataframe)):
        sum_output += output_hr[i]
    # divide by 4 for correct result in [kWh]
    sum_output = sum_output / 4
        
    heating_ratio = sum_output / sum_energy
    
    return heating_ratio