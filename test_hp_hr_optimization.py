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

hr = HeatingRod(identifier='hr1', 
                 environment=environment, user_profile = user_profile,
                 #el_power = el_power,
                 rampUpTime = ramp_up_time, 
                 rampDownTime = ramp_down_time, 
                 min_runtime = min_runtime, 
                 min_stop_time = min_stop_time)


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

# as basis, create dataframe containing temperature and heat demand over time
heat_demand = user_profile.thermal_energy_demand
temperature = pd.read_csv("./input/thermal/dwd_temp_15min_2015.csv", index_col="time")
dataframe = pd.concat([heat_demand, temperature], axis = 1)
print(str(dataframe))

# get point p0 (lowest temperature and corresponding (highest) heat demand)
T_p0 = round(float(dataframe['temperature'].min()), 1)
P_p0 = round(float(dataframe['thermal_energy_demand'].max()), 1) 
p0 = [T_p0, P_p0]
print(str(p0))

# get point p1 (heatstop temperature and corrsponding (0kW) heat demand)
T_p1 = 20   # choose reasonable value
P_p1 = 0
p1 = [T_p1, P_p1]

# calculate parameter a of linear function P(T)=a*T+b
a = (P_p1 - P_p0) / (T_p1 - T_p0)

# calculate parameter b: b=P(T)-a*T
b = 0 - a * 20

# bivalence temerature (determine with tabels in Vaillant hand book)
T_biv = -6.5

# calculate corresponding heat demand (equals thermal power of heat pump)
P_biv = a * T_biv + b
print("thermischer Bedarf im Bivalenzpunkt: " + str(P_biv) + " [kW]")

# thermal power hp
th_pwr_hp = round(float(P_biv), 1)
print("thermische Leistung der Wärmepumpe: " + str(th_pwr_hp) + " [kW]")

#thermal power hr
th_pwr_hr = round(float(P_p0 - th_pwr_hp), 1)
print("thermische Leistung des Heizstabs: " + str(th_pwr_hr) + " [kW]")
