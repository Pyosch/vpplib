# -*- coding: utf-8 -*-
"""
Info
----
In this testfile the basic functionalities of the VPPBEV class are tested.
Run each time you make changes on an existing function.
Adjust if a new function is added or 
parameters in an existing function are changed.

"""

from model.VPPBEV import VPPBEV
import matplotlib.pyplot as plt

start = '2017-06-01 00:00:00'
end = '2017-06-01 23:45:00'
timestamp_int = 48
timestamp_str = '2017-06-01 12:00:00'

bev = VPPBEV(timebase=15/60, identifier='bev_1', 
             start = start, end = end, time_freq = "15 min", 
             battery_max = 16, battery_min = 0, battery_usage = 1, 
             charging_power = 11, chargeEfficiency = 0.98, 
             environment=None, userProfile=None)
    
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