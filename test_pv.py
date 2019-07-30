# -*- coding: utf-8 -*-
"""
Info
----
In this testfile the basic functionalities of the VPPPhotovoltaic class are tested.
Run each time you make changes on an existing function.
Adjust if a new function is added or 
parameters in an existing function are changed.

"""

import pandas as pd
import matplotlib.pyplot as plt

from model.VPPPhotovoltaic import VPPPhotovoltaic


latitude = 50.941357
longitude = 6.958307
name = 'Cologne'
start = '2017-01-01 00:00:00'
end = '2017-01-01 23:45:00'
timestamp_int = 48
timestamp_str = '2017-01-01 12:00:00'

weather_data = pd.read_csv("./Input_House/PV/2017_irradiation_15min.csv")
weather_data.set_index("index", inplace = True)

pv = VPPPhotovoltaic(timebase=1, identifier=name, latitude=latitude, longitude=longitude, environment = None, userProfile = None,
                     start = start, end = end,
                     module_lib = 'SandiaMod', module = 'Canadian_Solar_CS5P_220M___2009_', 
                     inverter_lib = 'cecinverter', inverter = 'ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_',
                     surface_tilt = 20, surface_azimuth = 200,
                     modules_per_string = 1, strings_per_inverter = 1)

def test_prepareTimeSeries(pv, weather_data):
    
    pv.prepareTimeSeries(weather_data)
    print("prepareTimeSeries:")
    print(pv.timeseries.head())
    pv.timeseries.plot(figsize=(16,9))
    plt.show()

def test_valueForTimestamp(pv, timestamp):
    
    timestepvalue = pv.valueForTimestamp(timestamp)
    print("\nvalueForTimestamp:\n", timestepvalue)
    
def observationsForTimestamp(pv, timestamp):
    
    print('observationsForTimestamp:')
    observation = pv.observationsForTimestamp(timestamp)
    print(observation, '\n')
    
    
test_prepareTimeSeries(pv, weather_data)
test_valueForTimestamp(pv, timestamp_int)
test_valueForTimestamp(pv, timestamp_str)

observationsForTimestamp(pv, timestamp_int)
observationsForTimestamp(pv, timestamp_str)