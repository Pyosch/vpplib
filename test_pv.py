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

from Model.VPPPhotovoltaic import VPPPhotovoltaic


latitude = 50.941357
longitude = 6.958307
name = 'Cologne'

weather_data = pd.read_csv("./Input_House/PV/2017_irradiation_15min.csv")
weather_data.set_index("index", inplace = True)

pv = VPPPhotovoltaic(timebase=1, identifier=name, latitude=latitude, longitude=longitude, modules_per_string=1, strings_per_inverter=1)

def test_prepareTimeSeries(pv, weather_data):
    
    pv.prepareTimeSeries(weather_data)
    print("prepareTimeSeries:")
    print(pv.timeseries.head())
    pv.timeseries.plot()
    plt.show()

def test_valueForTimestamp(pv):
    
    i = 15024
    timestepvalue = pv.valueForTimestamp(timestamp = i)
    print("\nvalueForTimestamp:\n", timestepvalue)
    
test_prepareTimeSeries(pv, weather_data)
test_valueForTimestamp(pv)