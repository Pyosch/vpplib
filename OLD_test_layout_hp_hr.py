# -*- coding: utf-8 -*-
"""
Info
----
In this testfile the basic functionalities of the HeatPump class are tested.
Run each time you make changes on an existing function.
Adjust if a new function is added or 
parameters in an existing function are changed.

"""

from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.heat_pump import HeatPump
import matplotlib.pyplot as plt
import pandas as pd

#Values for environment
start = '2015-01-01 00:00:00'
end = '2015-01-14 23:45:00'
year = '2015'
time_freq = "15 min"
timestamp_int1 = 48
timestamp_int2 = 500
timestamp_str1 = '2015-01-01 12:00:00'
timestamp_str2 = '2015-01-10 06:00:00'
timebase = 15

#Values for user_profile
thermal_energy_demand_yearly = 12500
building_type = 'DE_HEF33'
t_0 = 40

#Values for Heatpump
#el_power = 5 #kW electric
ramp_up_time = 1 / 15 #timesteps
ramp_down_time = 1 / 15 #timesteps
min_runtime = 1 #timesteps
min_stop_time = 2 #timesteps
heat_pump_type = "Ground" #nur "Ground" oder "Air"!


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
    user_profile.thermal_energy_demand.plot()
    plt.show()


test_get_thermal_energy_demand(user_profile)


hp = HeatPump(identifier='hp',
              environment=environment, user_profile=user_profile,
              #el_power=el_power,
              ramp_up_time=ramp_up_time,
              ramp_down_time=ramp_down_time, heat_pump_type = heat_pump_type,
              min_runtime=min_runtime,
              min_stop_time=min_stop_time)


def test_get_cop(hp):
    
    print('get_cop:')
    hp.get_cop()
    hp.cop.plot(figsize=(16,9))
    plt.show()
    
    
def test_prepare_timeseries(hp):
    
    print('prepareTimeseries:')
    hp.prepare_time_series()
    hp.timeseries.plot(figsize=(16,9))
    plt.show()
    
def test_value_for_timestamp(hp, timestamp):
    
    print('value_for_timestamp:')
    demand= hp.value_for_timestamp(timestamp)
    print("El. Demand: ", demand, '\n')
    
def test_observations_for_timestamp(hp, timestamp):
    
    print('observations_for_timestamp:')
    observation = hp.observations_for_timestamp(timestamp)
    print(observation, '\n')


#------------------------------------------------------------------------------
# print heat_demand and temperature over time to show they dont fit together exactly
#------------------------------------------------------------------------------
print(str(user_profile.get_thermal_energy_demand_hourly()))
heat_demand_sorted = user_profile.thermal_energy_demand_hourly.sort_values(by =[0], ascending = False)
# key bei thermal_energy_demand_hourly anscheinend falsch => wie heißt der?

heat_demand_sorted = user_profile.thermal_energy_demand.sort_values(by =['thermal_energy_demand'], ascending = False)
# das hat jetzt viertelstündliche Auflösung, also muss mean_temp_hours (stündliche
# Auflösug) auch noch interpoliert werden

# mean_temp_hours interpolieren auf Viertelstunde 
temperature_interpolated = pd.read_csv("./input/thermal/dwd_temp_15min_2015.csv", index_col="time")
print(str(temperature_interpolated))
dataframe = pd.concat([heat_demand_sorted, temperature_interpolated], axis = 1)
dataframe.sort_values(by = ['temperature'], ascending = False, inplace = True)


print(str(dataframe))

# liefert nur NaN (?)

print(str(temperature_interpolated))


x = dataframe['temperature'].values
y = range(len(dataframe['temperature'].values))
# =============================================================================
# y2 = temperature_interpolated.values
# x = range(35040)
# 
# plt.plot(x, y2)
# =============================================================================
print(str(y))
print(str(x))
plt.plot(y, x)


    
print(str(dataframe['temperature'].iat[3]))
#datframe_cold = 