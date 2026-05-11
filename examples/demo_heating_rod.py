# -*- coding: utf-8 -*-
"""
Info
----
In this testfile the basic functionalities of the VPPHeatPump class are tested.
Run each time you make changes on an existing function.
Adjust if a new function is added or
parameters in an existing function are changed.

"""

from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.heating_rod import HeatingRod
import matplotlib.pyplot as plt
import datetime

# Values for environment
start = '2015-01-01 00:00:00'
end = '2015-01-14 23:45:00'
year = '2015'
time_freq = "15 min"
timestamp_int = 48
timestamp_str = '2015-01-01 12:00:00'
timebase = 15

# Values for user_profile
thermal_energy_demand_yearly = 12500
building_type = 'DE_HEF33'
t_0 = 40

# Values for HeatingRod
el_power = 3  # kW electric
rampUpTime = 1/15  # timesteps
rampDownTime = 1/15  # timesteps
min_runtime = 1  # timesteps
min_stop_time = 2  # timesteps

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

hr = HeatingRod(identifier='hp1',
                environment=environment, 
                thermal_energy_demand=user_profile.thermal_energy_demand,
                el_power=el_power, 
                rampUpTime=rampUpTime,
                rampDownTime=rampDownTime,
                min_runtime=min_runtime,
                min_stop_time=min_stop_time)


def test_prepareTimeseries(hr):

    print('prepareTimeseries:')
    hr.prepareTimeSeries()
    hr.timeseries.plot(figsize=(16, 9))
    plt.show()


def test_valueForTimestamp(hr, timestamp):

    print('valueForTimestamp:')
    demand = hr.valueForTimestamp(timestamp)
    print("El. Demand: ", demand, '\n')


def test_observationsForTimestamp(hr, timestamp):

    print('observationsForTimestamp:')
    observation = hr.observationsForTimestamp(timestamp)
    print(observation, '\n')


test_prepareTimeseries(hr)

test_valueForTimestamp(hr, timestamp_int)
test_observationsForTimestamp(hr, timestamp_int)

test_valueForTimestamp(hr, timestamp_str)
test_observationsForTimestamp(hr, timestamp_str)


"""MOSMIX
Using dwd mosmix (weather forecast) database for temperature data.
The forecast is queried for the next 10 days automatically.
"""
print("\n" + "="*60)
print("MOSMIX Heating Rod Test")
print("="*60)

latitude = 50.941357
longitude = 6.958307
time_now = Environment().get_time_from_dwd()
# Round up to next full hour so the 15-min grid aligns with MOSMIX hourly data
mosmix_start = (time_now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
mosmix_environment = Environment(
    timebase=timebase,
    start=mosmix_start,
    end=mosmix_start + datetime.timedelta(hours=239),
    force_end_time=True,
    use_timezone_aware_time_index=True,
    time_freq=time_freq,
    surpress_output_globally=False
)
mosmix_environment.get_dwd_mean_temp_hours(lat=latitude, lon=longitude, min_quality_per_parameter=10)
mosmix_environment.get_dwd_mean_temp_days(lat=latitude, lon=longitude, min_quality_per_parameter=10)
mosmix_environment.mean_temp_quarter_hours = mosmix_environment.mean_temp_hours.resample("15 Min").interpolate()

mosmix_user_profile = UserProfile(
    identifier=None,
    latitude=None,
    longitude=None,
    thermal_energy_demand_yearly=thermal_energy_demand_yearly,
    mean_temp_days=mosmix_environment.mean_temp_days,
    mean_temp_hours=mosmix_environment.mean_temp_hours,
    mean_temp_quarter_hours=mosmix_environment.mean_temp_quarter_hours,
    building_type=building_type,
    comfort_factor=None,
    t_0=t_0,
)
mosmix_user_profile.get_thermal_energy_demand()

mosmix_hr = HeatingRod(
    identifier='hr1_mosmix',
    environment=mosmix_environment,
    thermal_energy_demand=mosmix_user_profile.thermal_energy_demand,
    el_power=el_power,
    rampUpTime=rampUpTime,
    rampDownTime=rampDownTime,
    min_runtime=min_runtime,
    min_stop_time=min_stop_time,
)

test_prepareTimeseries(mosmix_hr)
test_valueForTimestamp(mosmix_hr, 48)
test_observationsForTimestamp(mosmix_hr, 48)
