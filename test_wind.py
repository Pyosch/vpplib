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

from model.VPPWind import VPPWind

import logging
logging.getLogger().setLevel(logging.DEBUG)


start = '2010-01-01 00:00:00'
end = '2010-12-31 23:45:00'
timezone = 'Europe/Berlin'
timestamp_int = 12
timestamp_str = '2010-06-01 12:00:00'

weather_filename = "./Input_House/Wind/weather.csv"

#WindTurbine data
turbine_type = 'E-126/4200'
hub_height = 135
rotor_diameter = 127
fetch_curve = 'power_curve'
data_source = 'oedb'

#ModelChain data
wind_speed_model = 'logarithmic'
density_model = 'ideal_gas'
temperature_model = 'linear_gradient'
power_output_model = 'power_curve'
density_correction = True
obstacle_height = 0
hellman_exp = None

wind = VPPWind(timebase = 1, identifier = None, 
                 environment = None, userProfile = None,
                 start = start, end = end, timezone = timezone,
                 weather_filename = weather_filename,
                 turbine_type = turbine_type, hub_height = hub_height,
                 rotor_diameter = rotor_diameter, fetch_curve = fetch_curve,
                 data_source = data_source,
                 wind_speed_model = wind_speed_model, density_model = density_model,
                 temperature_model = temperature_model, 
                 power_output_model = power_output_model, 
                 density_correction = density_correction,
                 obstacle_height = obstacle_height, hellman_exp = hellman_exp
                 )

def test_prepareTimeSeries(wind, weather_filename):
    
    wind.prepareTimeSeries(weather_filename)
    print("prepareTimeSeries:")
    print(wind.timeseries.head())
    wind.timeseries.plot(figsize=(16,9))
    plt.show()

def test_valueForTimestamp(wind, timestamp):
    
    timestepvalue = wind.valueForTimestamp(timestamp)
    print("\nvalueForTimestamp:\n", timestepvalue)
    
def observationsForTimestamp(wind, timestamp):
    
    print('observationsForTimestamp:')
    observation = wind.observationsForTimestamp(timestamp)
    print(observation, '\n')
    
    
test_prepareTimeSeries(wind, weather_filename)
test_valueForTimestamp(wind, timestamp_int)
test_valueForTimestamp(wind, timestamp_str)

observationsForTimestamp(wind, timestamp_int)
observationsForTimestamp(wind, timestamp_str)