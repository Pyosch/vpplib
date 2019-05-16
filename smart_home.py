# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 10:46:23 2018

@author: Sascha Birk
"""

import pandas as pd
import heatpump as hp
import bev as bev

def import_loadshape(filepath, index = 0):
    
    df = pd.DataFrame()
    df = pd.read_csv(filepath, delimiter = ';')

    #If index is needed:
    if index:
        df.set_index(df.Time, inplace = True)
        del df['Time']
        
    return df

# In[Starting DataFrame]:

def new_scenario(start = '2017-01-01 00:00:00', 
                 end = '2017-12-31 23:45:00', 
                 periods = None, freq = "15 min", column = 'Demand'):

    df_main = pd.DataFrame(pd.date_range(start, end, periods, freq, name ='Time'))
    df_main[column] = 0
    
    return df_main

# In[Photovoltaik]:

def pv_generation(pv, pv_size, df = new_scenario(column = "pv_generation")):
    
    if not "pv_generation" in df:
        df["pv_generation"] = pv.Generation * pv_size
        
    if "pv_generation" in df:
        df["pv_generation"] = df.pv_generation + (pv.Generation * pv_size)
        
    return df

# In[Battery electric vehicle]:

def bev_loadshape(work_start, work_end, weekend_trip_start, weekend_trip_end, battery_min, battery_max, charging_power, efficiency, battery_usage, time_base, df = new_scenario()):
    
    df = bev.split_time(df)
    
    df = bev.at_home(df, work_start, work_end, weekend_trip_start, weekend_trip_end)
    
    df = bev.charge(df, battery_min, battery_max, charging_power, efficiency, battery_usage, time_base )
    
    return df

# In[Heatpump]:
    
def hp_loadshape(building_type, SigLinDe, mean_temp_days, t_0, demand_daily, mean_temp_hours, heatpump_type, water_temp, hours_year, heatpump_power, df):
    #calculate the building parameters
    b_params = [] #[A, B, C, D, m_H, b_H, m_W, b_W]
    b_params = hp.building_parameters(building_type, SigLinDe)
    
    h_del = hp.h_del(mean_temp_days, b_params, t_0)
    
    heat_demand_daily = hp.daily_demand(h_del, mean_temp_days.Mean_Temp, demand_daily)
        
    df_cop = hp.cop(mean_temp_hours, heatpump_type, water_temp)
    
    Q_N = hp.demandfactor(hours_year, heatpump_power)
        
    K_w = hp.consumerfactor(Q_N, h_del)
    
    heat_demand_h = hp.hourly_heat_demand(heat_demand_daily, K_w)
    
    el_demand_h = hp.hourly_el_demand(heat_demand_h, df_cop)
    el_demand_h.dropna(inplace = True)
    
    df_h = new_scenario(freq = "H")
    df_h["Demand"] = el_demand_h
    df_h.dropna(inplace = True)
    
    temp = hp.hour_to_qarter(df_h)
    temp.reset_index(inplace = True)
    
    df["hp_demand"] = temp.Demand
    
    return df

# In[Calculate overall house loadshape]:

def combine_loadshapes(df):
    
    #Handle exeption in case not all loadshapes exist
    if 'hp_demand' not in df:
        df['hp_demand'] = 0
    if 'car_charger' not in df:
        df['car_charger'] = 0    
    if 'pv_generation' not in df:
        df['pv_generation'] = 0 
        
    df['house_demand'] =  df.baseload + df.hp_demand + df.car_charger - df.pv_generation
    
    return df

# In[El home storage]:
def el_storage(df, init_storage_charge, storage_max, charger_power, time_base):
    
    #add data to processing data frame. Battery model handels generation positive, demand negative
    df['house_demand'] *= -1
    lst_storage = []
    lst_demand = []
    storage_charge = init_storage_charge
    rest = 0 #reset

    for i, d in df.iterrows():

        #If the house would feed electricity into the grid, charge the storage first. 
        #No electricity exchange with grid as long as charger power is not ecxeeded
        if (d.house_demand > 0) & (storage_charge < storage_max):

            #Check if energy produced exceeds charger power
            if (d.house_demand < charger_power):
                storage_charge = storage_charge + (d.house_demand * 0.98 * time_base)
                rest = 0
            #If it does, feed the rest to the grid
            else:
                storage_charge = storage_charge + (charger_power * 0.98 * time_base)
                rest = d.house_demand - charger_power

            #If the storage would be overcharged, feed the 'rest' to the grid
            if (storage_charge > storage_max):                                  
                rest = ((storage_charge - storage_max)/ time_base)
                storage_charge = storage_max

        #If the house needs electricity from the grid, discharge the storage first. 
        #In this case d.house_demand is negative! 
        #No electricity exchange with grid as long as demand does not exceed charger power
        elif (d.house_demand < 0) & (storage_charge > 0):

            #Check if energy demand exceeds charger power
            if (d.house_demand < (charger_power * -1)):
                storage_charge = (storage_charge) - (charger_power * 1.02 * time_base)
                rest = d.house_demand + charger_power

            else:
                storage_charge = (storage_charge)  + (d.house_demand * 1.02 * time_base)
                rest = 0

            #If the storage would be undercharged, take the 'rest' from the grid
            if (storage_charge < 0):  
                #since storage_charge is negative in this case it can be taken as demand
                rest = (storage_charge / time_base) #kWh / h = kW
                storage_charge = 0

        #If the storage is full or empty, the demand is not affected
        #elif(storage_charge == 0) | (storage_charge == storage_max):
        else:
            rest = d.house_demand


        lst_storage.append(storage_charge)
        lst_demand.append(rest*-1)
        
    df["house_demand"] = lst_demand
    df["storage_charge"] = lst_storage
    
    return df

#    df_storage = pd.DataFrame(lst_storage)
#    df_Storage_Charge[column] = df_storage[0]
#    df_main[column] = lst_demand
#    df_Storage_Charge.set_index(df_Storage_Charge.Time, inplace = True)
#    del df_Storage_Charge['Time']
#    df_Storage_Charge.to_pickle(OUTPUT + SZENARIO +'/df_Storage_Charge.pkl')