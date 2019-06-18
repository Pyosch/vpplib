# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 11:31:31 2019

@author: Sascha Birk
"""

import pandas as pd

from Model import VPPPhotovoltaik


latitude = 50.941357
longitude = 6.958307
name = 'Cologne'

weather_data = pd.read_csv("./Input_House/PV/2017_irradiation_15min.csv")
weather_data.set_index("index", inplace = True)

pv = VPPPhotovoltaik.VPPPhotovoltaik(timebase=1, identifier=name, latitude=latitude, longitude=longitude, modules_per_string=1, strings_per_inverter=1)

def test_prepareTimeSeries(pv, weather_data):
    
    pv.prepareTimeSeries(weather_data)
    print("prepareTimeSeries:")
    print(pv.timeseries.head())

def test_valueForTimestamp(pv):
    
    i = 15024
    timestepvalue = pv.valueForTimestamp(timestamp = i)
    print("\nvalueForTimestamp:\n", timestepvalue)
    
test_prepareTimeSeries(pv, weather_data)
test_valueForTimestamp(pv)