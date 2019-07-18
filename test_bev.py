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

bev = VPPBEV(timebase=15/60, identifier=2, peakPower=3, year=2017, battery_max = 16, charging_power = 11)
    
def test_prepareTimeSeries(bev):
    
    bev.prepareTimeSeries()
    print("prepareTimeSeries:")
    print(bev.timeseries.head()) 
    bev.timeseries.plot()
    plt.show()
    
def test_valueForTimestamp(bev):
    
    timestepvalue = bev.valueForTimestamp(300)
    print("\nvalueForTimestamp:\n", timestepvalue)
    
test_prepareTimeSeries(bev)
test_valueForTimestamp(bev)
    