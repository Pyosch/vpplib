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

pv_number = 5
wind_number = 2#2
bev_number = 5
hp_number = 5  # always includes thermal energy storage
ees_number = 5
chp_number = 0  # always includes thermal energy storage


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
yearly_thermal_energy_demand = None  # kWh thermal; redifined depending on el baseload

# Values for pv
module_lib = "SandiaMod"
# module = "Canadian_Solar_CS5P_220M___2009_"
inverter_lib = "SandiaInverter"
# inverter = "ABB__PVI_4_2_OUTD_S_US_Z_M_A__208_V__208V__CEC_2014_"
surface_tilt = 20
surface_azimuth = 200
# modules_per_string = 10
# strings_per_inverter = 2
min_module_power = 220
max_module_power = 250
#  pv_power will be choosen during function call
inverter_power_range = 100

# WindTurbine data
wea_list = [
        "E-53/800",
        "E48/800",
        "V100/1800",
        "E-82/2000",
        "V90/2000"]  # randomly choose windturbine
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
#  power and capacity will be randomly assigned during component generation
# max_power = 4  # kW
# capacity = 4  # kWh
max_c = 1  # factor between 0.5 and 1.2

# Values for bev
#  power and capacity will be randomly assigned during component generation
# battery_max = 16
battery_min = 4
battery_usage = 1
# charging_power = 11
bev_charge_efficiency = 0.98
load_degradation_begin = 0.8

# Values for heat pump
heat_pump_type = "Air"
heat_sys_temp = 60
el_power_hp_min = 5
el_power_hp_max = 11
th_power_hp = None
building_type = "DE_HEF33"
ramp_up_time_hp = 1 / 15  # timesteps
ramp_down_time_hp = 1 / 15  # timesteps
min_runtime_hp = 1  # timesteps
min_stop_time_hp = 2  # timesteps

# Values for Thermal Storage
hysteresis = 5  # °K
#  radomly assigned during component generation
mass_of_storage_min = 400  # kg
mass_of_storage_max = 800  # kg
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
                                                 / 2).item()  # /4 *2= /2
    user_profile.get_thermal_energy_demand()

    up_dict[user_profile.identifier] = user_profile
    count += 1

# create a list of all user profiles and shuffle that list to obtain a random
# assignment of components to the bus
up_list = list(up_dict.keys())
random.shuffle(up_list)

# %% pick buses with components

#wind_amount = int(round((len(up_dict.keys()) * (wind_percentage/100)), 0))
up_with_wind = random.sample(list(up_dict.keys()), wind_number)

#pv_amount = int(round((len(up_dict.keys()) * (pv_percentage/100)), 0))
up_with_pv = random.sample(
    [x for x in list(up_dict.keys()) if x not in up_with_wind], pv_number)

#hp_amount = int(round((len(up_dict.keys()) * (hp_percentage/100)), 0))
up_with_hp = random.sample(
    [x for x in list(up_dict.keys()) if x not in up_with_wind], hp_number)

#chp_amount = int(round((len(up_dict.keys()) * (chp_percentage/100)), 0))
up_with_chp = random.sample(
    [x for x in list(up_dict.keys()) if x not in up_with_wind], chp_number)

#bev_amount = int(round((len(up_dict.keys()) * (bev_percentage/100)), 0))
up_with_bev = random.sample(
    [x for x in list(up_dict.keys()) if x not in up_with_wind], bev_number)

# Distribution of el storage is only done for houses with pv
#storage_amount = int(round((len(buses_with_pv) * (storage_percentage/100)), 0))
up_with_ees = random.sample(up_with_pv, ees_number)

# %% virtual power plant

vpp = VirtualPowerPlant("vpp")

# %% generate pv

for up in up_with_pv:

    pv_power = random.randrange(start=6000, stop=9000, step=100)
    surface_tilt = random.randrange(start=20, stop=40, step=5)
    surface_azimuth = random.randrange(start=160, stop=220, step=10)

    new_component = Photovoltaic(
    unit="kW",
    identifier=(up_dict[up].identifier + "_pv"),
    environment=environment,
    user_profile=up_dict[up],
    module_lib=module_lib,
    module=None,
    inverter_lib=inverter_lib,
    inverter=None,
    surface_tilt=surface_tilt,
    surface_azimuth=surface_azimuth,
    modules_per_string=None,
    strings_per_inverter=None,
    )

    new_component.pick_pvsystem(min_module_power,
                                max_module_power,
                                pv_power,
                                inverter_power_range)

    new_component.prepare_time_series()
    vpp.add_component(new_component)

    # export
    df_timeseries[new_component.identifier] = new_component.timeseries * -1

    df_component_values[new_component.identifier + "_kWp"] = (
        new_component.module.Impo
        * new_component.module.Vmpo
        / 1000
        * new_component.system.modules_per_string
        * new_component.system.strings_per_inverter
    )
# %% generate ees

for up in up_with_ees:

    cap_power = random.randrange(start=5, stop=9, step=1)

    new_component = ElectricalEnergyStorage(
    unit="kWh",
    identifier=(up_dict[up].identifier + "_ees"),
    environment=environment,
    user_profile=up_dict[up],
    capacity=cap_power,
    charge_efficiency=charge_efficiency,
    discharge_efficiency=discharge_efficiency,
    max_power=cap_power,
    max_c=max_c,
    )

    # new_component.prepare_time_series()
    vpp.add_component(new_component)
    
    # export
    
    df_component_values[
        new_component.identifier + "_capacity"
        ] = new_component.capacity
    df_component_values[
        new_component.identifier + "_power"
        ] = new_component.max_power
    df_component_values[
        new_component.identifier + "_charge_efficiency"
        ] = new_component.charge_efficiency
    df_component_values[
        new_component.identifier + "_discharge_efficiency"
    ] = new_component.discharge_efficiency


# %% generate wea

for up in up_with_wind:

    new_component = WindPower(
    unit="kW",
    identifier=(up_dict[up].identifier + "_wea"),
    environment=environment,
    user_profile=None,
    turbine_type=wea_list[random.randint(0, (len(wea_list) -1))],
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
    
    # export
    
    df_timeseries[new_component.identifier] = new_component.timeseries * -1
    
    df_component_values[new_component.identifier + "_kw"] = (
        new_component.ModelChain.power_plant.nominal_power / 1000
    )

# %% generate bev

for up in up_with_bev:

    new_component = BatteryElectricVehicle(
    unit="kW",
    identifier=(up_dict[up].identifier + "_bev"),
    battery_max=random.sample([50, 60, 17.6, 64, 33.5, 38.3,75, 20, 27.2, 6.1]
                              , 1)[0],
    battery_min=battery_min,
    battery_usage=battery_usage,
    charging_power=random.sample([3.6, 11, 22], 1)[0],
    charge_efficiency=bev_charge_efficiency,
    environment=environment,
    user_profile=up_dict[up],
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

    # export

    df_component_values[
        new_component.identifier + "_power"
        ] = new_component.charging_power
    df_component_values[
        new_component.identifier + "_battery_max"
        ] = new_component.battery_max
    df_component_values[
        new_component.identifier + "_efficiency"
        ] = new_component.charge_efficiency
    df_component_values[
        new_component.identifier + "_arrival_soc"
        ] = random.uniform(new_component.battery_min,
                           new_component.battery_max)

    df_timeseries[new_component.identifier] = new_component.timeseries

# %% generate hp and tes

for up in up_with_hp:

    new_storage = ThermalEnergyStorage(
        unit="kWh",
        identifier=(up_dict[up].identifier + "_hp_tes"),
        mass=random.randrange(start=mass_of_storage_min,
                              stop=mass_of_storage_max,
                              step=100),
        cp=cp,
        hysteresis=hysteresis,
        target_temperature=target_temperature,
        thermal_energy_loss_per_day=thermal_energy_loss_per_day,
        environment=environment,
        user_profile=up_dict[up],
    )

    new_heat_pump = HeatPump(
        unit="kW",
        identifier=(up_dict[up].identifier + "_hp"),
        heat_pump_type=heat_pump_type,
        heat_sys_temp=heat_sys_temp,
        environment=environment,
        user_profile=up_dict[up],
        el_power=random.randrange(start=el_power_hp_min,
                                  stop=el_power_hp_max,
                                  step=1),
        th_power=th_power_hp,
        ramp_up_time=ramp_up_time,
        ramp_down_time=ramp_down_time,
        min_runtime=min_runtime_hp,
        min_stop_time=min_stop_time_hp,
    )

    # for i in new_storage.user_profile.thermal_energy_demand.loc[
    #         start:end].index:
    #     new_storage.operate_storage(i, new_heat_pump)

    vpp.add_component(new_storage)
    vpp.add_component(new_heat_pump)

    # export

    df_component_values[
        new_heat_pump.identifier + "_power"
        ] = new_heat_pump.el_power

    # Formula: E = m * cp * dT
    df_component_values[new_storage.identifier + "therm_storage_capacity"] = (
        new_storage.mass
        * new_storage.cp
        * (new_storage.hysteresis * 2)  #dT
        / 3600  # convert KJ to kW
    )
    df_component_values["thermal_storage_efficiency"] =(
        new_storage.thermal_energy_loss_per_day
        )
    df_timeseries[
        new_heat_pump.identifier + "_thermal_energy_demand"
        ] = up_dict[up].thermal_energy_demand
    df_timeseries[new_heat_pump.identifier + "_cop"] = new_heat_pump.get_cop()
    df_timeseries[new_heat_pump.identifier + "_cop"].interpolate(inplace=True)

# %% generate chp and tes

# for up in up_with_chp:

#     new_storage = ThermalEnergyStorage(
#         unit="kWh",
#         identifier=(up_dict[up].identifier + "_chp_tes"),
#         mass=mass_of_storage,
#         cp=cp,
#         hysteresis=hysteresis,
#         target_temperature=target_temperature,
#         thermal_energy_loss_per_day=thermal_energy_loss_per_day,
#         environment=environment,
#         user_profile=up_dict[up],
#     )

#     new_chp = CombinedHeatAndPower(
#     unit="kW",
#     identifier=(up_dict[up].identifier + "_chp"),
#     environment=environment,
#     user_profile=up_dict[up],
#     el_power=el_power_chp,
#     th_power=th_power_chp,
#     overall_efficiency=overall_efficiency,
#     ramp_up_time=ramp_up_time,
#     ramp_down_time=ramp_down_time,
#     min_runtime=min_runtime_chp,
#     min_stop_time=min_stop_time_chp,
# )

#     for i in new_storage.user_profile.thermal_energy_demand.loc[start:end].index:
#         new_storage.operate_storage(i, new_chp)

#     vpp.add_component(new_storage)
#     vpp.add_component(new_chp)

#     # export

#     df_component_values[new_chp.identifier + "_power_therm"] = new_chp.th_power
#     df_component_values[new_chp.identifier + "_power_el"] = new_chp.el_power
#     df_component_values[new_chp.identifier + "_efficiency"] = new_chp.overall_efficiency


#%% Export vpp information and timeseries

df_timeseries.to_csv("df_timeseries.csv")

df_component_values.to_csv("df_component_values.csv")