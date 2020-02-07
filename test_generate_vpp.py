# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 15:35:09 2020

@author: sbirk
"""

import pandas as pd
import random

from vpplib import VirtualPowerPlant, Operator, UserProfile, Environment
from vpplib import Photovoltaic, WindPower, BatteryElectricVehicle
from vpplib import HeatPump, ThermalEnergyStorage, ElectricalEnergyStorage
from vpplib import CombinedHeatAndPower

bus_number = 20

pv_number = 20
wind_number = 2
bev_number = 20
hp_number = 20  # always includes thermal energy storage
ees_number = 20
chp_number = 20  # always includes thermal energy storage


# Values for environment
start = "2015-07-01 00:00:00"
end = "2015-07-31 23:45:00"
year = "2015"
time_freq = "15 min"
index_year = pd.date_range(
    start=year, periods=35040, freq=time_freq, name="time"
)
index_hours = pd.date_range(start=start, end=end, freq="h", name="time")
timebase = 15  # for calculations from kW to kWh

# Values for user profile
identifier = "bus"
latitude = 50.941357
longitude = 6.958307
target_temperature = 60  # °C
t_0 = 40  # °C
yearly_thermal_energy_demand = None  # kWh thermal; redifined in line 119

# Values for pv
module_lib = "SandiaMod"
module = "Canadian_Solar_CS5P_220M___2009_"
inverter_lib = "cecinverter"
inverter = "ABB__PVI_4_2_OUTD_S_US_Z_M_A__208_V__208V__CEC_2014_"
surface_tilt = 20
surface_azimuth = 200
modules_per_string = 10
strings_per_inverter = 2

# WindTurbine data
turbine_type = "E-126/4200"
hub_height = 135
rotor_diameter = 127
fetch_curve = "power_curve"
data_source = "oedb"

# Wind ModelChain data
# possible wind_speed_model: 'logarithmic', 'hellman',
# 'interpolation_extrapolation', 'log_interpolation_extrapolation'
wind_speed_model = "logarithmic"
density_model = "ideal_gas"
temperature_model = "linear_gradient"
power_output_model = "power_coefficient_curve"  # alt.: 'power_curve'
density_correction = True
obstacle_height = 0
hellman_exp = None

# Values for el storage
charge_efficiency = 0.98
discharge_efficiency = 0.98
max_power = 4  # kW
capacity = 4  # kWh
max_c = 1  # factor between 0.5 and 1.2

# Values for bev
battery_max = 16
battery_min = 4
battery_usage = 1
charging_power = 11
bev_charge_efficiency = 0.98
load_degradation_begin = 0.8

# Values for heat pump
heat_pump_type = "Air"
heat_sys_temp = 60
el_power_hp = 5
th_power_hp = None
building_type = "DE_HEF33"
ramp_up_time_hp = 1 / 15  # timesteps
ramp_down_time_hp = 1 / 15  # timesteps
min_runtime_hp = 1  # timesteps
min_stop_time_hp = 2  # timesteps

# Values for Thermal Storage
hysteresis = 5  # °K
mass_of_storage = 500  # kg
cp = 4.2
thermal_energy_loss_per_day = 0.13

# Values for chp
el_power_chp = 6  # kW
th_power_chp = 10  # kW
overall_efficiency = 0.8
ramp_up_time = 1 / 15  # timesteps
ramp_down_time = 1 / 15  # timesteps
min_runtime_chp = 1  # timesteps
min_stop_time_chp = 2  # timesteps

# %% export

# dataframes for exporting timeseries and component values
df_timeseries = pd.DataFrame(
    index=pd.date_range(start=start, end=end, freq=time_freq, name="time")
)

df_component_values = pd.DataFrame(index=[0])

# %% environment

environment = Environment(
    timebase=timebase,
    timezone="Europe/Berlin",
    start=start,
    end=end,
    year=year,
    time_freq=time_freq,
)

environment.get_mean_temp_days()
environment.get_mean_temp_hours()
environment.get_pv_data()
environment.get_wind_data()

# %% baseload

# input data
baseload = pd.read_csv("./input/baseload/df_S_15min.csv")
baseload.drop(columns=["Time"], inplace=True)
baseload.index = pd.date_range(
    start=year, periods=35040, freq=time_freq, name="time"
)

# %% generate user profiles

up_dict = {}
count = 0
while count < bus_number:
    
    user_profile = UserProfile(
        identifier=(identifier + str(count)),
        latitude=latitude,
        longitude=longitude,
        thermal_energy_demand_yearly=yearly_thermal_energy_demand,
        building_type=building_type,
        comfort_factor=None,
        t_0=t_0,
        daily_vehicle_usage=None,
        week_trip_start=[],
        week_trip_end=[],
        weekend_trip_start=[],
        weekend_trip_end=[],
    )
    
    user_profile.baseload = pd.DataFrame(
        baseload[
            str(random.randint(0, (len(baseload.columns) -1)))].loc[start:end]
        / 1000)
    # thermal energy demand equals two times the electrical energy demand:
    user_profile.thermal_energy_demand_yearly = (user_profile.baseload.sum()
                                                 / 1000
                                                 / 2).item()
    user_profile.get_thermal_energy_demand()

    up_dict[user_profile.identifier] = user_profile
    count += 1

# create a list of all user profiles and shuffle that list to obtain a random
# assignment of components to the bus
up_list = list(up_dict.keys())
random.shuffle(up_list)

# %% pick buses with components

#pv_amount = int(round((len(up_dict.keys()) * (pv_percentage/100)), 0))
up_with_pv = random.sample(list(up_dict.keys()), pv_number)

#hp_amount = int(round((len(up_dict.keys()) * (hp_percentage/100)), 0))
up_with_hp = random.sample(list(up_dict.keys()), hp_number)

#bev_amount = int(round((len(up_dict.keys()) * (bev_percentage/100)), 0))
up_with_bev = random.sample(list(up_dict.keys()), bev_number)

#wind_amount = int(round((len(up_dict.keys()) * (wind_percentage/100)), 0))
up_with_wind = random.sample(list(up_dict.keys()), wind_number)

# Distribution of el storage is only done for houses with pv
#storage_amount = int(round((len(buses_with_pv) * (storage_percentage/100)), 0))
up_with_ees = random.sample(up_with_pv, ees_number)

# %% virtual power plant

vpp = VirtualPowerPlant("vpp")

# %% generate pv

for up in up_with_pv:

    new_component = Photovoltaic(
    unit="kW",
    identifier=(up_dict[up].identifier + "_pv"),
    environment=environment,
    user_profile=up_dict[up],
    module_lib=module_lib,
    module=module,
    inverter_lib=inverter_lib,
    inverter=inverter,
    surface_tilt=surface_tilt,
    surface_azimuth=surface_azimuth,
    modules_per_string=modules_per_string,
    strings_per_inverter=strings_per_inverter,
)
    new_component.prepare_time_series()
    vpp.add_component(new_component)

# %% generate ees
count = 0
while count < ees_number:
    new_ees = ElectricalEnergyStorage(
    unit="kWh",
    identifier=(identifier + "_ees" + "_" + str(count)),
    environment=environment,
    user_profile=user_profile,
    capacity=capacity,
    charge_efficiency=charge_efficiency,
    discharge_efficiency=discharge_efficiency,
    max_power=max_power,
    max_c=max_c,
)

    # new_ees.prepare_time_series()
    vpp.add_component(new_ees)
    count += 1

# %% generate wea
count = 0
while count < wind_number:
    new_component = WindPower(
    unit="kW",
    identifier=(identifier + "_wea" + "_" + str(count)),
    environment=environment,
    user_profile=None,
    turbine_type=turbine_type,
    hub_height=hub_height,
    rotor_diameter=rotor_diameter,
    fetch_curve=fetch_curve,
    data_source=data_source,
    wind_speed_model=wind_speed_model,
    density_model=density_model,
    temperature_model=temperature_model,
    power_output_model=power_output_model,
    density_correction=density_correction,
    obstacle_height=obstacle_height,
    hellman_exp=hellman_exp,
)
    new_component.prepare_time_series()
    vpp.add_component(new_component)
    count += 1

# %% generate bev
count = 0
while count < bev_number:
    new_component = BatteryElectricVehicle(
    unit="kW",
    identifier=(identifier + "_bev" + "_" + str(count)),
    battery_max=battery_max,
    battery_min=battery_min,
    battery_usage=battery_usage,
    charging_power=charging_power,
    charge_efficiency=bev_charge_efficiency,
    environment=environment,
    user_profile=user_profile,
    load_degradation_begin=load_degradation_begin,
)
    new_component.timeseries = pd.DataFrame(
        index=pd.date_range(
            start=new_component.environment.start,
            end=new_component.environment.end,
            freq=new_component.environment.time_freq,
            name="Time",
        )
    )
    new_component.split_time()
    new_component.set_weekday()
    new_component.set_at_home()
    new_component.timeseries = new_component.at_home

    vpp.add_component(new_component)
    count += 1

# %% generate hp and tes
count = 0
while count < hp_number:
    new_storage = ThermalEnergyStorage(
        unit="kWh",
        identifier=(identifier + "_hp_tes" + "_" + str(count)),
        mass=mass_of_storage,
        cp=cp,
        hysteresis=hysteresis,
        target_temperature=target_temperature,
        thermal_energy_loss_per_day=thermal_energy_loss_per_day,
        environment=environment,
        user_profile=user_profile,
    )

    new_heat_pump = HeatPump(
        unit="kW",
        identifier=(identifier + "_hp" + "_" + str(count)),
        heat_pump_type=heat_pump_type,
        heat_sys_temp=heat_sys_temp,
        environment=environment,
        user_profile=user_profile,
        el_power=el_power_hp,
        th_power=th_power_hp,
        ramp_up_time=ramp_up_time,
        ramp_down_time=ramp_down_time,
        min_runtime=min_runtime_hp,
        min_stop_time=min_stop_time_hp,
    )

    for i in new_storage.user_profile.thermal_energy_demand.loc[start:end].index:
        new_storage.operate_storage(i, new_heat_pump)
        
    vpp.add_component(new_storage)
    vpp.add_component(new_heat_pump)
    count += 1

# %% generate chp and tes
count = 0
while count < chp_number:
    new_storage = ThermalEnergyStorage(
        unit="kWh",
        identifier=(identifier + "_chp_tes" + "_" + str(count)),
        mass=mass_of_storage,
        cp=cp,
        hysteresis=hysteresis,
        target_temperature=target_temperature,
        thermal_energy_loss_per_day=thermal_energy_loss_per_day,
        environment=environment,
        user_profile=user_profile,
    )

    new_chp = CombinedHeatAndPower(
    unit="kW",
    identifier=(identifier + "_chp" + "_" + str(count)),
    environment=environment,
    user_profile=user_profile,
    el_power=el_power_chp,
    th_power=th_power_chp,
    overall_efficiency=overall_efficiency,
    ramp_up_time=ramp_up_time,
    ramp_down_time=ramp_down_time,
    min_runtime=min_runtime_chp,
    min_stop_time=min_stop_time_chp,
)

    for i in new_storage.user_profile.thermal_energy_demand.loc[start:end].index:
        new_storage.operate_storage(i, new_chp)
        
    vpp.add_component(new_storage)
    vpp.add_component(new_chp)
    count += 1
