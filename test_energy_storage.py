# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 13:25:23 2019

@author: Sascha Birk
"""

from model.VPPEnergyStorage import VPPEnergyStorage
from model.VPPPhotovoltaic import VPPPhotovoltaic

import pandas as pd
import matplotlib.pyplot as plt

#PV
latitude = 50.941357
longitude = 6.958307
name = 'Cologne'
start = '2017-06-01 00:00:00'
end = '2017-06-07 23:45:00'
year = '2017'

#storage
timebase = 15/60
chargeEfficiency = 0.98
dischargeEfficiency = 0.98
maxPower = 4 #kW
capacity = 4 #kWh
maxC = 1 #factor between 0.5 and 1.2

#test
timestamp_int = 48
timestamp_str = '2017-06-01 12:00:00'

#input data
baseload = pd.read_csv("./Input_House/Base_Szenario/df_S_15min.csv")
baseload.set_index(baseload.Time, inplace = True)
baseload.drop(labels="Time", axis=1, inplace = True)

weather_data = pd.read_csv("./Input_House/PV/2017_irradiation_15min.csv")
weather_data.set_index("index", inplace = True)

#create pv object and timeseries
pv = VPPPhotovoltaic(timebase=1, identifier=(name+'_PV'), latitude=latitude, longitude=longitude, environment = None, userProfile = None,
                     start = start, end = end,
                     module_lib = 'SandiaMod', module = 'Canadian_Solar_CS5P_220M___2009_', 
                     inverter_lib = 'cecinverter', inverter = 'ABB__PVI_4_2_OUTD_S_US_Z_M_A__208_V__208V__CEC_2014_',
                     surface_tilt = 20, surface_azimuth = 200,
                     modules_per_string = 4, strings_per_inverter = 2)

pv.prepareTimeSeries(weather_data)

#create storage object
storage = VPPEnergyStorage(timebase = timebase, identifier=(name+'_storage'), capacity=capacity, 
                           chargeEfficiency=chargeEfficiency, 
                           dischargeEfficiency=dischargeEfficiency, 
                           maxPower=maxPower, maxC=maxC, 
                           environment = None, userProfile = None)

#combine baseload and pv timeseries to get residual load
house_loadshape = pd.DataFrame(baseload['0'].loc[start:end]/1000)
house_loadshape['pv_gen'] = pv.timeseries.loc[start:end]
house_loadshape['residual_load'] = baseload['0'].loc[start:end]/1000 - pv.timeseries.Cologne_PV

#assign residual load to storage
storage.residual_load = house_loadshape.residual_load

def test_prepareTimeSeries(storage):
    
    storage.prepareTimeSeries()
    print("prepareTimeSeries:")
    print(storage.timeseries.head()) 
    storage.timeseries.plot(figsize=(16,9))
    plt.show()
    
def test_valueForTimestamp(storage, timestamp):
    
    timestepvalue = storage.valueForTimestamp(timestamp)
    print("\nvalueForTimestamp:\n", timestepvalue)
    
def test_observationsForTimestamp(storage, timestamp):
    
    print('observationsForTimestamp:')
    observation = storage.observationsForTimestamp(timestamp)
    print(observation, '\n')
    
def test_operate_storage(storage, timestamp):
    
    print('operate_storage:')
    state_of_charge, res_load = storage.operate_storage(storage.residual_load.loc[timestamp])
    print('state_of_charge: ', state_of_charge)
    print('res_load: ', res_load)
    
test_prepareTimeSeries(storage)
test_valueForTimestamp(storage, timestamp_int)
test_valueForTimestamp(storage, timestamp_str)

test_observationsForTimestamp(storage, timestamp_int)
test_observationsForTimestamp(storage, timestamp_str)

test_operate_storage(storage, timestamp_str)