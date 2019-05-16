# -*- coding: utf-8 -*-
"""
Created on Thu May 24 13:47:36 2018

@author: Sascha Birk
"""
# In[Determine Runtime]:

import time
#Processingtime in minutes
timer_start = time.time()

# In[set up environment]

import os
import pandas as pd
import matplotlib.pyplot as plt
import smart_home as smart_home
import random as random
    
filepath = "C:/Users/Sascha Birk/sciebo/Programmierung/RL_Energiesystem/Lastprofilgenerator/Input_House/Base_Szenario/HTW_Data/"

OUTPUT = './Results/'
SZENARIO = 'residual_load'
if not os.path.exists(OUTPUT + SZENARIO):
    os.makedirs(OUTPUT + SZENARIO)
    
# In[Determine scenario parameters]:
    
number_of_buses = 1
df_htw = pd.read_csv(filepath + 'df_S_15min.csv') #74 baseloadprofiles from HTW Berlin in Watt. Named 0-73

start = '2017-06-01 00:00:00'
end = '2017-06-02 00:00:00'

# In[Input PV]:

pv_percentage = 100 #%
pv_size = 1 #power in kWp
#pv_generation = pd.read_pickle("./Input_House/PV/Solar_Reference_PLZ_5_H.pkl") #hourly timebase
irradiation = pd.read_csv("./Input_House/PV/Solar_Data-Random.csv", delimiter = ";") #15-min timebase
#irradiation.reset_index(inplace = True)

# In[El. Home Storage]:

storage_percentage = 0 #%

nr_storage = 1
storage_max = nr_storage * 3  #Capacity in kWh
charger_power = nr_storage * 3.3 #Charging power in kW
init_storage_charge = 0.0 #Current state of charge

# In[Input Heatpump]:

hp_percentage = 0 #%

SigLinDe = pd.read_csv("./Input_House/heatpump_model/SigLinDe.csv", decimal=",")
building_type_lst = ['DE_HMF33', 'DE_HMF34']
#import table to distribute daily demand load over 24 hours
demand_daily = pd.read_csv('./Input_House/heatpump_model/demand_daily.csv')

mean_temp_hours = pd.read_csv('./Input_House/heatpump_model/mean_temp_hours_2017.csv', header = None)

mean_temp_days = pd.DataFrame(pd.date_range("2017-01-01","2017-12-31",freq="D", name = 'Time'))
mean_temp_days['Mean_Temp'] = pd.read_csv("./Input_House/heatpump_model/mean_temp_days_2017.csv", header = None)

#Hours of usage per year. According to BDEW multi family homes: 2000, single family homes: 2100
hours_year = 2000
heatpump_power_lst = [10.6, 14.5, 18.5] #power in kW
heatpump_type = "Air"
#Reference temperature for SigLinDe funktion
t_0 = 40 #°C
water_temp = 60


# In[Input BEV]:

#time_base = 1 #for hourly loadshapes
time_base = 15/60 #for loadshapes with steps, smaller than one hour (eg. 15 minutes)

#Input electric vehicle
bev_percentage = 0 #%

efficiency = 0.98
charging_power = 11 #kW
battery_max = 20 #max capacity in kWh
battery_min = 2 #min capacity in kWh
#kW, discharge car battery with battery_usage * time_base. 
#Determines charge needed when returned home
battery_usage = 1 
weekend_trip_start = ['08:00:00', '08:15:00', '08:30:00', '08:45:00', 
                      '09:00:00', '09:15:00', '09:30:00', '09:45:00',
                      '10:00:00', '10:15:00', '10:30:00', '10:45:00', 
                      '11:00:00', '11:15:00', '11:30:00', '11:45:00', 
                      '12:00:00', '12:15:00', '12:30:00', '12:45:00', 
                      '13:00:00']

weekend_trip_end = ['17:00:00', '17:15:00', '17:30:00', '17:45:00', 
                    '18:00:00', '18:15:00', '18:30:00', '18:45:00', 
                    '19:00:00', '19:15:00', '19:30:00', '19:45:00', 
                    '20:00:00', '20:15:00', '20:30:00', '20:45:00', 
                    '21:00:00', '21:15:00', '21:30:00', '21:45:00', 
                    '22:00:00', '22:15:00', '22:30:00', '22:45:00', 
                    '23:00:00']

work_start = ['07:00:00', '07:15:00', '07:30:00', '07:45:00', 
              '08:00:00', '08:15:00', '08:30:00', '08:45:00', 
              '09:00:00']

work_end = ['16:00:00', '16:15:00', '16:30:00', '16:45:00', 
            '17:00:00', '17:15:00', '17:30:00', '17:45:00', 
            '18:00:00', '18:15:00', '18:30:00', '18:45:00', 
            '19:00:00', '19:15:00', '19:30:00', '19:45:00', 
            '20:00:00', '20:15:00', '20:30:00', '20:45:00', 
            '21:00:00', '21:15:00', '21:30:00', '21:45:00', 
            '22:00:00']

# In[Create a dictionary for the grid and include HTW data as 
#    baseload of the buses]:

grid_dict = {}
buses = range(number_of_buses)

for bus in buses:
    
    grid_dict[bus] = smart_home.new_scenario(column = 'baseload')
    
for bus, df in grid_dict.items():
    
    grid_dict[bus]['baseload'] = df_htw[str(bus)]/1000 #convert from W to kW
    
    
# In[Determine distribution of pv, heatpumps, bevs and el storage]:
    
pv_installations = int(round((len(grid_dict) * (pv_percentage/100)), 0))
buses_with_pv = random.sample(list(grid_dict), pv_installations)

hp_installations = int(round((len(grid_dict) * (hp_percentage/100)), 0))
buses_with_hp = random.sample(list(grid_dict), hp_installations)

bevs = int(round((len(grid_dict) * (bev_percentage/100)), 0))
buses_with_bev = random.sample(list(grid_dict), bevs)

#Distribution of el storage is only done for houses with pv
storage_installations = int(round((len(buses_with_pv) * (storage_percentage/100)), 0))
buses_with_storage = random.sample(buses_with_pv, storage_installations)
    
    
# In[Include pv loadshape]:

if len(buses_with_pv) > 0:
    
    for bus, df in grid_dict.items():
        if bus in buses_with_pv:
                
            grid_dict[bus] = smart_home.pv_generation(irradiation, pv_size, df)

# In[Include hp loadshape]:
    
if len(buses_with_hp) > 0:
    
    for bus, df in grid_dict.items():
        if bus in buses_with_hp:
                
            building_type = building_type_lst[random.randrange(0,(len(building_type_lst)),1)]
            heatpump_power = heatpump_power_lst[random.randrange(0,(len(heatpump_power_lst)),1)]
            
            grid_dict[bus] =  smart_home.hp_loadshape(building_type, SigLinDe, 
                                         mean_temp_days, t_0, demand_daily, 
                                         mean_temp_hours, heatpump_type, water_temp, 
                                         hours_year, heatpump_power, df)

# In[Include bev loadshape]:

if len(buses_with_bev) > 0:
    
    for bus, df in grid_dict.items():
        if bus in buses_with_bev:
    
            grid_dict[bus] = smart_home.bev_loadshape(work_start, work_end, 
                                         weekend_trip_start, weekend_trip_end, 
                                         battery_min, battery_max, charging_power, 
                                         efficiency, battery_usage, time_base, df)

# In[Combine all loadshapes to get overall house demand]:

for bus, df in grid_dict.items():
    
    grid_dict[bus] = smart_home.combine_loadshapes(df)

# In[Include home storage]:

if len(buses_with_storage) > 0:
    
    for bus, df in grid_dict.items():
        if bus in buses_with_storage:
                
            grid_dict[bus] = smart_home.el_storage(df, init_storage_charge, storage_max, charger_power, time_base)

# In[Set Index]:

for bus, df in grid_dict.items():
    
    grid_dict[bus].set_index('Time', inplace = True, drop = True)
    
# In[Combine final loadshapes of all buses in one file]:

grid_dict['loadshapes'] = pd.DataFrame(pd.date_range(start, end, freq = '15 min', name ='Time'))
grid_dict['loadshapes'].set_index('Time', inplace = True, drop = True)
  
for bus, df in grid_dict.items():
    
    if bus is not 'loadshapes':
        
        grid_dict['loadshapes'][bus] = grid_dict[bus].house_demand

# In[Save to file]:

grid_dict['loadshapes'].to_csv(OUTPUT + SZENARIO + '/grid_loadshapes.csv')

#%%
#print(grid_dict)
grid_dict['loadshapes'].plot()
plt.show()
#print(grid_dict[0].hp_demand)

#%% Tests
#for bus, df in grid_dict.items():
#    print(df)
#
#grid_dict[2].house_demand.plot()
#plt.show()
#grid_dict[2].storage_charge.loc['2017-03-01 00:00:00' : '2017-03-30 00:00:00'].plot()
#plt.show()

# In[Determine Runtime]:

#Processingtime in minutes
timer_end = time.time()
print('Runtime ' + str(round((timer_end-timer_start)/60, 2)) + ' Minutes')
