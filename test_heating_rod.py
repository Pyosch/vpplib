# -*- coding: utf-8 -*-
"""
Info
----
In this testfile the basic functionalities of the VPPHeatingRod class are tested.
Run each time you make changes on an existing function.
Adjust if a new function is added or 
parameters in an existing function are changed.

"""

from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.heating_rod import HeatingRod
import matplotlib.pyplot as plt

#Values for environment
start = '2015-01-01 00:00:00'
end = '2015-12-31 23:45:00'
year = '2015'
time_freq = "15 min"
timestamp_int = 48
timestamp_str = '2015-01-01 12:00:00'
timebase = 15

#Values for user_profile
thermal_energy_demand_yearly= 10000
building_type = 'DE_HEF33'
t_0 = 40

#Values for HeatingRod
el_power = 3 #kW electric
rampUpTime = 1/15 #timesteps
rampDownTime = 1/15 #timesteps
min_runtime = 1 #timesteps
min_stop_time = 2 #timesteps

environment = Environment(timebase=timebase, start=start, end=end, year=year,
                             time_freq=time_freq)

user_profile = UserProfile(identifier=None,
                                 latitude = None,
                                 longitude = None,
                                 thermal_energy_demand_yearly = thermal_energy_demand_yearly,
                                 building_type = building_type,
                                 comfort_factor = None,
                                 t_0=t_0)

def test_get_thermal_energy_demand(user_profile):
    
    user_profile.get_thermal_energy_demand()
    user_profile.thermal_energy_demand.plot()
    plt.show()
    
test_get_thermal_energy_demand(user_profile)

hr = HeatingRod(identifier='hp1', 
                 environment=environment, user_profile = user_profile,
                 el_power = el_power, rampUpTime = rampUpTime, 
                 rampDownTime = rampDownTime, 
                 min_runtime = min_runtime, 
                 min_stop_time = min_stop_time)
  
    
def test_prepareTimeseries(hr):
    
    print('prepareTimeseries:')
    hr.prepareTimeSeries()
    hr.timeseries.plot(figsize=(16,9))
    plt.show()
    
def test_valueForTimestamp(hr, timestamp):
    
    print('valueForTimestamp:')
    demand= hr.value_for_timestamp(timestamp)
    print("El. Demand: ",demand, '\n')
    
def test_observationsForTimestamp(hr, timestamp):
    
    print('observationsForTimestamp:')
    observation = hr.observations_for_timestamp(timestamp)
    print(observation, '\n')
  
test_prepareTimeseries(hr)  

test_valueForTimestamp(hr, timestamp_int)
test_observationsForTimestamp(hr, timestamp_int)

test_valueForTimestamp(hr, timestamp_str)
test_observationsForTimestamp(hr, timestamp_str)

sum_el_dem = hr.timeseries["el_demand"].sum() * 0.25
print("electrical demand hr: " + str(sum_el_dem) + " [kWh]")

hr.timeseries.to_csv("./input/pv/HR_eff1.csv")
