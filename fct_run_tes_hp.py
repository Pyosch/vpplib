# -*- coding: utf-8 -*-
"""
Created on Sun May 24 13:25:28 2020

@author: andre
function for running tes + hp
"""
import pandas as pd

def run_tes_hp(tes, hp , mode, user_profile, environment):
    try:
        mode in ["optimize runtime", "overcome shutdown"]
        
    except:
        raise ValueError("mode needs to be 'optimize runtime' or 'overcome shutdown'.")
        
    heat_demand = user_profile.thermal_energy_demand
    temperature = pd.read_csv("./input/thermal/dwd_temp_15min_2015.csv",
                              index_col="time")
    
    dataframe = pd.concat([heat_demand, temperature], axis = 1)
    
    cop_threshold = 2.5
    
    # to iterate over
    th_energy_demand = dataframe['thermal_energy_demand'].values
    temperatures = dataframe['temperature'].values
    
    cops = []
    i = 0
    
    if hp.heat_pump_type == "Air":
        while i < len(dataframe):
            cops.append((6.81 - 0.121 * (hp.heat_sys_temp - temperatures[i])
                       + 0.00063 * (hp.heat_sys_temp - temperatures[i])**2))
            i += 1
            
    if hp.heat_pump_type == "Ground":
        while i < len(dataframe):
            cops.append((8.77 - 0.15 * (hp.heat_sys_temp - temperatures[i])
                       + 0.000734 * (hp.heat_sys_temp - temperatures[i])**2))
            i += 1
            
    output_hp = []
    demand_hp = []
    output_tes = []
    input_tes = []
    load_tes_list = []
    load_tes_start = 0
    load_tes = load_tes_start
    
            
    #if mode == "optimize runtime":
    for i in range(len(dataframe)):       
        if cops[i] < cop_threshold:
            if load_tes >= th_energy_demand[i]:
                output_tes.append(th_energy_demand[i])
                load_tes -= output_tes[i]
                output_hp.append(0)
                demand_hp.append(0)
                
            
                
        if cops[i] > cop_threshold:
            # hp allways running full power
            output_hp.append(hp.el_power * cops[i])
            print(str(output_hp))
            input_tes.append(output_hp[i] - th_energy_demand[i])
            load_tes += input_tes[i]
            demand_hp.append(hp.el_power)
        
        load_tes = load_tes * (1 - 0.1 / ((60 / environment.timebase) * 24))
        load_tes_list.append(load_tes)
        
    load_tes_df = pd.DataFrame(data = load_tes_list, colums = ['load_tes'],
                               index = dataframe.index)
    
    th_outup_hp = pd.DataFrame(data = output_hp, columns = ['th_output_hp'],
                               index = dataframe.index)
    
    el_demand_hp = pd.DataFrame(data = demand_hp, columns = ['el_demand_hp'],
                                index = dataframe.index)
    
    input_tes_df = pd.DataFrame(data = input_tes, columns = ['input_tes'],
                                index = dataframe.index)
    
    output_tes_df = pd.DataFrame(data = output_tes, columns = ['output_tes'],
                                 index = dataframe.index)
    
    dataframe = pd.concat([dataframe, load_tes_df, th_output_hp, el_demand_hp,
                           input_tes_df, output_tes_df])
    
    return dataframe

    
            
        
            
    
    