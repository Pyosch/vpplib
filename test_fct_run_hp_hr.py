# -*- coding: utf-8 -*-
"""
Created on Sun May 10 12:23:05 2020

@author: andre
test fct_run_hp_hr
"""

from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.heat_pump import HeatPump
from vpplib.heating_rod import HeatingRod
from fct_optimize_bivalent import optimize_bivalent
from fct_run_hp_hr import run_hp_hr
from fct_determin_heating_ratio import determin_heating_ratio
import matplotlib.pyplot as plt
import pandas as pd

#Values for environment
start = '2015-01-01 00:00:00'
end = '2015-12-31 23:45:00'
year = '2015'
time_freq = "15 min"
timestamp_int1 = 48
timestamp_int2 = 500
timestamp_str1 = '2015-01-01 12:00:00'
timestamp_str2 = '2015-01-10 06:00:00'
timebase = 15

#Values for user_profile
thermal_energy_demand_yearly = 10000
building_type = 'DE_HEF33'
t_0 = 40

#Values for Heatpump
#el_power = 5 #kW electric
ramp_up_time = 1 / 15 #timesteps
ramp_down_time = 1 / 15 #timesteps
min_runtime = 1 #timesteps
min_stop_time = 2 #timesteps
heat_pump_type = "Air" #nur "Ground" oder "Air"!


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


hp = HeatPump(identifier='hp',
              environment=environment, user_profile=user_profile,
              #el_power=el_power,
              ramp_up_time=ramp_up_time,
              ramp_down_time=ramp_down_time, heat_pump_type = heat_pump_type,
              min_runtime=min_runtime,
              min_stop_time=min_stop_time)

hr = HeatingRod(identifier='hr1', 
                 environment=environment, user_profile = user_profile,
                 #el_power = el_power,
                 rampUpTime = ramp_up_time, 
                 rampDownTime = ramp_down_time, 
                 min_runtime = min_runtime, 
                 min_stop_time = min_stop_time)

# parameters for running hp and hr
norm_temp = -14.0    # biv_temp = -3.0
mode = "parallel"

# layout hr and hp
optimize_bivalent(hp, hr, mode, norm_temp, user_profile)

# show results of layout
print("thermal power hp: " + str(hp.th_power) + "[kW]")
print("electrical power hr: " + str(hr.el_power) + "[kW]")

data = run_hp_hr(hp, hr, mode, user_profile, norm_temp)
ratio = determin_heating_ratio(data)
print("share of heating rod: " + (str(ratio * 100)) + " %")

#i_data = pd.concat([data.th_output_hp, data.thermal_energy_demand], axis = 1)

print(str(data))
data[:].plot(figsize = (16, 9))
plt.show()

data.to_csv("./input/pv/HP_air_HR_eff1_alternative.csv")