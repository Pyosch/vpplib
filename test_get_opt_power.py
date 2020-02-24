# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 17:51:01 2020

@author: andre

testing fct_get_opt_power
"""

from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.heat_pump import HeatPump
from vpplib.heating_rod import HeatingRod
import matplotlib.pyplot as plt
import fct_get_opt_power as gop

#Values for environment
start = '2015-01-01 00:00:00'
end = '2015-01-14 23:45:00'
year = '2015'
time_freq = "15 min"
timestamp_int = 48
timestamp_str = '2015-01-01 12:00:00'
timebase = 15

#Values for user_profile
thermal_energy_demand_yearly = 25000
building_type = 'DE_HEF33'
t_0 = 40

#Values for Heatpump
el_power = 5 #kW electric
ramp_up_time = 1 / 15 #timesteps
ramp_down_time = 1 / 15 #timesteps
min_runtime = 1 #timesteps
min_stop_time = 2 #timesteps

environment = Environment(timebase=timebase, start=start, end=end, year=year,
                          time_freq=time_freq)

user_profile = UserProfile(identifier=None,
                           latitude=None,
                           longitude=None,
                           thermal_energy_demand_yearly=thermal_energy_demand_yearly,
                           building_type=building_type,
                           comfort_factor=None,
                           t_0=t_0)


def test_get_thermal_energy_demand(user_profile):
    
    user_profile.get_thermal_energy_demand()
    user_profile.thermal_energy_demand.plot()
    plt.show()


test_get_thermal_energy_demand(user_profile)

hp = HeatPump(identifier='hp1',
              environment=environment, user_profile=user_profile,
              el_power=el_power, ramp_up_time=ramp_up_time,
              ramp_down_time=ramp_down_time,
              min_runtime=min_runtime,
              min_stop_time=min_stop_time)

hr = HeatingRod(identifier='hr1', 
                 environment=environment, user_profile = user_profile,
                 el_power = el_power, rampUpTime = rampUpTime, 
                 rampDownTime = rampDownTime, 
                 min_runtime = min_runtime, 
                 min_stop_time = min_stop_time)

gop.get_opt_power(1000, user_profile, environment, hp, hr)