# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 15:33:53 2019

@author: patri, pyosch
"""
from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.thermal_energy_storage import ThermalEnergyStorage
from vpplib.heat_pump import HeatPump
import matplotlib.pyplot as plt

figsize = (10, 6)
#Values for environment
start = '2015-01-01 00:00:00'
end = '2015-01-31 23:45:00'
year = '2015'

#Values for user_profile
yearly_thermal_energy_demand = 15000 # kWh
building_type = 'DE_HEF33'
t_0 = 40  # °C

#Values for Thermal Storage
target_temperature = 60  # °C
hysteresis = 5  # °K
mass_of_storage = 500  # kg

#Values for Heatpump
el_power = 5 #kW electric
ramp_up_time = 1 / 15 #timesteps
ramp_down_time = 1 / 15 #timesteps
min_runtime = 1 #timesteps
min_stop_time = 2 #timesteps
timebase = 15
type_hp = "Ground"
heat_sys_temp = 60

environment = Environment(timebase=timebase, start=start, end=end, year=year)

user_profile = UserProfile(identifier=None,
                           latitude=None,
                           longitude=None,
                           thermal_energy_demand_yearly=yearly_thermal_energy_demand,
                           building_type=building_type,
                           comfort_factor=None,
                           t_0=t_0)


def test_get_thermal_energy_demand(user_profile):
    
    user_profile.get_thermal_energy_demand()
    user_profile.thermal_energy_demand.plot()
    plt.show()


test_get_thermal_energy_demand(user_profile)

tes = ThermalEnergyStorage(environment=environment, user_profile=user_profile,
                           mass=mass_of_storage,
                           hysteresis=hysteresis,
                           target_temperature=target_temperature)

hp = HeatPump(identifier='hp1',
              environment=environment, user_profile=user_profile,
              el_power=el_power, ramp_up_time=ramp_up_time,
              ramp_down_time=ramp_down_time,
              min_runtime=min_runtime, heat_pump_type = type_hp,
              min_stop_time=min_stop_time,
              heat_sys_temp = heat_sys_temp)

mode = "overcome shutdown"
# layout of hp and tes according to thermal energy demand
tes.optimize_tes_hp(hp, mode)

print("mass of tes: " + str(tes.mass) + " [kg]")
print("electrical power of hp: " + str(hp.el_power) + " [kW]")
print("thermal power of hp: " + str(hp.th_power) + " [kW]")
print(tes.timeseries)

for i in tes.user_profile.thermal_energy_demand.loc[start:end].index:
    tes.operate_storage(i, hp)


tes.timeseries.plot(figsize=figsize, title="Temperature of Storage")
plt.show()
tes.timeseries.iloc[0:960].plot(figsize=figsize, title="Temperature of Storage 10-Day View")
plt.show()
tes.timeseries.iloc[0:96].plot(figsize=figsize, title="Temperature of Storage Daily View")
plt.show()
hp.timeseries.el_demand.plot(figsize=figsize, title="Electrical Loadshape")
plt.show()
hp.timeseries.el_demand.iloc[0:960].plot(figsize=figsize, title="Electrical Loadshape 10-Day View")
plt.show()
hp.timeseries.el_demand.iloc[0:96].plot(figsize=figsize, title="Electrical Loadshape Daily View")
plt.show()
