# -*- coding: utf-8 -*-
"""
Info
----
In this testfile the basic functionalities of the VPPHeatPump class are tested.
Run each time you make changes on an existing function.
Adjust if a new function is added or 
parameters in an existing function are changed.

"""

from model.VPPHeatPump import VPPHeatPump
import matplotlib.pyplot as plt


start = '2017-01-01 00:00:00'
end = '2017-01-14 23:45:00'
freq = "15 min"
timestamp_int = 48
timestamp_str = '2017-01-01 12:00:00'

hp = VPPHeatPump(identifier = "House 1", timebase = 1, heatpump_type = "Air", 
                 heat_sys_temp = 60, environment = None, userProfile = None, 
                 heatpump_power = 10.6, full_load_hours = 2100, heat_demand_year = None,
                 building_type = 'DE_HEF33', start = start,
                 end = end, year = '2017')

def test_get_heat_demand(hp):
    
    print('get_heat_demand:')
    hp.get_heat_demand()
    hp.heat_demand.plot(figsize=(16,9))
    plt.show()

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
test_get_heat_demand(hp)
test_get_cop(hp)
test_valueForTimestamp(hp, timestamp_int)
test_observationsForTimestamp(hp, timestamp_int)

test_valueForTimestamp(hp, timestamp_str)
test_observationsForTimestamp(hp, timestamp_str)
