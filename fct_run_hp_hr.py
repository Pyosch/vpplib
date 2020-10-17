# -*- coding: utf-8 -*-
"""
Created on Sun May 10 09:49:17 2020

@author: andre

function for running heat pump and heating rod as described in "test_run_hp_hr.py"

"""
import pandas as pd

def run_hp_hr(hp, hr, mode, user_profile, norm_temp):
    
    # determine bivalence temperature according to norm_temperature
    if norm_temp <= -16:
        biv_temp = -4
    elif (norm_temp > -16) & (norm_temp <= -10):
        biv_temp = -3
    elif norm_temp > -10:
        biv_temp = -2
        
    temp_air = pd.read_csv("./input/thermal/dwd_temp_15min_2015.csv",
                              index_col="time")
    
        
    # temperature and heat demand over time
    heat_demand = user_profile.thermal_energy_demand
    if hp.heat_pump_type == "Air":
        temperature = temp_air
        dataframe = pd.concat([heat_demand, temperature], axis = 1)
    if hp.heat_pump_type == "Ground":
        temperature = pd.read_csv("./input/thermal/pik_temp_15min_ground_2015.csv",
                              index_col="time")
        dataframe = pd.concat([heat_demand, temperature, temp_air], axis = 1)
    
    # times where actual temp is below bivalence temp
    filter_temp = dataframe['temperature'] < biv_temp
    bools_temp = filter_temp.values
    filter_temp = pd.DataFrame(data = bools_temp, columns = ['t below t_biv'],
                               index = dataframe.index)
   
    dataframe = pd.concat([dataframe, filter_temp], axis = 1)
    
    output_hp = []
    demand_hp = []
    
    output_hr = []
    demand_hr = []
    
    cops_hp = []
    
    hp_capable = []
    hr_working = []
    
    # to iterate over
    th_energy_demand = dataframe['thermal_energy_demand'].values
    if hp.heat_pump_type == "Ground":
        temperature = dataframe['ground_temperature'].values
    if hp.heat_pump_type == "Air":
        temperature = dataframe['temperature'].values
#    # parallel mode
#    if mode == "parallel":
#        # determine heat pump thermal output (heat pump allways running)
#        for i in range(len(dataframe)):
#            if th_energy_demand[i] <= hp.el_power * hp.get_current_cop(temperature[i]):
#                output_hp.append(th_energy_demand[i])
#            else:
#                output_hp.append(hp.th_power)#hp.el_power * hp.get_current_cop(temperature[i]))
#                
#        # determine heating rod thermal output
#        for i in range(len(dataframe)):
#            if th_energy_demand[i] > output_hp[i]:   # if bools_temp[i] == True
#                diff = th_energy_demand[i] - output_hp[i]
#                if diff <= hr.el_power + hr.efficiency:
#                    output_hr.append(diff)
#                else:
#                    output_hr.append(hr.el_power + hr.efficiency)
#            else:
#                output_hr.append(0)
    
    # parallel mode
    if mode == "parallel":
        for i in range(len(dataframe)):
            # thermal output hp
            curr_th_power_hp = hp.el_power * hp.get_current_cop(temperature[i])
            if th_energy_demand[i] <= curr_th_power_hp:
                output_hp.append(th_energy_demand[i])
                hp_capable.append(True)
            else:
                output_hp.append(curr_th_power_hp)
                hp_capable.append(False)
            
        for i in range(len(dataframe)):
            # thermal output hr
            if bools_temp[i] or not hp_capable[i]:
                diff = th_energy_demand[i] - output_hp[i]
                if diff <= hr.el_power * hr.efficiency:
                    output_hr.append(diff)
                else:
                    output_hr.append(hr.el_power * hr.efficiency)
            else:
                output_hr.append(0)
                
                
    # alternative mode
    if mode == "alternative":
        # determine heat pump thermal output (heat pump running if t >= t_biv)
        for i in range(len(dataframe)):
            if bools_temp[i] == False:
                curr_th_power_hp = hp.el_power * hp.get_current_cop(temperature[i])
                if th_energy_demand[i] <= curr_th_power_hp:
                    output_hp.append(th_energy_demand[i])
                    hp_capable.append(True)
                else:
                    output_hp.append(curr_th_power_hp)#hp.el_power * hp.get_current_cop(temperature[i]))
                    hp_capable.append(False)
            else:
                output_hp.append(0)
                hp_capable.append(False)
                
        # determine heating rod thermal output
        for i in range(len(dataframe)):
            if bools_temp[i]:
                if th_energy_demand[i] <= hr.el_power * hr.efficiency:
                    output_hr.append(th_energy_demand[i])
                    hr_working.append(True)
                else:
                    output_hr.append(hr.el_power * hr.efficiency)
                    hr_working.append(True)
            else:
                output_hr.append(0)
                hr_working.append(False)
                
        for i in range(len(dataframe)):
            if not hp_capable[i] or not hr_working[i]:
                diff = th_energy_demand[i] - output_hp[i]
                if diff <= hr.el_power * hr.efficiency:
                    output_hr[i] = diff
                else:
                    output_hr[i] = hr.el_power * hr.efficiency

                
    th_output_hp = pd.DataFrame(data = output_hp, columns = ['th_output_hp'],
                                index = dataframe.index)
    
    th_output_hr = pd.DataFrame(data = output_hr, columns = ['th_output_hr'],
                                index = dataframe.index)
    
    dataframe = pd.concat([dataframe, th_output_hp, th_output_hr], axis = 1)
    
    # determine electrical demand of heat pump and heating rod
    for i in range(len(dataframe)):
        demand_hp.append(output_hp[i] / hp.get_current_cop(temperature[i]))
        demand_hr.append(output_hr[i] / hr.efficiency)
        
    el_demand_hp = pd.DataFrame(data = demand_hp, columns = ['el_demand_hp'],
                                index = dataframe.index)
    
    el_demand_hr = pd.DataFrame(data = demand_hr, columns = ['el_demand_hr'],
                                index = dataframe.index)
    
    for i in range(len(dataframe)):
        cops_hp.append(hp.get_current_cop(temperature[i]))
        
    cops = pd.DataFrame(data = cops_hp, columns = ['cop'], index = dataframe.index)
    
    dataframe = pd.concat([dataframe, el_demand_hp, el_demand_hr, cops], axis = 1)
    
    return dataframe
