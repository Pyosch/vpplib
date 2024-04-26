# -*- coding: utf-8 -*-
"""
Info
----
In this testfile the basic functionalities of the Photovoltaic class are tested.
Run each time you make changes on an existing function.
Adjust if a new function is added or
parameters in an existing function are changed.

"""

import matplotlib.pyplot as plt

from vpplib.environment import Environment
from vpplib.user_profile import UserProfile
from vpplib.photovoltaic import Photovoltaic
import datetime # for Mosmix test

latitude = 51.4
longitude = 6.97
identifier = "Cologne"
timestamp_int = 48

"""
Read weather data vom .csv file:

timestamp_str = "2015-11-09 12:00:00"
environment = Environment(start="2015-01-01 00:00:00", end="2015-12-31 23:45:00")
environment.get_pv_data(file="./input/pv/dwd_pv_data_2015.csv")
"""

"""
Using dwd observation (weather recording) database for weather data
use_timezone_aware_time_index has to be set to True because there is a timezone shift within the queried time period. Otherwise the dataframe's time index would be non monotonic.
"""
timestamp_str = "2015-11-09 12:00:00"
environment = Environment(
    start = "2015-01-01 00:00:00", 
    end = "2015-12-31 23:45:00", 
    use_timezone_aware_time_index = True, 
    surpress_output_globally = False)
environment.get_dwd_pv_data(lat=latitude, lon=longitude)



"""
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
environment.get_dwd_pv_data(lat=latitude, lon=longitude, min_quality_per_parameter=10)
"""


user_profile = UserProfile(
    identifier=identifier, latitude=latitude, longitude=longitude
)

pv = Photovoltaic(
    unit="kW",
    identifier=identifier,
    environment=environment,
    user_profile=user_profile,
    module_lib="SandiaMod",
    module="Canadian_Solar_CS5P_220M___2009_",
    inverter_lib="cecinverter",
    inverter="ABB__MICRO_0_25_I_OUTD_US_208__208V_",
    surface_tilt=20,
    surface_azimuth=200,
    modules_per_string=2,
    strings_per_inverter=2,
    temp_lib='sapm',
    temp_model='open_rack_glass_glass'
)


def test_prepare_time_series(pv):

    pv.prepare_time_series()
    print("prepare_time_series:")
    print(pv.timeseries.head())
    pv.timeseries.plot(figsize=(16, 9))
    plt.show()


def test_value_for_timestamp(pv, timestamp):

    timestepvalue = pv.value_for_timestamp(timestamp)
    print("\nvalue_for_timestamp:\n", timestepvalue)


def observations_for_timestamp(pv, timestamp):

    print("observations_for_timestamp:")
    observation = pv.observations_for_timestamp(timestamp)
    print(observation, "\n")


test_prepare_time_series(pv)
test_value_for_timestamp(pv, timestamp_int)
test_value_for_timestamp(pv, timestamp_str)

observations_for_timestamp(pv, timestamp_int)
observations_for_timestamp(pv, timestamp_str)
