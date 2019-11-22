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
yearly_heat_demand = 2500 # kWh
building_type = 'DE_HEF33'
t_0 = 40  # °C

#Values for Thermal Storage
target_temperature = 60  # °C
hysteresis = 5  # °K
mass_of_storage = 500  # kg

#Values for Heatpump
el_power = 5 #kW electric
rampUpTime = 1/15 #timesteps
rampDownTime = 1/15 #timesteps
min_runtime = 1 #timesteps
min_stop_time = 2 #timesteps
timebase = 15

environment = Environment(timebase=timebase, start=start, end=end, year=year)

user_profile = UserProfile(identifier=None,
                           latitude=None,
                           longitude=None,
                           yearly_heat_demand=yearly_heat_demand,
                           building_type=building_type,
                           comfort_factor=None,
                           t_0=t_0)


def test_get_heat_demand(user_profile):
    
    user_profile.get_heat_demand()
    user_profile.heat_demand.plot()
    plt.show()


test_get_heat_demand(user_profile)

tes = ThermalEnergyStorage(environment=environment, user_profile=user_profile,
                           mass=mass_of_storage,
                           hysteresis=hysteresis,
                           target_temperature=target_temperature)

hp = HeatPump(identifier='hp1',
              environment=environment, user_profile=user_profile,
              el_power=el_power, ramp_up_time=rampUpTime,
              ramp_down_time=rampDownTime,
              min_runtime=min_runtime,
              min_stop_time=min_stop_time)


for i in tes.user_profile.heat_demand.loc[start:end].index:
    tes.operate_storage(i, hp)


tes.timeseries.plot(figsize=figsize, title="Temperature of Storage")
plt.show()
tes.timeseries.iloc[0:960].plot(figsize=figsize,title="Temperature of Storage 10-Day View")
plt.show()
tes.timeseries.iloc[0:96].plot(figsize=figsize, title="Temperature of Storage Daily View")
plt.show()
hp.timeseries.el_demand.plot(figsize=figsize, title="Electrical Loadshape")
plt.show()
hp.timeseries.el_demand.iloc[0:960].plot(figsize=figsize, title="Electrical Loadshape 10-Day View")
plt.show()
hp.timeseries.el_demand.iloc[0:96].plot(figsize=figsize, title="Electrical Loadshape Daily View")
plt.show()
