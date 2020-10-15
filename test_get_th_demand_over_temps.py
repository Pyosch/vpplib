# -*- coding: utf-8 -*-
"""
Created on Sun Oct  4 09:14:06 2020

@author: andre
get the heat demand over temperaturer
"""

from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.heat_pump import HeatPump
from vpplib.heating_rod import HeatingRod
from fct_optimize_bivalent import optimize_bivalent
from fct_run_hp_hr import run_hp_hr
from fct_determin_heating_ratio import determin_heating_ratio
import matplotlib.pyplot as plt
import pandas as pd

#Values for environment
start = '2015-01-01 00:00:00'
end = '2015-12-31 23:45:00'
year = '2015'
time_freq = "15 min"
timestamp_int1 = 48
timestamp_int2 = 500
timestamp_str1 = '2015-01-01 12:00:00'
timestamp_str2 = '2015-01-10 06:00:00'
timebase = 15

#Values for user_profile
thermal_energy_demand_yearly = 10000
building_type = 'DE_HEF33'
t_0 = 40

environment = Environment(timebase=timebase, start=start, end=end, year=year,
                          time_freq=time_freq)

user_profile = UserProfile(identifier=None,
                           latitude=None,
                           longitude=None,
                           thermal_energy_demand_yearly=thermal_energy_demand_yearly,
                           building_type=building_type,
                           comfort_factor=None,
                           t_0=t_0)

def test_get_thermal_energy_demand(user_profile):
    
    user_profile.get_thermal_energy_demand()
    #user_profile.thermal_energy_demand.plot()
    #plt.show()


test_get_thermal_energy_demand(user_profile)

df_temps = pd.read_csv("./input/thermal/dwd_temp_15min_2015.csv", index_col="time")

print(df_temps)

df_dem_temps = pd.concat([user_profile.thermal_energy_demand, df_temps], axis = 1)

df_dem_temps.sort_values(by = "temperature", ascending = True, inplace = True)
print(df_dem_temps)

x = df_dem_temps.temperature.values
y = df_dem_temps.thermal_energy_demand.values

plt.plot(x, y)
plot.show()