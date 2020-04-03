# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 12:20:07 2020

@author: sbirk
"""

from vpplib.environment import Environment
from vpplib.user_profile import UserProfile
from vpplib.photovoltaic import Photovoltaic

# Values for environment
start = "2015-07-01 00:00:00"
end = "2015-07-31 23:45:00"
year = "2015"
time_freq = "15 min"
timebase = 15

# Values for user profile
identifier = "bus_1"
latitude = 50.941357
longitude = 6.958307

environment = Environment(
    timebase=timebase,
    timezone="Europe/Berlin",
    start=start,
    end=end,
    year=year,
    time_freq=time_freq,
)

environment.get_pv_data()

user_profile = UserProfile(
    identifier=identifier,
    latitude=latitude,
    longitude=longitude,
    thermal_energy_demand_yearly=None,
    building_type=None,
    comfort_factor=None,
    t_0=None,
    daily_vehicle_usage=None,
    week_trip_start=[],
    week_trip_end=[],
    weekend_trip_start=[],
    weekend_trip_end=[],
)

pv = Photovoltaic(module_lib="SandiaMod",
                  inverter_lib="SandiaInverter",
                  surface_tilt = 20,
                  surface_azimuth = 200,
                  unit="kW",
                  identifier=None,
                  environment=environment,
                  user_profile=user_profile,
                  cost=None)

(modules_per_string,
 strings_per_inverter,
 module, inverter) = pv.pick_pvsystem(
     min_module_power = 220,
     max_module_power = 240,
     pv_power = 8000,
     inverter_power_range = 100)

pv.prepare_time_series()

print("PV module: ")
print(pv.peak_power)
print("PV inverter: ")
print(pv.inverter)
print("PV peak power: ", pv.peak_power)
print("Area of PV modules: ", pv.modules_area)
pv.timeseries.plot(figsize=(16,9))