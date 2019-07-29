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
capacity = 0
chargeEfficiency = 0.98
dischargeEfficiency = 0.98
maxPower = 4 #kW
maxC = 4

#test
timestamp_int = 48
timestamp_str = '2017-06-01 12:00:00'

baseload = pd.read_csv("./Input_House/Base_Szenario/df_S_15min.csv")
baseload.set_index(baseload.Time, inplace = True)
baseload.drop(labels="Time", axis=1, inplace = True)

weather_data = pd.read_csv("./Input_House/PV/2017_irradiation_15min.csv")
weather_data.set_index("index", inplace = True)

pv = VPPPhotovoltaic(timebase=1, identifier=name, latitude=latitude, longitude=longitude, environment = None, userProfile = None,
                     start = start, end = end,
                     module_lib = 'SandiaMod', module = 'Canadian_Solar_CS5P_220M___2009_', 
                     inverter_lib = 'cecinverter', inverter = 'ABB__PVI_4_2_OUTD_S_US_Z_M_A__208_V__208V__CEC_2014_',
                     surface_tilt = 20, surface_azimuth = 200,
                     modules_per_string = 4, strings_per_inverter = 2)

pv.prepareTimeSeries(weather_data)

storage = VPPEnergyStorage(timebase = timebase, capacity=capacity, 
                           chargeEfficiency=chargeEfficiency, 
                           dischargeEfficiency=dischargeEfficiency, 
                           maxPower=maxPower, maxC=maxC, 
                           environment = None, userProfile = None)

house_loadshape = pd.DataFrame(baseload['0'].loc[start:end]/1000)
house_loadshape['pv_gen'] = pv.timeseries.loc[start:end]
house_loadshape['loadshape'] = baseload['0'].loc[start:end]/1000 - pv.timeseries.Cologne


soc_lst = []
res_load_lst = []
for residual_load in house_loadshape.loadshape:
    
    soc, res_load = storage.operate_storage(residual_load=residual_load)
    soc_lst.append(soc)
    res_load_lst.append(res_load)

house_loadshape['stateOfCharge'] = soc_lst
house_loadshape['res_load'] = res_load_lst

house_loadshape.plot(figsize=(16,9))
plt.show()
