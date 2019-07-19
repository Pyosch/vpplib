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

bev = VPPBEV(timebase=15/60, identifier='bev_1', 
             start = '2017-06-01 00:00:00', end = '2017-06-01 23:45:00', time_freq = "15 min", 
             battery_max = 16, battery_min = 0, battery_usage = 1, 
             charging_power = 11, chargeEfficiency = 0.98, 
             environment=None, userProfile=None)
    
def test_prepareTimeSeries(bev):
    
    bev.prepareTimeSeries()
    print("prepareTimeSeries:")
    print(bev.timeseries.head()) 
    bev.timeseries.plot()
    plt.show()
    
def test_valueForTimestamp(bev):
    
    timestepvalue = bev.valueForTimestamp(48)
    print("\nvalueForTimestamp:\n", timestepvalue)
    
test_prepareTimeSeries(bev)
test_valueForTimestamp(bev)
    