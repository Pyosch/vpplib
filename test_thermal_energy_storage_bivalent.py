# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 10:43:54 2020

@author: andre
test function operate_storage_bivalent
"""
from tqdm import tqdm
from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.ALTERNATIVE_thermal_energy_storage import ThermalEnergyStorage
from vpplib.heat_pump import HeatPump
from vpplib.heating_rod import HeatingRod
import matplotlib.pyplot as plt
from fct_optimize_bivalent import optimize_bivalent
import pandas as pd

figsize = (10, 6)
# Values for environment
start = "2015-01-01 00:00:00"
end = "2015-12-31 23:45:00"     
year = "2015"
timebase = 15

# Values for user_profile
yearly_thermal_energy_demand = 10000  # kWh
building_type = "DE_HEF33"
t_0 = 40  # °C

# Values for Thermal Storage
target_temperature = 60  # °C
hysteresis = 5  # °K
mass_of_storage = 500  # kg
cp = 4.2
efficiency_class = "A+"

# Values for Heatpump
#el_power = 5  # kW electric
#th_power = 8  # kW thermal
ramp_up_time = 1 / 15  # timesteps
ramp_down_time = 1 / 15  # timesteps
min_runtime = 1  # timesteps
min_stop_time = 2  # timesteps
heat_pump_type = "Ground"
heat_sys_temp = 60


t_norm = -12

environment = Environment(timebase=timebase, start=start, end=end, year=year)

user_profile = UserProfile(
    identifier=None,
    latitude=None,
    longitude=None,
    thermal_energy_demand_yearly=yearly_thermal_energy_demand,
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
    user_profile=user_profile,
    unit="kWh",
    cp=cp,
    mass=mass_of_storage,
    hysteresis=hysteresis,
    target_temperature=target_temperature,
    #thermal_energy_loss_per_day=thermal_energy_loss_per_day,
    efficiency_class = efficiency_class
)

hp = HeatPump(
    identifier="hp1",
    unit="kW",
    environment=environment,
    user_profile=user_profile,
    ramp_up_time=ramp_up_time,
    ramp_down_time=ramp_down_time,
    min_runtime=min_runtime,
    min_stop_time=min_stop_time,
    heat_pump_type=heat_pump_type,
    heat_sys_temp=heat_sys_temp,
)

hr = HeatingRod(
        identifier='hr1', 
        environment=environment, user_profile = user_profile,
        #el_power = el_power,
        rampUpTime = ramp_up_time, 
        rampDownTime = ramp_down_time, 
        min_runtime = min_runtime, 
        min_stop_time = min_stop_time)

mode = "overcome shutdown"
# layout tes and hp
tes.optimize_tes_hp(hp, mode)

# layout hp and hr bivalent - override layout of hp from before
modus = "alternative"
optimize_bivalent(hp, hr, modus, t_norm, user_profile)
#hp.el_power = 5

print("mass of tes: " + str(tes.mass) + " [kg]")
print("electrical power of hp: " + str(hp.el_power) + " [kW]")
#print("thermal power of hp: " + str(hp.th_power) + " [kW]")
print("electrical power of hr: " + str(hr.el_power) + " [kW]")
print(str(tes.efficiency_per_timestep))

for i in tqdm (tes.user_profile.thermal_energy_demand.loc[start:end].index):
    tes.operate_storage_bivalent(i, hp, hr, t_norm)


#tes.timeseries.plot(figsize=figsize, title="Temperature of Storage")
#plt.show()
#tes.timeseries.iloc[0:960].plot(
#    figsize=figsize, title="Temperature of Storage 10-Day View"
#)
#plt.show()
#tes.timeseries.iloc[0:96].plot(
#    figsize=figsize, title="Temperature of Storage Daily View"
#)
#plt.show()
#
#hp.timeseries.el_demand.plot(figsize=figsize, title="Electrical Loadshape hp")
#plt.show()
#hp.timeseries.el_demand.iloc[0:960].plot(
#    figsize=figsize, title="Electrical Loadshape hp 10-Day View"
#)
#plt.show()
#hp.timeseries.el_demand.iloc[0:96].plot(
#    figsize=figsize, title="Electrical Loadshape hp Daily View"
#)
#plt.show()
#
#hr.timeseries.el_demand.plot(figsize=figsize, title="Electrical Loadshape hr")
#plt.show()
#hr.timeseries.el_demand.iloc[0:960].plot(
#    figsize=figsize, title="Electrical Loadshape hr 10-Day View"
#)
#plt.show()
#hr.timeseries.el_demand.iloc[0:96].plot(
#    figsize=figsize, title="Electrical Loadshape hr Daily View"
#)
#plt.show()

print(hr.timeseries)
print(hp.timeseries)
print(tes.timeseries)

hp.timeseries.plot()
hr.timeseries.plot()
tes.timeseries.plot()

min_dem_hp = hp.timeseries.el_demand.min()
max_dem_hp = hp.timeseries.el_demand.max()
mean_dem_hp = hp.timeseries.el_demand.mean()
sum_dem_hp  = hp.timeseries.el_demand.sum() / 4

min_dem_hr = hr.timeseries.el_demand.min()
max_dem_hr = hr.timeseries.el_demand.max()
mean_dem_hr = hr.timeseries.el_demand.mean()
sum_dem_hr  = hr.timeseries.el_demand.sum() / 4

min_cop = hp.timeseries.cop.min()
max_cop = hp.timeseries.cop.max()
mean_cop = hp.timeseries.cop.mean()

max_output_hp = hp.timeseries.thermal_energy_output.max()
sum_output_hp = hp.timeseries.thermal_energy_output.sum() / 4
scop = sum_output_hp / sum_dem_hp

max_output_hr = hr.timeseries.thermal_energy_output.max()
sum_output_hr = hr.timeseries.thermal_energy_output.sum() / 4

print("min dem hp [kW]: " + str(min_dem_hp))
print("max dem hp [kW]: " + str(max_dem_hp))
print("mean dem hp [kW]: " + str(mean_dem_hp))
print("sum dem hp [kWh]: " + str(sum_dem_hp))

print("min dem hr [kW]: " + str(min_dem_hr))
print("max dem hr [kW]: " + str(max_dem_hr))
print("mean dem hr [kW]: " + str(mean_dem_hr))
print("sum dem hr [kWh]: " + str(sum_dem_hr))

print("sum output hp [kWh]: " + str(sum_output_hp))
print("scop hp [-]: " + str(scop))
print("sum output hr [kWh]: " + str(sum_output_hr))


df_complete = pd.concat([hr.timeseries, hp.timeseries, tes.timeseries], axis = 1)

df_complete.to_csv("./output/HP_ground_HR_eff1_TES.csv")