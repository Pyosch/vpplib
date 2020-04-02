# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 15:35:09 2020

Generate a virtual power plant based on predefined numbers of buses and
components.

Export timeseries and component values to csv-files at the end

@author: pyosch
"""

import pandas as pd
import random
import time

import simbench as sb
import pandapower as pp

from vpplib import VirtualPowerPlant, UserProfile, Environment, Operator
from vpplib import Photovoltaic, WindPower, BatteryElectricVehicle
from vpplib import HeatPump, ThermalEnergyStorage, ElectricalEnergyStorage
from vpplib import CombinedHeatAndPower

# define virtual power plant
pv_number = 5
wind_number = 2
bev_number = 5
hp_number = 5  # always includes thermal energy storage
ees_number = 5
chp_number = 5  # always includes thermal energy storage

lv_bus_number = pv_number + bev_number + hp_number + chp_number

# Simbench Network parameters
sb_code = "1-MVLV-semiurb-5.220-0-sw" # "1-LV-semiurb4--0-sw"

# Values for environment
start = "2015-07-01 00:00:00"
end = "2015-07-07 23:45:00"
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
# module will be choosen during function call
inverter_lib = "SandiaInverter"
# inverter will be choosen during function call
surface_tilt = 20
surface_azimuth = 200
# modules_per_string will be choosen during function call
# strings_per_inverter will be choosen during function call
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
# power and capacity will be randomly assigned during component generation
max_c = 1  # factor between 0.5 and 1.2

# Values for bev
# power and capacity will be randomly assigned during component generation
battery_min = 4
battery_usage = 1
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

print(time.asctime( time.localtime(time.time()) ))
print("Loaded input\n")
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

# %% virtual power plant

vpp = VirtualPowerPlant("vpp")

# %% Simbench network

net = sb.get_simbench_net(sb_code)

# plot the grid
pp.plotting.simple_plot(net)

# check that all needed profiles existent
assert not sb.profiles_are_missing(net)

# calculate absolute profiles
profiles = sb.get_absolute_values(net, profiles_instead_of_study_cases=True)

# get datetime index for profiles
profiles['load', 'p_mw'].index = pd.date_range(
    start=start[:4],
    periods=len(profiles['load', 'p_mw'].index),
    freq=time_freq)

print(time.asctime(time.localtime(time.time())))
print("Initialized environment, vpp and net\n")

# %% generate user profiles based on grid buses for lv

lv_buses = []
for bus in net.bus.name:
    if "LV" in bus:
        lv_buses.append(bus)

up_dict = {}
count = 0
while count <= lv_bus_number:

    # Get a bus with a load to add the loadprofile to the user_profile.
    # This the equivalent to a do-while-loop
    while True:
        simbus = random.sample(lv_buses, 1)[0]
        if len(net.load[net.load.bus == net.bus[
                net.bus.name == simbus].index.item()]) > 0:
            break

    user_profile = UserProfile(
        identifier=simbus,
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
        profiles['load', 'p_mw'][
            net.load[net.load.bus == net.bus[
                net.bus.name == simbus].index.item()].iloc[0].name # net.bus.name == simbus].index.item()].index.item()
            ].loc[start:end]
        * 1000)
    # thermal energy demand equals two times the electrical energy demand:
    user_profile.thermal_energy_demand_yearly = (user_profile.baseload.sum()
                                                 / 2).item()  # /4 *2= /2
    user_profile.get_thermal_energy_demand()

    up_dict[user_profile.identifier] = user_profile
    count += 1

# %% generate user profiles based on grid buses for mv

if wind_number > 0:
    mv_buses = []

    for bus in net.bus.name:
        if "MV" in bus:
            mv_buses.append(bus)

count = 0
up_with_wind = []
while count < wind_number:

    simbus = random.sample(mv_buses, 1)[0]
    vpp.buses_with_wind.append(simbus)

    user_profile = UserProfile(
        identifier=simbus,
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

    up_with_wind.append(user_profile.identifier)

    up_dict[user_profile.identifier] = user_profile
    count += 1

# create a list of all user profiles and shuffle that list to obtain a random
# assignment of components to the bus
up_list = list(up_dict.keys())
random.shuffle(up_list)

print(time.asctime(time.localtime(time.time())))
print("Generated user_profiles\n")
# %% pick buses with components

vpp.buses_with_pv = random.sample(
    [x for x in list(up_dict.keys()) if x not in up_with_wind], pv_number)

vpp.buses_with_hp = random.sample(
    [x for x in list(up_dict.keys()) if x not in up_with_wind], hp_number)

vpp.buses_with_chp = random.sample(
    [x for x in list(up_dict.keys()) if x not in up_with_wind], chp_number)

vpp.buses_with_bev = random.sample(
    [x for x in list(up_dict.keys()) if x not in up_with_wind], bev_number)

# Distribution of el storage is only done for houses with pv
vpp.buses_with_ees = random.sample(vpp.buses_with_pv, ees_number)

# %% generate pv

for bus in vpp.buses_with_pv:

    pv_power = random.randrange(start=6000, stop=9000, step=100)
    surface_tilt = random.randrange(start=20, stop=40, step=5)
    surface_azimuth = random.randrange(start=160, stop=220, step=10)

    new_component = Photovoltaic(
    unit="kW",
    identifier=(bus + "_pv"),
    environment=environment,
    user_profile=up_dict[bus],
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

    # TODO
    # Somehow in some pvlib timeseries the inverter losses during night hours
    # are not complete. Once we find out how to solve this problem we can
    # delete this part:
    if new_component.timeseries.isnull().values.any():
            new_component.timeseries.fillna(
                value=new_component.timeseries.min(),
                inplace=True)

    vpp.add_component(new_component)

# %% generate ees

for bus in vpp.buses_with_ees:

    cap_power = random.randrange(start=5, stop=9, step=1)

    new_component = ElectricalEnergyStorage(
    unit="kWh",
    identifier=(bus + "_ees"),
    environment=environment,
    user_profile=up_dict[bus],
    capacity=cap_power,
    charge_efficiency=charge_efficiency,
    discharge_efficiency=discharge_efficiency,
    max_power=cap_power,
    max_c=max_c,
    )

    vpp.add_component(new_component)

# %% generate wea

for bus in vpp.buses_with_wind:

    new_component = WindPower(
    unit="kW",
    identifier=(bus + "_wea"),
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

# %% generate bev

for bus in vpp.buses_with_bev:

    new_component = BatteryElectricVehicle(
    unit="kW",
    identifier=(bus + "_bev"),
    battery_max=random.sample([50, 60, 17.6, 64, 33.5, 38.3,75, 20, 27.2, 6.1]
                              , 1)[0],
    battery_min=battery_min,
    battery_usage=battery_usage,
    charging_power=random.sample([3.6, 11, 22], 1)[0],
    charge_efficiency=bev_charge_efficiency,
    environment=environment,
    user_profile=up_dict[bus],
    load_degradation_begin=load_degradation_begin,
    )

    new_component.prepare_time_series()
    vpp.add_component(new_component)

# %% generate hp and tes

for bus in vpp.buses_with_hp:

    new_storage = ThermalEnergyStorage(
        unit="kWh",
        identifier=(bus + "_hp_tes"),
        mass=random.randrange(start=mass_of_storage_min,
                              stop=mass_of_storage_max,
                              step=100),
        cp=cp,
        hysteresis=hysteresis,
        target_temperature=target_temperature,
        thermal_energy_loss_per_day=thermal_energy_loss_per_day,
        environment=environment,
        user_profile=up_dict[bus],
    )

    new_heat_pump = HeatPump(
        unit="kW",
        identifier=(bus + "_hp"),
        heat_pump_type=heat_pump_type,
        heat_sys_temp=heat_sys_temp,
        environment=environment,
        user_profile=up_dict[bus],
        el_power=random.randrange(start=el_power_hp_min,
                                  stop=el_power_hp_max,
                                  step=1),
        th_power=th_power_hp,
        ramp_up_time=ramp_up_time,
        ramp_down_time=ramp_down_time,
        min_runtime=min_runtime_hp,
        min_stop_time=min_stop_time_hp,
    )

    # generate timeseries for heat pump and storage
    for i in new_storage.user_profile.thermal_energy_demand.loc[start:end].index:
        new_storage.operate_storage(i, new_heat_pump)

    vpp.add_component(new_storage)
    vpp.add_component(new_heat_pump)


# %% generate chp and tes

for bus in vpp.buses_with_chp:

    new_storage = ThermalEnergyStorage(
        unit="kWh",
        identifier=(bus + "_chp_tes"),
        mass=random.randrange(start=mass_of_storage_min,
                              stop=mass_of_storage_max,
                              step=100),
        cp=cp,
        hysteresis=hysteresis,
        target_temperature=target_temperature,
        thermal_energy_loss_per_day=thermal_energy_loss_per_day,
        environment=environment,
        user_profile=up_dict[bus],
    )

    new_chp = CombinedHeatAndPower(
    unit="kW",
    identifier=(bus + "_chp"),
    environment=environment,
    user_profile=up_dict[bus],
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

print(time.asctime(time.localtime(time.time())))
print("Generated components in vpp\n")
# %% create elements in the pandapower.net

for bus in vpp.buses_with_pv:

    pp.create_sgen(
        net,
        bus=net.bus[net.bus.name == bus].index[0],
        p_mw=(
            vpp.components[bus + "_pv"].module.Impo
            * vpp.components[bus + "_pv"].module.Vmpo
            / 1000000
        ),
        q_mvar = 0,
        name=(bus + "_pv"),
        type="pv",
    )

for bus in vpp.buses_with_storage:

    pp.create_storage(
        net,
        bus=net.bus[net.bus.name == bus].index[0],
        p_mw=0,
        q_mvar = 0,
        max_e_mwh=vpp.components[bus].capacity / 1000,
        name=(bus + "_ees"),
        type="ees",
    )

for bus in vpp.buses_with_bev:

    pp.create_load(
        net,
        bus=net.bus[net.bus.name == bus].index[0],
        p_mw=(vpp.components[bus + "_bev"].charging_power / 1000),
        q_mvar = 0,
        name=(bus + "_bev"),
        type="bev",
    )

for bus in vpp.buses_with_hp:

    pp.create_load(
        net,
        bus=net.bus[net.bus.name == bus].index[0],
        p_mw=(vpp.components[bus + "_hp"].el_power / 1000),
        q_mvar = 0,
        name=(bus + "_hp"),
        type="hp",
    )

for bus in vpp.buses_with_wind:

    pp.create_sgen(
        net,
        bus=net.bus[net.bus.name == bus].index[0],
        p_mw=(
            vpp.components[bus + "_wea"].wind_turbine.nominal_power / 1000000
        ),
        q_mvar = 0,
        name=(bus + "_wea"),
        type="wea",
    )

print(time.asctime(time.localtime(time.time())))
print("Generated components in net\n")
# %% initialize operator

operator = Operator(virtual_power_plant=vpp, net=net, target_data=None)

print(time.asctime(time.localtime(time.time())))
print("Initialized Operator\n")

# %% timeseries are in kW, pandapower needs MW
for component in vpp.components.keys():
    # el energy storage does not have a timeseries yet
    if "_ees" not in component:
        vpp.components[component].timeseries /= 1000

# %% run base_scenario without operation strategies
net_dict = operator.run_simbench_scenario(profiles)

print(time.asctime(time.localtime(time.time())))
print("Finished run_simbench_scenario()\n")
# %% extract results from powerflow

results = operator.extract_results(net_dict)
single_result = operator.extract_single_result(
    net_dict, res="ext_grid", value="p_mw"
)

print(time.asctime(time.localtime(time.time())))
print("Exported results\n")
# %% plot results of powerflow and storage values

single_result.plot(
    figsize=(16, 9), title="ext_grid from single_result function"
)
operator.plot_results(results, legend=False)
operator.plot_storages()