# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 15:33:53 2019

@author: patri, pyosch
"""
import matplotlib.pyplot as plt
from tqdm import tqdm
import datetime

from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.thermal_energy_storage import ThermalEnergyStorage
from vpplib.heat_pump import HeatPump

figsize = (10, 6)

# Reference period: yesterday going back one year
yesterday = datetime.date.today() - datetime.timedelta(days=1)
ref_start = yesterday.replace(year=yesterday.year - 1)
ref_end = yesterday

# Location
latitude = 51.200001
longitude = 6.433333

# Values for environment — January of the most recent year in the reference period
start = f"{ref_end.year}-01-01 00:00:00"
end = f"{ref_end.year}-01-31 23:45:00"
time_freq = "15 min"
timebase = 15

# Values for user_profile
yearly_thermal_energy_demand = 12500  # kWh
building_type = "DE_HEF33"
t_0 = 40  # °C

# Values for Thermal Storage
target_temperature = 60  # °C
min_temperature = 40  # °C
hysteresis = 5  # °K
mass_of_storage = 500  # kg
cp = 4.2
thermal_energy_loss_per_day = 0.13

# Values for Heatpump
el_power = 5  # kW electric
th_power = 8  # kW thermal
ramp_up_time = 1 / 15  # timesteps
ramp_down_time = 1 / 15  # timesteps
min_runtime = 1  # timesteps
min_stop_time = 2  # timesteps
heat_pump_type = "Air"
heat_sys_temp = 60

# ---------------------------------------------------------------------------
# Fetch one full reference year of DWD observation data for the location.
# This drives the consumerfactor calibration that the MOSMIX section reuses.
# ---------------------------------------------------------------------------
print(f"Fetching DWD observation data {ref_start} to {ref_end} at ({latitude}, {longitude}) ...")
ref_environment = Environment(
    timebase=60,
    start=f"{ref_start} 00:00:00",
    end=f"{ref_end} 23:00:00",
    time_freq="60 min",
    surpress_output_globally=True,
)
ref_environment.get_dwd_mean_temp_hours(lat=latitude, lon=longitude, min_quality_per_parameter=10)
ref_environment.get_dwd_mean_temp_days(lat=latitude, lon=longitude, min_quality_per_parameter=10)
ref_environment.mean_temp_quarter_hours = ref_environment.mean_temp_hours.resample("15 Min").interpolate()

user_profile = UserProfile(
    identifier=None,
    latitude=latitude,
    longitude=longitude,
    thermal_energy_demand_yearly=yearly_thermal_energy_demand,
    mean_temp_days=ref_environment.mean_temp_days,
    mean_temp_hours=ref_environment.mean_temp_hours,
    mean_temp_quarter_hours=ref_environment.mean_temp_quarter_hours,
    building_type=building_type,
    comfort_factor=None,
    t_0=t_0,
)


def test_get_thermal_energy_demand(user_profile):

    user_profile.get_thermal_energy_demand()
    user_profile.thermal_energy_demand.plot()
    plt.show()


test_get_thermal_energy_demand(user_profile)
print(f"Location-calibrated consumerfactor: {user_profile.consumerfactor:.4f}")

# January simulation environment — fetch temperature data for the simulation window
environment = Environment(
    timebase=timebase,
    start=start,
    end=end,
    time_freq=time_freq,
    surpress_output_globally=False
)
environment.get_dwd_mean_temp_hours(lat=latitude, lon=longitude, min_quality_per_parameter=10)
environment.get_dwd_mean_temp_days(lat=latitude, lon=longitude, min_quality_per_parameter=10)
environment.mean_temp_quarter_hours = environment.mean_temp_hours.resample("15 Min").interpolate()

tes = ThermalEnergyStorage(
    environment=environment,
    unit="kWh",
    cp=cp,
    mass=mass_of_storage,
    hysteresis=hysteresis,
    target_temperature=target_temperature,
    min_temperature=min_temperature,
    thermal_energy_loss_per_day=thermal_energy_loss_per_day,
)

hp = HeatPump(
    identifier="hp1",
    unit="kW",
    environment=environment,
    thermal_energy_demand=user_profile.thermal_energy_demand,
    el_power=el_power,
    th_power=th_power,
    ramp_up_time=ramp_up_time,
    ramp_down_time=ramp_down_time,
    min_runtime=min_runtime,
    min_stop_time=min_stop_time,
    heat_pump_type=heat_pump_type,
    heat_sys_temp=heat_sys_temp,
)


for i in tqdm(hp.timeseries.index):
    tes.operate_storage(i, hp)


tes.timeseries.plot(figsize=figsize, title="Temperature of Storage")
plt.show()
tes.timeseries.iloc[0:960].plot(
    figsize=figsize, title="Temperature of Storage 10-Day View"
)
plt.show()
tes.timeseries.iloc[0:96].plot(
    figsize=figsize, title="Temperature of Storage Daily View"
)
plt.show()
hp.timeseries.el_demand.plot(figsize=figsize, title="Electrical Loadshape")
plt.show()
hp.timeseries.el_demand.iloc[0:960].plot(
    figsize=figsize, title="Electrical Loadshape 10-Day View"
)
plt.show()
hp.timeseries.el_demand.iloc[0:96].plot(
    figsize=figsize, title="Electrical Loadshape Daily View"
)
plt.show()


"""MOSMIX
Using dwd mosmix (weather forecast) database for temperature data.
The forecast is queried for the next 10 days automatically.
"""
print("\n" + "="*60)
print("MOSMIX Thermal Energy Storage Test")
print("="*60)

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

mosmix_tes = ThermalEnergyStorage(
    environment=mosmix_environment,
    unit="kWh",
    cp=cp,
    mass=mass_of_storage,
    hysteresis=hysteresis,
    target_temperature=target_temperature,
    min_temperature=min_temperature,
    thermal_energy_loss_per_day=thermal_energy_loss_per_day,
)

mosmix_hp = HeatPump(
    identifier="hp1_mosmix",
    unit="kW",
    environment=mosmix_environment,
    thermal_energy_demand=mosmix_user_profile.thermal_energy_demand,
    el_power=el_power,
    th_power=th_power,
    ramp_up_time=ramp_up_time,
    ramp_down_time=ramp_down_time,
    min_runtime=min_runtime,
    min_stop_time=min_stop_time,
    heat_pump_type=heat_pump_type,
    heat_sys_temp=heat_sys_temp,
)

try:
    for i in tqdm(mosmix_hp.thermal_energy_demand.index):
        mosmix_tes.operate_storage(i, mosmix_hp)
except ValueError as e:
    print(f"\nStorage simulation stopped early: {e}")
    print("This can happen when component parameters are not tuned for the forecast period.")

mosmix_tes.timeseries.iloc[0:96].plot(
    figsize=figsize, title="MOSMIX Temperature of Storage Daily View"
)
plt.show()
mosmix_hp.timeseries.el_demand.iloc[0:96].plot(
    figsize=figsize, title="MOSMIX Electrical Loadshape Daily View"
)
plt.show()
