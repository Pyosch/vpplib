# -*- coding: utf-8 -*-
"""
Info
----
In this testfile the basic functionalities of the VPPBEV class are tested.
Run each time you make changes on an existing function.
Adjust if a new function is added or 
parameters in an existing function are changed.

"""
from model.VPPUserProfile import VPPUserProfile
from model.VPPEnvironment import VPPEnvironment
from model.VPPBEV import VPPBEV
import matplotlib.pyplot as plt

identifier = 'bev_1'
start = '2015-06-01 00:00:00'
end = '2015-06-01 23:45:00'
timebase = 15
timestamp_int = 48
timestamp_str = '2015-06-01 12:00:00'

charging_power = 11
battery_max = 16
battery_min = 0
battery_usage = 1
charge_efficiency = 0.98
load_degradiation_begin = 0.8

environment = VPPEnvironment(start=start, end=end, timebase=timebase)

user_profile = VPPUserProfile(identifier=identifier)


bev = VPPBEV(unit="kW", identifier=None,
             environment=environment, user_profile=user_profile,
             battery_max=battery_max, battery_min=battery_min, 
             battery_usage=battery_usage, 
             charging_power=charging_power, 
             load_degradiation_begin=load_degradiation_begin, 
             charge_efficiency=charge_efficiency)
    
def test_prepareTimeSeries(bev):
    
    bev.prepareTimeSeries()
    print("prepareTimeSeries:")
    print(bev.timeseries.head()) 
    bev.timeseries.plot(figsize=(16,9))
    plt.show()
    
def test_valueForTimestamp(bev, timestamp):
    
    timestepvalue = bev.valueForTimestamp(timestamp)
    print("\nvalueForTimestamp:\n", timestepvalue)
    
def test_observationsForTimestamp(bev, timestamp):
    
    print('observationsForTimestamp:')
    observation = bev.observationsForTimestamp(timestamp)
    print(observation, '\n')
    
test_prepareTimeSeries(bev)
test_valueForTimestamp(bev, timestamp_int)
test_valueForTimestamp(bev, timestamp_str)

test_observationsForTimestamp(bev, timestamp_int)
test_observationsForTimestamp(bev, timestamp_str)