"""
Created on Tue Jul  2 10:38:17 2019

@author: Sascha Birk
"""

import pandas as pd
import pandapower as pp
import pandapower.networks as pn
import os
import sys

sys.path.append(os.path.abspath(os.path.join('')))
from environment import Environment


# environment
start = "2015-03-01 00:00:00"
end = "2015-03-03 23:45:00"
timezone = "Europe/Berlin"
year = "2015"
time_freq = "15 min"
timebase = 15
force_end_time = False


# user_profile
latitude = 50.941357
longitude = 6.958307
radius_weather_station=20

environment = Environment(
    timebase=timebase,
    timezone=timezone,
    start=start,
    end=end,
    year=year,
    time_freq=time_freq,
    force_end_time=force_end_time,
)

environment.get_dwd_pv_data(lat=latitude,lon=longitude)

print(environment.pv_data)





