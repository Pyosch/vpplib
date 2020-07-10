# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 10:43:54 2020

@author: andre
test function operate_storage_bivalent
"""

from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.ALTERNATIVE_thermal_energy_storage import ThermalEnergyStorage
from vpplib.heat_pump import HeatPump
from vpplib.heating_rod import HeatingRod
import matplotlib.pyplot as plt
from fct_optimize_bivalent import optimize_bivalent

figsize = (10, 6)
# Values for environment
start = "2015-01-01 00:00:00"
end = "2015-01-31 23:45:00"     
year = "2015"
timebase = 15

# Values for user_profile
yearly_thermal_energy_demand = 15000  # kWh
building_type = "DE_HEF33"
t_0 = 40  # °C

# Values for Thermal Storage
target_temperature = 60  # °C
hysteresis = 5  # °K
mass_of_storage = 500  # kg
cp = 4.2
thermal_energy_loss_per_day = 0.13

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
    thermal_energy_loss_per_day=thermal_energy_loss_per_day,
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
#tes.optimize_tes_hp(hp, mode)

# layout hp and hr bivalent - override layout of hp from before
modus = "alternative"
optimize_bivalent(hp, hr, modus, t_norm, user_profile)
hp.el_power = 5

print("mass of tes: " + str(tes.mass) + " [kg]")
print("electrical power of hp: " + str(hp.el_power) + " [kW]")
#print("thermal power of hp: " + str(hp.th_power) + " [kW]")
print("electrical power of hr: " + str(hr.el_power) + " [kW]")

for i in tes.user_profile.thermal_energy_demand.loc[start:end].index:
    tes.operate_storage_bivalent(i, hp, hr, t_norm)


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

hp.timeseries.el_demand.plot(figsize=figsize, title="Electrical Loadshape hp")
plt.show()
hp.timeseries.el_demand.iloc[0:960].plot(
    figsize=figsize, title="Electrical Loadshape hp 10-Day View"
)
plt.show()
hp.timeseries.el_demand.iloc[0:96].plot(
    figsize=figsize, title="Electrical Loadshape hp Daily View"
)
plt.show()

# =============================================================================
# hr.timeseries.el_demand.plot(figsize=figsize, title="Electrical Loadshape hr")
# plt.show()
# hr.timeseries.el_demand.iloc[0:960].plot(
#     figsize=figsize, title="Electrical Loadshape hr 10-Day View"
# )
# plt.show()
# hr.timeseries.el_demand.iloc[0:96].plot(
#     figsize=figsize, title="Electrical Loadshape hr Daily View"
# )
# plt.show()
# =============================================================================
