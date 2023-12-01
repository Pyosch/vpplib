"""
Created on Tue Jul  2 10:38:17 2019

@author: Sascha Birk
"""

import pandas as pd
import pandapower as pp
import pandapower.networks as pn
import os

from vpplib.environment import Environment
from vpplib.user_profile import UserProfile
from vpplib.photovoltaic import Photovoltaic
from vpplib.battery_electric_vehicle import BatteryElectricVehicle
from vpplib.heat_pump import HeatPump
from vpplib.electrical_energy_storage import ElectricalEnergyStorage
from vpplib.wind_power import WindPower
from vpplib.virtual_power_plant import VirtualPowerPlant
from vpplib.operator import Operator


# def simulation(store_basic_settings, store_environment, store_user_profile, store_bev,
#                store_pv, store_wind, store_heatpump, store_storage):

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# environment
start = "2015-03-01 00:00:00"
end = "2015-03-01 23:45:00"
timezone = "Europe/Berlin"
year = "2015"
time_freq = "15 min"
timebase = 15
index = pd.date_range(start=start, end=end, freq=time_freq)
temp_days_file = f"{parentdir}/input/thermal/dwd_temp_days_2015.csv"
temp_hours_file = f"{parentdir}/input/thermal/dwd_temp_15min_2015.csv"

# user_profile
identifier = "bus_1"
latitude = 50.941357
longitude = 6.958307
yearly_thermal_energy_demand = 12500
comfort_factor = None
daily_vehicle_usage = None
building_type = "DE_HEF33"
t_0 = 40
week_trip_start = []
week_trip_end = []
weekend_trip_start = []
weekend_trip_end = []

baseload = pd.read_csv(f"{parentdir}/input/baseload/df_S_15min.csv")
baseload.drop(columns=["Time"], inplace=True)
baseload.index = pd.date_range(
    start=year, periods=35040, freq=time_freq, name="time"
)

unit = "kW"


baseload = pd.read_csv(f"{parentdir}/input/baseload/df_S_15min.csv")
baseload.drop(columns=["Time"], inplace=True)
baseload.index = pd.date_range(
    start=year, periods=35040, freq=time_freq, name="time"
)

unit = "kW"

# WindTurbine data
turbine_type = "E-126/4200"
hub_height = 135
rotor_diameter = 127
fetch_curve = "power_curve"
data_source = "oedb"

# WindPower ModelChain data
wind_file = f"{parentdir}/input/wind/dwd_wind_data_2015.csv"
wind_speed_model = "logarithmic"
density_model = "ideal_gas"
temperature_model = "linear_gradient"
power_output_model = "power_curve"
density_correction = True
obstacle_height = 0
hellman_exp = None

# PV data
pv_file = f"{parentdir}/input/pv/dwd_pv_data_2015.csv"
module_lib = "SandiaMod"
module = "Canadian_Solar_CS5P_220M___2009_"
inverter_lib = "cecinverter"
inverter = "ABB__MICRO_0_25_I_OUTD_US_208__208V_"
surface_tilt = (20,)
surface_azimuth = 200
modules_per_string = 2
strings_per_inverter = 2
temp_lib = 'sapm'
temp_model = 'open_rack_glass_glass'

    # BEV data
    # BEV data
battery_max = 16
battery_min = 0
battery_usage = 1
charging_power = 11
charge_efficiency_bev = 0.98
load_degradation_begin = 0.8

# heat pump data
heatpump_type = "Air"
heat_sys_temp = 60
el_power = 5
building_type = "DE_HEF33"
th_power = 3
ramp_up_time = 0
ramp_down_time = 0
min_runtime = 0
min_stop_time = 0

# storage
charge_efficiency_storage = 0.98
discharge_efficiency_storage = 0.98
max_power = 4  # kW
capacity = 4  # kWh
max_c = 1  # factor between 0.5 and 1.2

num_pv = 5
num_storage = 5
num_bev = 5
num_hp = 5
num_wind = 5

# environment

environment = Environment(
    timebase=timebase,
    timezone=timezone,
    start=start,
    end=end,
    year=year,
    time_freq=time_freq,
)

environment.get_wind_data(file=wind_file, utc=False)
environment.get_pv_data(file=pv_file)
environment.get_mean_temp_days(file=temp_days_file)
environment.get_mean_temp_hours(file=temp_hours_file)

# user profile

user_profile = UserProfile(
    identifier=identifier,
    latitude=latitude,
    longitude=longitude,
    thermal_energy_demand_yearly=yearly_thermal_energy_demand,
    building_type=building_type,
    comfort_factor=comfort_factor,
    t_0=t_0,
    daily_vehicle_usage=daily_vehicle_usage,
    week_trip_start=week_trip_start,
    week_trip_end=week_trip_end,
    weekend_trip_start=weekend_trip_start,
    weekend_trip_end=weekend_trip_end,
)

user_profile.get_thermal_energy_demand()

# create instance of VirtualPowerPlant and the designated grid
vpp = VirtualPowerPlant("Master")


# create components and assign components to the Virtual Powerplant

for pv in range(num_pv):

    vpp.add_component(
        Photovoltaic(
            unit=unit,
            identifier=("pv_" + str(pv)),
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
            temp_lib=temp_lib,
            temp_model=temp_model
        )
    )

    vpp.components[list(vpp.components.keys())[-1]].prepare_time_series()


for units in range(num_storage):

    vpp.add_component(
        ElectricalEnergyStorage(
            unit=unit,
            identifier=("storage_" + str(units)),
            environment=environment,
            user_profile=user_profile,
            capacity=capacity,
            charge_efficiency=charge_efficiency_storage,
            discharge_efficiency=discharge_efficiency_storage,
            max_power=max_power,
            max_c=max_c,
        )
    )

    vpp.components[list(vpp.components.keys())[-1]].timeseries = pd.DataFrame(
        columns=["state_of_charge", "residual_load"],
        index=pd.date_range(start=start, end=end, freq=time_freq),
    )


for bev in range(num_bev):

    vpp.add_component(
        BatteryElectricVehicle(
            unit=unit,
            identifier=("BEV_" + str(bev)),
            environment=environment,
            user_profile=user_profile,
            battery_max=battery_max,
            battery_min=battery_min,
            battery_usage=battery_usage,
            charging_power=charging_power,
            charge_efficiency=charge_efficiency_bev,
            load_degradation_begin=load_degradation_begin,
        )
    )

    vpp.components[list(vpp.components.keys())[-1]].prepare_time_series()


for hp in range(num_hp):

    vpp.add_component(
        HeatPump(
            unit=unit,
            identifier=("HP_" + str(hp)),
            environment=environment,
            user_profile=user_profile,
            heat_pump_type=heatpump_type,
            heat_sys_temp=heat_sys_temp,
            el_power=el_power,
            th_power=th_power,
            ramp_up_time=ramp_up_time,
            ramp_down_time=ramp_down_time,
            min_runtime=min_runtime,
            min_stop_time=min_stop_time,
        )
    )

    vpp.components[list(vpp.components.keys())[-1]].prepare_time_series()

for wind in range(num_wind):

    vpp.add_component(
        WindPower(
            unit=unit,
            identifier=("Wind_" + str(wind)),
            environment=environment,
            user_profile=user_profile,
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
    )

    vpp.components[list(vpp.components.keys())[-1]].prepare_time_series()


df_timeseries=vpp.export_component_timeseries()
print(df_timeseries)
# df_timeseries.to_csv(f"{parentdir}/input/df_timeseries.csv")