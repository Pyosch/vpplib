# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 15:33:53 2019

@author: patri, pyosch
"""
import matplotlib.pyplot as plt
from tqdm import tqdm

from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.thermal_energy_storage import ThermalEnergyStorage
from vpplib.heat_pump import HeatPump

figsize = (10, 6)
# Values for environment
start = "2015-01-01 00:00:00"
end = "2015-01-31 23:45:00"
year = "2015"
time_freq = "15 min"
timebase = 15
latitude = 51.200001
longitude = 6.433333
# Add CSV file paths for thermal data
temp_days_file = "./input/thermal/dwd_temp_days_2015.csv"
temp_hours_file = "./input/thermal/dwd_temp_hours_2015.csv"

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
# Create quarter-hourly temperature data by resampling hourly data
environment.mean_temp_quarter_hours = environment.mean_temp_hours.resample("15 Min").interpolate()

user_profile = UserProfile(
    identifier=None,
    latitude=None,
    longitude=None,
    thermal_energy_demand_yearly=yearly_thermal_energy_demand,
    mean_temp_days=environment.mean_temp_days,
    mean_temp_hours=environment.mean_temp_hours,
    mean_temp_quarter_hours=environment.mean_temp_quarter_hours,
    building_type=building_type,
    comfort_factor=None,
    t_0=t_0,
)


def test_get_thermal_energy_demand(user_profile):

    user_profile.get_thermal_energy_demand()
    user_profile.thermal_energy_demand.plot()
    plt.show()


test_get_thermal_energy_demand(user_profile)

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
    thermal_energy_demand = user_profile.thermal_energy_demand,
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
