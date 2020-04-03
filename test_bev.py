# -*- coding: utf-8 -*-
"""
Info
----
In this testfile the basic functionalities of the BatteryElectricVehicle class
are tested.
Run each time you make changes on an existing function.
Adjust if a new function is added or
parameters in an existing function are changed.

"""
from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.battery_electric_vehicle import BatteryElectricVehicle
import matplotlib.pyplot as plt

identifier = "bev_1"
start = "2015-06-01 00:00:00"
end = "2015-06-01 23:45:00"
timebase = 15
timestamp_int = 48
timestamp_str = "2015-06-01 12:00:00"

charging_power = 11
battery_max = 16
battery_min = 0
battery_usage = 1
charge_efficiency = 0.98
load_degradiation_begin = 0.8

environment = Environment(start=start, end=end, timebase=timebase)

user_profile = UserProfile(identifier=identifier)


bev = BatteryElectricVehicle(
    unit="kW",
    identifier=None,
    environment=environment,
    user_profile=user_profile,
    battery_max=battery_max,
    battery_min=battery_min,
    battery_usage=battery_usage,
    charging_power=charging_power,
    load_degradation_begin=load_degradiation_begin,
    charge_efficiency=charge_efficiency,
)


def test_prepare_time_series(bev):

    bev.prepare_time_series()
    print("prepare_time_series:")
    print(bev.timeseries.head())
    bev.timeseries.plot(figsize=(16, 9))
    plt.show()


def test_value_for_timestamp(bev, timestamp):

    timestepvalue = bev.value_for_timestamp(timestamp)
    print("\nvalue_for_timestamp:\n", timestepvalue)


def test_observations_for_timestamp(bev, timestamp):

    print("observations_for_timestamp:")
    observation = bev.observations_for_timestamp(timestamp)
    print(observation, "\n")


test_prepare_time_series(bev)
test_value_for_timestamp(bev, timestamp_int)
test_value_for_timestamp(bev, timestamp_str)

test_observations_for_timestamp(bev, timestamp_int)
test_observations_for_timestamp(bev, timestamp_str)
