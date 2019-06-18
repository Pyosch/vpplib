# -*- coding: utf-8 -*-
"""
Info
----
In this testfile the basic functionalities of the VPPBEV class are tested.
Run each time you make changes on an existing function.
Adjust if a new function is added or 
parameters in an existing function are changed.

"""

from Model.VPPBEV import VPPBEV
import matplotlib.pyplot as plt

bev = VPPBEV(1,2,3,2017)

def test_prepareTimeSeries(bev):
    
    bev.prepareTimeSeries()
    bev.prepareBEV()
    print("prepareTimeSeries:")
    print(bev.timeseries.head()) 
    bev.timeseries.plot()
    plt.show()
    
def test_valueForTimestamp(bev):
    
    timestepvalue = bev.valueForTimestamp(300)
    print("\nvalueForTimestamp:\n", timestepvalue)
    
test_prepareTimeSeries(bev)
test_valueForTimestamp(bev)