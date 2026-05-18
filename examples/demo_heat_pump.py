# -*- coding: utf-8 -*-
"""
Info
----
In this testfile the basic functionalities of the HeatPump class are tested.
Run each time you make changes on an existing function.
Adjust if a new function is added or
parameters in an existing function are changed.

"""

from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.heat_pump import HeatPump
import matplotlib.pyplot as plt
import datetime

# Values for environment
start = "2015-01-01 00:00:00"
end = "2015-12-31 23:45:00"
year = "2015"
time_freq = "15 min"
timestamp_int = 48
timestamp_str = "2015-12-07 12:00:00"
timebase = 15
latitude = 50.941357
longitude = 6.958307
# Add CSV file paths for thermal data
temp_days_file = "./input/thermal/dwd_temp_days_2015.csv"
temp_hours_file = "./input/thermal/dwd_temp_hours_2015.csv"

# Values for user_profile
yearly_thermal_energy_demand = 12500
building_type = "DE_HEF33"
t_0 = 40

# Values for Heatpump
el_power = 5  # kW electric
th_power = 8  # kW thermal
heat_pump_type = "Air"
heat_sys_temp = 60
ramp_up_time = 1 / 15  # timesteps
ramp_down_time = 1 / 15  # timesteps
min_runtime = 1  # timesteps
min_stop_time = 2  # timesteps

environment = Environment(
    timebase=timebase, 
    start=start, 
    end=end, 
    year=year, 
    time_freq=time_freq, 
    surpress_output_globally=False
)
# Load mean temperatures from CSVs instead of DWD API
environment.get_mean_temp_hours(file=temp_hours_file)
environment.get_mean_temp_days(file=temp_days_file)

user_profile = UserProfile(
    identifier=None,
    latitude=None,
    longitude=None,
    thermal_energy_demand_yearly=yearly_thermal_energy_demand,
    mean_temp_days=environment.mean_temp_days,
    mean_temp_hours=environment.mean_temp_hours,
    mean_temp_quarter_hours=environment.mean_temp_hours.resample("15 Min").interpolate(),
    building_type=building_type,
    comfort_factor=None,
    t_0=t_0,
)


def test_get_thermal_energy_demand(user_profile):

    user_profile.get_thermal_energy_demand()
    user_profile.thermal_energy_demand.plot()
    plt.show()


test_get_thermal_energy_demand(user_profile)

hp = HeatPump(
    identifier="hp1",
    unit="kW",
    environment=environment,
    thermal_energy_demand=user_profile.thermal_energy_demand,
    el_power=el_power,
    th_power=th_power,
    heat_pump_type=heat_pump_type,
    heat_sys_temp=heat_sys_temp,
    ramp_up_time=ramp_up_time,
    ramp_down_time=ramp_down_time,
    min_runtime=min_runtime,
    min_stop_time=min_stop_time,
)


def test_get_cop(hp):

    print("get_cop:")
    hp.get_cop()
    hp.cop.plot(figsize=(16, 9))
    plt.show()


def test_prepare_timeseries(hp):

    print("prepareTimeseries:")
    hp.prepare_time_series()
    hp.timeseries.plot(figsize=(16, 9))
    plt.show()


def test_value_for_timestamp(hp, timestamp):

    print("value_for_timestamp:")
    demand = hp.value_for_timestamp(timestamp)
    print("El. Demand: ", demand, "\n")


def test_observations_for_timestamp(hp, timestamp):

    print("observations_for_timestamp:")
    observation = hp.observations_for_timestamp(timestamp)
    print(observation, "\n")


test_get_cop(hp)
test_prepare_timeseries(hp)

test_value_for_timestamp(hp, timestamp_int)
test_observations_for_timestamp(hp, timestamp_int)

test_value_for_timestamp(hp, timestamp_str)
test_observations_for_timestamp(hp, timestamp_str)


"""MOSMIX
Using dwd mosmix (weather forecast) database for temperature data.
The forecast is queried for the next 10 days automatically.
"""
print("\n" + "="*60)
print("MOSMIX Heat Pump Test")
print("="*60)

time_now = Environment().get_time_from_dwd()
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
    latitude=latitude,
    longitude=longitude,
    thermal_energy_demand_yearly=yearly_thermal_energy_demand,
    mean_temp_days=mosmix_environment.mean_temp_days,
    mean_temp_hours=mosmix_environment.mean_temp_hours,
    mean_temp_quarter_hours=mosmix_environment.mean_temp_quarter_hours,
    building_type=building_type,
    comfort_factor=None,
    t_0=t_0,
    consumerfactor=user_profile.consumerfactor,
)
mosmix_user_profile.get_thermal_energy_demand()

mosmix_hp = HeatPump(
    identifier="hp1_mosmix",
    unit="kW",
    environment=mosmix_environment,
    thermal_energy_demand=mosmix_user_profile.thermal_energy_demand,
    el_power=el_power,
    th_power=th_power,
    heat_pump_type=heat_pump_type,
    heat_sys_temp=heat_sys_temp,
    ramp_up_time=ramp_up_time,
    ramp_down_time=ramp_down_time,
    min_runtime=min_runtime,
    min_stop_time=min_stop_time,
)
test_get_cop(mosmix_hp)
test_prepare_timeseries(mosmix_hp)
test_value_for_timestamp(mosmix_hp, 48)
test_observations_for_timestamp(mosmix_hp, 48)
