# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 15:35:09 2020

@author: sbirk
"""

import pandas as pd

from vpplib import VirtualPowerPlant, Operator, UserProfile, Environment
from vpplib import Photovoltaic, WindPower, BatteryElectricVehicle

pv_number = 20
wind_number = 20
bev_number = 20


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
temp_days_file = "./input/thermal/dwd_temp_days_2015.csv"
temp_hours_file = "./input/thermal/dwd_temp_hours_2015.csv"

# Values for user profile
identifier = "bus_1"
latitude = 50.941357
longitude = 6.958307
target_temperature = 60  # °C
t_0 = 40  # °C
yearly_thermal_energy_demand = None  # kWh thermal; redifined in line 119

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

# WindTurbine data
wind_file = "./input/wind/dwd_wind_data_2015.csv"
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

# Values for bev
battery_max = 16
battery_min = 4
battery_usage = 1
charging_power = 11
bev_charge_efficiency = 0.98
load_degradation_begin = 0.8

# %% environment

environment = Environment(
    timebase=timebase,
    timezone="Europe/Berlin",
    start=start,
    end=end,
    year=year,
    time_freq=time_freq,
)

environment.get_pv_data(file=pv_file)
environment.get_wind_data(file=wind_file, utc=False)

# %% user profile

user_profile = UserProfile(
    identifier=identifier,
    latitude=latitude,
    longitude=longitude,
    thermal_energy_demand_yearly=yearly_thermal_energy_demand,
    building_type=None,
    comfort_factor=None,
    t_0=t_0,
    daily_vehicle_usage=None,
    week_trip_start=[],
    week_trip_end=[],
    weekend_trip_start=[],
    weekend_trip_end=[],
)

# %% baseload

# input data
baseload = pd.read_csv("./input/baseload/df_S_15min.csv")
baseload.drop(columns=["Time"], inplace=True)
baseload.index = pd.date_range(
    start=year, periods=35040, freq=time_freq, name="time"
)

user_profile.baseload = pd.DataFrame(baseload["0"].loc[start:end] / 1000)
# thermal energy demand equals two times the electrical energy demand:
user_profile.thermal_energy_demand_yearly = pd.DataFrame(baseload["0"]
                                                         / 1000).sum()/2

# %% virtual power plant

vpp = VirtualPowerPlant("vpp")

# %% generate pv
count = 0
while count < pv_number:
    new_component = Photovoltaic(
    unit="kW",
    identifier=(identifier + "_pv" + "_" + str(count)),
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
    new_component.prepare_time_series()
    vpp.add_component(new_component)
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
    new_component.prepare_time_series()
    vpp.add_component(new_component)
    count += 1
    
