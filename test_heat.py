# -*- coding: utf-8 -*-
"""
Info
----
In this testfile the basic functionalities of the VPPHeatPump class are tested.
Run each time you make changes on an existing function.
Adjust if a new function is added or 
parameters in an existing function are changed.

"""

from model.VPPUserProfile import VPPUserProfile
from model.VPPEnvironment import VPPEnvironment
from model.VPPHeatPump import VPPHeatPump
import matplotlib.pyplot as plt

#Values for environment
start = '2017-01-01 00:00:00'
end = '2017-01-14 23:45:00'
year = '2017'
time_freq = "15 min"
timestamp_int = 48
timestamp_str = '2017-01-01 12:00:00'
timebase = 15

#Values for user_profile
yearly_heat_demand = 12500
building_type = 'DE_HEF33'
t_0 = 40

#Values for Heatpump
el_power = 5 #kW electric
rampUpTime = 1/15 #timesteps
rampDownTime = 1/15 #timesteps
min_runtime = 1 #timesteps
min_stop_time = 2 #timesteps

environment = VPPEnvironment(timebase=timebase, start=start, end=end, year=year,
                             time_freq=time_freq)

user_profile = VPPUserProfile(yearly_heat_demand=yearly_heat_demand, t_0=t_0)

hp = VPPHeatPump(identifier='hp1', environment=environment, user_profile = user_profile,
                 el_power = el_power, rampUpTime = rampUpTime, 
                 rampDownTime = rampDownTime, 
                 min_runtime = min_runtime, 
                 min_stop_time = min_stop_time)

def test_get_cop(hp):
    
    print('get_cop:')
    hp.get_cop()
    hp.cop.plot(figsize=(16,9))
    plt.show()
    
    
def test_prepareTimeseries(hp):
    
    print('prepareTimeseries:')
    hp.prepareTimeSeries()
    hp.timeseries.plot(figsize=(16,9))
    plt.show()
    
def test_valueForTimestamp(hp, timestamp):
    
    print('valueForTimestamp:')
    demand= hp.valueForTimestamp(timestamp)
    print("El. Demand: ",demand, '\n')
    
def test_observationsForTimestamp(hp, timestamp):
    
    print('observationsForTimestamp:')
    observation = hp.observationsForTimestamp(timestamp)
    print(observation, '\n')
    
test_prepareTimeseries(hp)  
test_get_cop(hp)
test_valueForTimestamp(hp, timestamp_int)
test_observationsForTimestamp(hp, timestamp_int)

test_valueForTimestamp(hp, timestamp_str)
test_observationsForTimestamp(hp, timestamp_str)
