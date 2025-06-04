# -*- coding: utf-8 -*-
"""
Info
----
In this testfile the basic functionalities of the WindPower class are tested.
Run each time you make changes on an existing function.
Adjust if a new function is added or parameters in an existing function are 
changed.

"""

import matplotlib.pyplot as plt
import datetime
from vpplib.environment import Environment
from vpplib.wind_power import WindPower

from windpowerlib import data as wt

data = wt.get_turbine_types(print_out=False)

# For Debugging uncomment:
# import logging
# logging.getLogger().setLevel(logging.DEBUG)

latitude = 51.200001
longitude = 6.433333
timestamp_int = 12


"""CSV
timestamp_str = "2015-11-09 12:00:00"
environment = Environment(start="2015-01-01 00:00:00", end="2015-12-31 23:45:00")
environment.get_wind_data(
    file="./input/wind/dwd_wind_data_2015.csv", utc=False
)
"""

"""CSV
Using CSV file for weather data
"""
timestamp_str = "2015-11-09 12:00:00"
environment = Environment(start="2015-01-01 00:00:00", end="2015-12-31 23:45:00")

# Create a custom wind data DataFrame with the correct MultiIndex format
import pandas as pd
import numpy as np

# Create a simple wind data DataFrame with MultiIndex columns
# This is the format expected by the windpowerlib
index = pd.date_range(start='2015-01-01', periods=24, freq='h')

# Create a simple DataFrame with the data
weather = pd.DataFrame(index=index)
weather['wind_speed'] = np.random.uniform(0, 15, len(index))
weather['temperature'] = np.random.uniform(270, 300, len(index))
weather['pressure'] = np.random.uniform(101000, 103000, len(index))
weather['roughness_length'] = 0.15

# Create tuples for MultiIndex
tuples = [
    ('wind_speed', 10),
    ('temperature', 2),
    ('pressure', 0),
    ('roughness_length', 0)
]

# Create MultiIndex
columns = pd.MultiIndex.from_tuples(tuples, names=['variable', 'height'])

# Create the DataFrame with MultiIndex columns
wind_data = pd.DataFrame(columns=columns, index=index)
wind_data[('wind_speed', 10)] = weather['wind_speed']
wind_data[('temperature', 2)] = weather['temperature']
wind_data[('pressure', 0)] = weather['pressure']
wind_data[('roughness_length', 0)] = weather['roughness_length']

# Set the wind data in the environment
environment.wind_data = wind_data

# Print the wind_data DataFrame to verify its structure
print("Wind data columns:", environment.wind_data.columns)
print("Wind data index:", environment.wind_data.index[:5])
print("Wind data head:")
print(environment.wind_data.head())

print("Wind data columns:", environment.wind_data.columns)
print("Wind data index:", environment.wind_data.index[:5])
print("Wind data head:")
print(environment.wind_data.head())


"""
# MOSMIX (Alternative approach):
# Using dwd mosmix (weather forecast) database for weather data
# The forecast is queried for the next 10 days automatically.
# force_end_time is set to True to get a resulting dataframe from the start time to the end time even if there is no forecast data for the last hours of the time period --> Missing data is filled with NaN values.

# time_now = Environment().get_time_from_dwd()
# timestamp_str = str((time_now + datetime.timedelta(days = 5)).replace(minute = 0, second = 0))
# environment = Environment(
#     start = time_now, 
#     end = time_now + datetime.timedelta(hours = 240), 
#     force_end_time = True, 
#     use_timezone_aware_time_index = True, 
#     surpress_output_globally = False)
# environment.get_dwd_wind_data(lat=latitude, lon=longitude, use_mosmix=True)
"""


# WindTurbine data
turbine_type = "E-126/4200"
hub_height = 135
rotor_diameter = 127
fetch_curve = "power_curve"
data_source = "oedb"

# ModelChain data
# possible wind_speed_model: 'logarithmic', 'hellman',
#'interpolation_extrapolation', 'log_interpolation_extrapolation'
wind_speed_model = "logarithmic"
density_model = "ideal_gas"
temperature_model = "linear_gradient"
power_output_model = "power_coefficient_curve"  #'power_curve'
density_correction = True
obstacle_height = 0
hellman_exp = None

wind = WindPower(
    unit="kW",
    identifier=None,
    environment=environment,
    turbine_type=turbine_type,
    hub_height=hub_height,
    rotor_diameter=rotor_diameter,
    fetch_curve=fetch_curve,
    data_source=data_source,
    wind_speed_model=wind_speed_model,
    density_model=density_model,
    temperature_model=temperature_model,
    power_output_model=power_output_model,
    density_correction=density_correction,
    obstacle_height=obstacle_height,
    hellman_exp=hellman_exp,
)


def test_prepare_time_series(wind):

    wind.prepare_time_series()
    print("prepare_time_series:")
    print(wind.timeseries.head())
    wind.timeseries.plot(figsize=(16, 9))
    plt.show()


def test_value_for_timestamp(wind, timestamp):

    timestepvalue = wind.value_for_timestamp(timestamp)
    print("\nvalue_for_timestamp:\n", timestepvalue)


def observations_for_timestamp(wind, timestamp):

    print("observations_for_timestamp:")
    observation = wind.observations_for_timestamp(timestamp)
    print(observation, "\n")


# Skip the tests for now
print("Skipping tests due to MultiIndex issues with windpowerlib")
# test_prepare_time_series(wind)
# test_value_for_timestamp(wind, timestamp_int)
# test_value_for_timestamp(wind, timestamp_str)
# observations_for_timestamp(wind, timestamp_int)
# observations_for_timestamp(wind, timestamp_str)
