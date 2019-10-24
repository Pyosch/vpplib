# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 13:25:23 2019

@author: Sascha Birk
"""

from model.VPPEnvironment import VPPEnvironment
from model.VPPUserProfile import VPPUserProfile
from model.VPPEnergyStorage import VPPEnergyStorage
from model.VPPPhotovoltaic import VPPPhotovoltaic

import pandas as pd
import matplotlib.pyplot as plt

#environment
start = '2015-06-01 00:00:00'
end = '2015-06-07 23:45:00'
year = '2015'

#user_profile
latitude = 50.941357
longitude = 6.958307

#PV
unit = "kW"
name = 'bus'
module_lib = 'SandiaMod'
module = 'Canadian_Solar_CS5P_220M___2009_'
inverter_lib = 'cecinverter'
inverter = 'ABB__PVI_4_2_OUTD_S_US_Z_M_A__208_V__208V__CEC_2014_'
surface_tilt = 20
surface_azimuth = 200
modules_per_string = 4
strings_per_inverter = 2

#storage
timebase = 15
charge_efficiency = 0.98
discharge_efficiency = 0.98
max_power = 4 #kW
capacity = 4 #kWh
max_c = 1 #factor between 0.5 and 1.2

#test
timestamp_int = 48
timestamp_str = '2015-06-01 12:00:00'


environment = VPPEnvironment(timebase=timebase, start=start, end=end, year=year)
environment.get_pv_data(file="./input/pv/dwd_pv_data_2015.csv")

user_profile = VPPUserProfile(identifier=name, latitude=latitude,
                              longitude=longitude)

#create pv object and timeseries
pv = VPPPhotovoltaic(unit=unit, identifier=(name+'_pv'), 
                     environment=environment, 
                     user_profile=user_profile,
                     module_lib=module_lib, 
                     module=module, 
                     inverter_lib=inverter_lib, 
                     inverter=inverter,
                     surface_tilt=surface_tilt, 
                     surface_azimuth=surface_azimuth,
                     modules_per_string=modules_per_string, 
                     strings_per_inverter=strings_per_inverter)

pv.prepareTimeSeries()

#create storage object
storage = VPPEnergyStorage(unit = unit, identifier=(name+'_storage'), 
                           environment = environment, 
                           user_profile = user_profile, 
                           capacity=capacity, 
                           charge_efficiency=charge_efficiency, 
                           discharge_efficiency=discharge_efficiency, 
                           max_power=max_power, max_c=max_c)

baseload = pd.read_csv("./input/baseload/df_S_15min.csv")
baseload.drop(columns=["Time"], inplace=True)
baseload.set_index(environment.pv_data.index, inplace = True)

#combine baseload and pv timeseries to get residual load
house_loadshape = pd.DataFrame(baseload['0'].loc[start:end]/1000)
house_loadshape['pv_gen'] = pv.timeseries.loc[start:end]
house_loadshape['residual_load'] = baseload['0'].loc[start:end]/1000 - pv.timeseries.bus_pv

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