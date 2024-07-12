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
#timezone = "Europe/Berlin"
timestamp_int = 12


"""CSV
timestamp_str = "2015-11-09 12:00:00"
environment = Environment(start="2015-01-01 00:00:00", end="2015-12-31 23:45:00")
environment.get_wind_data(
    file="./input/wind/dwd_wind_data_2015.csv", utc=False
)
"""

"""OBSERVATION 
Using dwd observation (weather recording) database for weather data
use_timezone_aware_time_index has to be set to True because there is a timezone shift within the queried time period. Otherwise the dataframe's time index would be non monotonic.
"""
timestamp_str = "2015-01-09 12:00:00"
environment = Environment(
    start = "2015-01-01 00:00:00", 
    end = "2015-12-31 23:45:00", 
    use_timezone_aware_time_index = True, 
    surpress_output_globally = False)
environment.get_dwd_wind_data(lat=latitude, lon=longitude)


"""MOSMIX:
Using dwd mosmix (weather forecast) database for weather data
The forecast is queried for the next 10 days automatically.
force_end_time is set to True to get a resulting dataframe from the start time to the end time even if there is no forecast data for the last hours of the time period --> Missing data is filled with NaN values.

time_now = Environment().get_time_from_dwd()
timestamp_str = str((time_now + datetime.timedelta(days = 5)).replace(minute = 0, second = 0))
environment = Environment(
    start = time_now, 
    end = time_now + datetime.timedelta(hours = 240), 
    force_end_time = True, 
    use_timezone_aware_time_index = True, 
    surpress_output_globally = False)
environment.get_dwd_wind_data(lat=latitude, lon=longitude)
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
    user_profile=None,
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


test_prepare_time_series(wind)
test_value_for_timestamp(wind, timestamp_int)
test_value_for_timestamp(wind, timestamp_str)

observations_for_timestamp(wind, timestamp_int)
observations_for_timestamp(wind, timestamp_str)
