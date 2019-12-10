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


latitude = 50.941357
longitude = 6.958307
identifier = "Cologne"
start = "2015-06-01 00:00:00"
end = "2015-06-07 23:45:00"
timestamp_int = 48
timestamp_str = "2015-06-05 12:00:00"

environment = Environment(start=start, end=end)
environment.get_pv_data(file="./input/pv/dwd_pv_data_2015.csv")

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
    inverter="ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_",
    surface_tilt=20,
    surface_azimuth=200,
    modules_per_string=2,
    strings_per_inverter=2,
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
