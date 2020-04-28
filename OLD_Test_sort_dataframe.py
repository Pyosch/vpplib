# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 15:21:01 2019

@author: andre
"""

from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
import matplotlib.pyplot as plt

figsize = (10,6)
#Values for environment
start = '2015-01-01 00:00:00'
end = '2015-12-31 23:45:00'
year = '2015'

#Values for user_profile
thermal_energy_demand_yearly = 100 # kWh
building_type = 'DE_HEF33'
t_0 = 40 # °C

#Values for Thermal Storage
target_temperature = 60 # °C
hysteresis = 5 # °K
mass_of_storage = 500 # kg

#Values for HeatingRod
el_power = 30 #kW electric
rampUpTime = 1/15 #timesteps
rampDownTime = 1/15 #timesteps
min_runtime = 1 #timesteps
min_stop_time = 2 #timesteps
timebase = 15

environment = Environment(timebase=timebase, start=start, end=end, year=year)

user_profile = UserProfile(identifier=None,
                                 latitude = None,
                                 longitude = None,
                                 thermal_energy_demand_yearly=thermal_energy_demand_yearly,
                                 building_type = building_type,
                                 comfort_factor = None,
                                 t_0=t_0)

def test_get_thermal_energy_demand(user_profile):
    
    user_profile.get_thermal_energy_demand()
    user_profile.thermal_energy_demand.plot()
    plt.show()
    
test_get_thermal_energy_demand(user_profile)

data = user_profile.get_thermal_energy_demand()
duration_curve = data.sort_values(by = ["thermal_energy_demand"], ascending = False)
duration_curve_x = range(35040)
duration_curve_y = duration_curve.values

plt.plot(duration_curve_x, duration_curve_y)