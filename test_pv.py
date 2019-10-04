# -*- coding: utf-8 -*-
"""
Info
----
In this testfile the basic functionalities of the VPPPhotovoltaic class are tested.
Run each time you make changes on an existing function.
Adjust if a new function is added or 
parameters in an existing function are changed.

"""

import matplotlib.pyplot as plt

from model.VPPEnvironment import VPPEnvironment
from model.VPPUserProfile import VPPUserProfile
from model.VPPPhotovoltaic import VPPPhotovoltaic


latitude = 50.941357
longitude = 6.958307
identifier = 'Cologne'
start = '2017-01-01 00:00:00'
end = '2017-12-31 23:45:00'
timestamp_int = 48
timestamp_str = '2017-01-01 12:00:00'

environment = VPPEnvironment(start=start, end=end)
environment.get_irradiation_data()

user_profile = VPPUserProfile(identifier=identifier, latitude=latitude,
                              longitude=longitude)

pv = VPPPhotovoltaic(unit="kW", identifier=identifier, environment = environment, 
                     user_profile = user_profile,
                     module_lib = 'SandiaMod', 
                     module = 'Canadian_Solar_CS5P_220M___2009_', 
                     inverter_lib = 'cecinverter', 
                     inverter = 'ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_',
                     surface_tilt = 20, surface_azimuth = 200,
                     modules_per_string = 2, strings_per_inverter = 2)

def test_prepareTimeSeries(pv):
    
    pv.prepareTimeSeries()
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
    
    
test_prepareTimeSeries(pv)
test_valueForTimestamp(pv, timestamp_int)
test_valueForTimestamp(pv, timestamp_str)

observationsForTimestamp(pv, timestamp_int)
observationsForTimestamp(pv, timestamp_str)