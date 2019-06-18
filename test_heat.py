# -*- coding: utf-8 -*-
"""
Info
----
In this testfile the basic functionalities of the VPPHeatPump class are tested.
Run each time you make changes on an existing function.
Adjust if a new function is added or 
parameters in an existing function are changed.

"""

from Model.VPPHeatPump import VPPHeatPump
import matplotlib.pyplot as plt
import pandas as pd


start = '2017-01-01 00:00:00'
end = '2017-12-31 23:45:00'
periods = None
freq = "15 min"

df_index = pd.DataFrame(pd.date_range(start, end, periods, freq, name ='Time'))

hp = VPPHeatPump(identifier = "House 1", df_index = df_index)

def test_get_heat_demand(hp):
    
    hp.get_heat_demand()
    hp.heat_demand.plot()
    plt.show()

def test_get_cop(hp):
    
    hp.get_cop()
    hp.cop.plot()
    plt.show()
    
    
def test_prepareTimeseries(hp):
    
    hp.prepareTimeSeries()
    hp.timeseries.plot()
    plt.show()
    
def test_valueForTimestamp(hp):
    
    i = 15024
    demand, cop = hp.valueForTimestamp(timestamp = i)
    print("Demand: ",demand)
    print("cop: ", cop)
    
    
test_prepareTimeseries(hp)  
test_get_heat_demand(hp)
test_get_cop(hp)
test_valueForTimestamp(hp)