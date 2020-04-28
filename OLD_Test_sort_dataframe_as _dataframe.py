# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 15:21:01 2019

@author: andre

deprecated: see test_get_opt_power.py
"""

from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
import matplotlib.pyplot as plt
import pandas as pd
#import math

figsize = (10,6)
#Values for environment
start = '2015-01-01 00:00:00'
end = '2015-12-31 23:45:00'
year = '2015'

#Values for user_profile
thermal_energy_demand_yearly = 15000 # kWh
building_type = 'DE_HEF33'
t_0 = 40 # °C

#Values for Thermal Storage
target_temperature = 60 # °C
hysteresis = 5 # °K
mass_of_storage = 500 # kg

#Values for HeatingRod
el_power = 30 #kW electric
rampUpTime = 1/15 #timesteps
rampDownTime = 1/15 #timesteps
min_runtime = 1 #timesteps
min_stop_time = 2 #timesteps
timebase = 15

environment = Environment(timebase=timebase, start=start, end=end, year=year)

user_profile = UserProfile(identifier=None,
                                 latitude = None,
                                 longitude = None,
                                 thermal_energy_demand_yearly=thermal_energy_demand_yearly,
                                 building_type = building_type,
                                 comfort_factor = None,
                                 t_0=t_0)

# =============================================================================
# bis hierher nur Vorgeplänkel
# =============================================================================

def test_get_thermal_energy_demand(user_profile):
    
    user_profile.get_thermal_energy_demand()
    user_profile.thermal_energy_demand.plot()
    plt.show()
    
test_get_thermal_energy_demand(user_profile)

df = user_profile.get_thermal_energy_demand()
#print(df)
df_sorted = df.sort_values(by = 'thermal_energy_demand', ascending = False)
#print(df_sorted)

def test_get_hours_high_demand(high_demand):
    high_demand_filt = (df_sorted['thermal_energy_demand'] >= high_demand)
    hours = df_sorted[high_demand_filt].size / 4     #Viertelstunden nach Stunden
    #print(df_sorted[high_demand])
    return hours

hours_high_demand = 0
power = 6.2
iter_steps = 0
max_hours_exceeding_demand = 2500    
#für jeden Durchlauf wird geprüft, 
while (hours_high_demand < max_hours_exceeding_demand):
    hours_high_demand = test_get_hours_high_demand(power)
    print(str(hours_high_demand))
    power -= 0.1
    iter_steps += 1
    print(str(iter_steps))
    
print(str(round(power, 2)))
power_alternative = df_sorted.iloc[max_hours_exceeding_demand * 4]
print(str(round(power_alternative, 2)))
    

data = user_profile.get_thermal_energy_demand()
duration_curve = data.sort_values(by = ["thermal_energy_demand"], ascending = False)
duration_curve_x = range(35040)
duration_curve_y = duration_curve.values 
plt.plot(duration_curve_x, duration_curve_y)

