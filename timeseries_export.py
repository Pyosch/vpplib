# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 15:50:38 2019

@author: pyosch
"""

import pandas as pd
import matplotlib.pyplot as plt

from vpplib.battery_electric_vehicle import BatteryElectricVehicle
from vpplib.photovoltaic import Photovoltaic
from vpplib.electrical_energy_storage import ElectricalEnergyStorage
from vpplib.heat_pump import HeatPump
from vpplib.environment import Environment
from vpplib.user_profile import UserProfile
from vpplib.thermal_energy_storage import ThermalEnergyStorage
from vpplib.combined_heat_and_power import CombinedHeatAndPower

# Values for environment
start = "2015-06-01 00:00:00"
end = "2015-06-07 23:45:00"
year = "2015"
time_freq = "15 min"
index_year = pd.date_range(
    start=year, periods=35040, freq=time_freq, name="time"
)
timebase = 15  # for calculations from kW to kWh
temp_days_file = "./input/thermal/dwd_temp_days_2015.csv"
temp_hours_file = "./input/thermal/dwd_temp_hours_2015.csv"

scenario = 2

# plot
figsize = (14, 7)

# dataframes for exporting timeseries and component values
df_timeseries = pd.DataFrame(
    index=pd.date_range(start=start, end=end, freq=time_freq, name="time")
)

df_component_values = pd.DataFrame(index=[0])

# Values for user profile
identifier = "bus_1"
latitude = 50.941357
longitude = 6.958307
target_temperature = 60  # °C
t_0 = 40  # °C
yearly_thermal_energy_demand = 12500  # kWh thermal

# Values for pv
pv_file = "./input/pv/dwd_pv_data_2015.csv"
module_lib = "SandiaMod"
module = "Canadian_Solar_CS5P_220M___2009_"
inverter_lib = "cecinverter"
inverter = "ABB__PVI_4_2_OUTD_S_US_Z_M_A__208_V__208V__CEC_2014_"
surface_tilt = 20
surface_azimuth = 200
modules_per_string = 10
strings_per_inverter = 2

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

# Values for heat pump
heatpump_type = "Air"
heat_sys_temp = 60
el_power_hp = 5
th_power_hp = None
building_type = "DE_HEF33"
min_runtime_hp = 1  # timesteps
min_stop_time_hp = 2  # timesteps


# Values for Thermal Storage
hysteresis = 5  # °K
mass_of_storage = 500  # kg
cp = 4.2
heatloss_per_day = 0.13

# Values for chp
el_power_chp = 6  # kW
th_power_chp = 10  # kW
overall_efficiency = 0.8
ramp_up_time = 1 / 15  # timesteps
ramp_down_time = 1 / 15  # timesteps
min_runtime_chp = 1  # timesteps
min_stop_time_chp = 2  # timesteps

#%% environment

environment = Environment(
    timebase=timebase,
    timezone="Europe/Berlin",
    start=start,
    end=end,
    year=year,
    time_freq=time_freq,
)

environment.get_pv_data(file=pv_file)
environment.get_mean_temp_days(file=temp_days_file)
environment.get_mean_temp_hours(file=temp_hours_file)

#%% user profile

user_profile = UserProfile(
    identifier=identifier,
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

user_profile.get_thermal_energy_demand()

#%% baseload

# input data
baseload = pd.read_csv("./input/baseload/df_S_15min.csv")
baseload.drop(columns=["Time"], inplace=True)
baseload.index = pd.date_range(
    start=year, periods=35040, freq=time_freq, name="time"
)

df_timeseries["baseload"] = pd.DataFrame(baseload["0"].loc[start:end] / 1000)

df_timeseries.baseload.plot(figsize=figsize, label="baseload [kW]")

#%% PV

pv = Photovoltaic(
    unit="kW",
    identifier=(identifier + "_pv"),
    environment=environment,
    user_profile=user_profile,
    module_lib=module_lib,
    module=module,
    inverter_lib=inverter_lib,
    inverter=inverter,
    surface_tilt=surface_tilt,
    surface_azimuth=surface_azimuth,
    modules_per_string=modules_per_string,
    strings_per_inverter=strings_per_inverter,
)

df_timeseries["pv"] = pv.prepare_time_series() * -1

df_component_values["pv_kWp"] = (
    pv.module.Impo
    * pv.module.Vmpo
    / 1000
    * pv.system.modules_per_string
    * pv.system.strings_per_inverter
)
df_timeseries.pv.plot(figsize=figsize, label="pv [kW]")

#%% el storage

# create storage object
storage = ElectricalEnergyStorage(
    unit="kWh",
    identifier=(identifier + "_storage"),
    environment=environment,
    user_profile=user_profile,
    capacity=capacity,
    charge_efficiency=charge_efficiency,
    discharge_efficiency=discharge_efficiency,
    max_power=max_power,
    max_c=max_c,
)

df_component_values["el_storage_capacity"] = storage.capacity
df_component_values["el_storage_power"] = storage.max_power
df_component_values["el_storage_charge_efficiency"] = storage.charge_efficiency
df_component_values[
    "el_storage_discharge_efficiency"
] = storage.discharge_efficiency


#%% BEV

bev = BatteryElectricVehicle(
    identifier=(identifier + "_bev"),
    battery_max=battery_max,
    battery_min=battery_min,
    battery_usage=battery_usage,
    charging_power=charging_power,
    charge_efficiency=bev_charge_efficiency,
    environment=environment,
    user_profile=user_profile,
)

df_component_values["bev_power"] = bev.charging_power
df_component_values["bev_efficiency"] = bev.charge_efficiency
df_component_values["bev_arrival_soc"] = (
    bev.battery_min / bev.battery_max * 100
)


def get_at_home(bev):

    bev.timeseries = pd.DataFrame(
        index=pd.date_range(
            start=bev.environment.start,
            end=bev.environment.end,
            freq=bev.environment.time_freq,
            name="Time",
        )
    )
    bev.split_time()
    bev.set_weekday()
    bev.set_at_home()

    return bev.at_home


df_timeseries["at_home"] = get_at_home(bev)

df_timeseries.at_home.plot(figsize=figsize, label="at home [0/1]")

#%% heat_pump

hp = HeatPump(
    identifier=(identifier + "_hp"),
    environment=environment,
    user_profile=user_profile,
    heat_pump_type=heatpump_type,
    heat_sys_temp=heat_sys_temp,
    el_power=el_power_hp,
    th_power=th_power_hp,
)

df_component_values["heat_pump_power_therm"] = hp.el_power

if scenario == 1:

    # For heat pump without thermal storage
    #    df_timeseries["heat_pump"] = hp.prepare_time_series().el_demand
    #    df_timeseries.heat_pump.plot(figsize=figsize, label="heat pump [kW-el]")

    tes_hp = ThermalEnergyStorage(
        mass=mass_of_storage,
        hysteresis=hysteresis,
        target_temperature=target_temperature,
        environment=environment,
        user_profile=user_profile,
    )

    hp = HeatPump(
        identifier="hp1",
        environment=environment,
        user_profile=user_profile,
        el_power=el_power_hp,
        ramp_up_time=ramp_up_time,
        ramp_down_time=ramp_down_time,
        min_runtime=min_runtime_hp,
        min_stop_time=min_stop_time_hp,
    )

    loadshape = tes_hp.user_profile.thermal_energy_demand[0:][
        "thermal_energy_demand"
    ]
    outside_temp = tes_hp.user_profile.mean_temp_hours.temperature
    log, log_load, log_cop = [], [], []
    hp.last_ramp_up = hp.user_profile.thermal_energy_demand.index[0]
    hp.last_ramp_down = hp.user_profile.thermal_energy_demand.index[0]
    for i in hp.user_profile.thermal_energy_demand.index:
        thermal_energy_demand = hp.user_profile.thermal_energy_demand.thermal_energy_demand.loc[
            i
        ]
        if tes_hp.get_needs_loading():
            hp.ramp_up(i)
        else:
            hp.ramp_down(i)
        temp = tes_hp.operate_storage(thermal_energy_demand, i, hp)
        if hp.is_running:
            log_load.append(el_power_hp)
        else:
            log_load.append(0)
        log.append(temp)

    df_timeseries["heat_pump"] = pd.DataFrame(log_load, index=index_year).loc[
        start:end
    ]
    df_timeseries.heat_pump.plot(figsize=figsize, label="heat pump [kW-el]")

elif scenario == 2:

    df_timeseries["thermal_energy_demand"] = user_profile.thermal_energy_demand
    df_timeseries["cop"] = hp.get_cop()
    df_timeseries.cop.interpolate(inplace=True)

    df_timeseries.thermal_energy_demand.plot(
        figsize=figsize, label="thermal energy demand[kW-therm]"
    )
    df_timeseries.cop.plot(figsize=figsize, label="cop [-]")

else:
    print("Heat pump scenario ", scenario, " is not defined!")


#%% chp

tes_chp = ThermalEnergyStorage(
    identifier="th_storage",
    mass=mass_of_storage,
    environment=environment,
    user_profile=user_profile,
    hysteresis=hysteresis,
    target_temperature=target_temperature,
    cp=cp,
    thermal_energy_loss_per_day=heatloss_per_day,
)

chp = CombinedHeatAndPower(
    identifier="chp1",
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

# Formula: E = m * cp * T
df_component_values["therm_storage_capacity"] = (
    tes_chp.mass
    * tes_chp.cp
    * (tes_chp.target_temperature + tes_chp.hysteresis + 273.15)
)  # °K
df_component_values["thermal_storage_efficiency"] = 100 * (
    1 - tes_chp.thermal_energy_loss_per_day
)

if scenario == 1:

    loadshape = tes_chp.user_profile.thermal_energy_demand[0:][
        "thermal_energy_demand"
    ]
    outside_temp = tes_chp.user_profile.mean_temp_hours.temperature
    log, log_load, log_el = [], [], []
    chp.last_ramp_up = chp.user_profile.thermal_energy_demand.index[0]
    chp.last_ramp_down = chp.user_profile.thermal_energy_demand.index[0]
    for i in chp.user_profile.thermal_energy_demand.index:
        thermal_energy_demand = chp.user_profile.thermal_energy_demand.thermal_energy_demand.loc[
            i
        ]
        if tes_chp.get_needs_loading():
            chp.ramp_up(i)
        else:
            chp.ramp_down(i)
        temp = tes_chp.operate_storage(thermal_energy_demand, i, chp)
        if chp.is_running:
            log_load.append(th_power_chp)
            log_el.append(el_power_chp)
        else:
            log_load.append(0)
            log_el.append(0)
        log.append(temp)

    df_timeseries["chp_heat"] = (
        pd.DataFrame(log_load, index=index_year).loc[start:end] * -1
    )
    df_timeseries["chp_el"] = (
        pd.DataFrame(log_el, index=index_year).loc[start:end] * -1
    )

    df_timeseries.chp_heat.plot(figsize=figsize, label="chp gen[kW-therm]")
    df_timeseries.chp_el.plot(figsize=figsize, label="chp gen[kW-el]")

elif scenario == 2:

    df_component_values["chp_power_therm"] = chp.th_power
    df_component_values["chp_power_el"] = chp.el_power
    df_component_values["chp_efficiency"] = chp.overall_efficiency

else:
    print("chp scenario ", scenario, " is not defined!")


plt.legend()
print(df_component_values)

# df_timeseries.to_csv("./Results/df_timeseries.csv")
# df_component_values.to_csv("./Results/df_component_values.csv")
