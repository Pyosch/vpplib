# -*- coding: utf-8 -*-
"""
Created on Sun May 24 12:25:31 2020

@author: andre

test fct_optimize_tes_hp
"""

from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.heat_pump import HeatPump
from vpplib.thermal_energy_storage import ThermalEnergyStorage
from fct_optimize_tes_hp import optimize_tes_hp
import matplotlib.pyplot as plt
import pandas as pd

#Values for environment
start = '2015-01-01 00:00:00'
end = '2015-01-14 23:45:00'
year = '2015'
time_freq = "15 min"
timestamp_int1 = 48
timestamp_int2 = 500
timestamp_str1 = '2015-01-01 12:00:00'
timestamp_str2 = '2015-01-10 06:00:00'
timebase = 15

#Values for user_profile
thermal_energy_demand_yearly = 15000
building_type = 'DE_HEF33'
t_0 = 40

#Values for Heatpump
#el_power = 5 #kW electric
ramp_up_time = 1 / 15 #timesteps
ramp_down_time = 1 / 15 #timesteps
min_runtime = 1 #timesteps
min_stop_time = 2 #timesteps
heat_pump_type = "Ground" #nur "Ground" oder "Air"!

#Values for Thermal Storage
target_temperature = 60  # °C
hysteresis = 5  # °K
#mass_of_storage = 500  # kg


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

tes = ThermalEnergyStorage(environment=environment, user_profile=user_profile,
                           #mass=mass_of_storage,
                           hysteresis=hysteresis,
                           target_temperature=target_temperature)

mode = "overcome shutdown"
#optimize_tes_hp(tes, hp, mode, user_profile)
tes.optimize_tes_hp(hp, mode)

print("mass of thermal storage: " + str(tes.mass) + " [kg]")
print("electrical power hp: " + str(hp.el_power) + " [kW]")
print("thermal power hp: " + str(hp.th_power) + " [kW]")
print("tägliche Verluste: " + str(tes.thermal_energy_loss_per_day) + " [kW]")
