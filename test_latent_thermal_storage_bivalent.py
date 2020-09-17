# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 09:28:44 2020

@author: andre
test real using case of lts (charged by solar thermal, discharged by heat pump)
"""
from tqdm import tqdm
from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.latent_thermal_storage import LatentThermalStorage
from vpplib.heat_pump import HeatPump
import matplotlib.pyplot as plt

figsize = (10, 6)
# Values for environment
start = "2015-01-01 00:00:00"
end = "2015-03-31 23:45:00"
year = "2015"
timebase = 15

# Values for user_profile
yearly_thermal_energy_demand = 15000  # kWh
building_type = "DE_HEF33"
t_0 = 40  # °C

# Values for Thermal Storage 
t_over = 5  # K
t_under = 10  # K
mass_of_storage = 500  # kg


# Values for Heatpump
#el_power = 5  # kW electric
#th_power = 8  # kW thermal
ramp_up_time = 1 / 15  # timesteps
ramp_down_time = 1 / 15  # timesteps
min_runtime = 1  # timesteps
min_stop_time = 2  # timesteps
heat_pump_type = "Ground"
heat_sys_temp = 60

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

user_profile.get_thermal_energy_demand()    # steht ja eigentlich in funktion unten

def test_get_thermal_energy_demand(user_profile):

    user_profile.get_thermal_energy_demand()
    user_profile.thermal_energy_demand.plot()
    plt.show()


#test_get_thermal_energy_demand(user_profile)

lts = LatentThermalStorage(
        unit = "kW",
        identifier = "lts_1",
        t_over = t_over,
        t_under = t_under,
        environment = environment,
        user_profile = user_profile,
        mass = 500
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


hp.determine_optimum_thermal_power()
lts.layout_storage(hp)

print("areas heat exchangers: regeneration : " + str(lts.a_heat_exchanger_reg) +
      " [m2]; deprevation: " + str(lts.a_heat_exchanger_depr) + " [m2]")
print("mass lts: " + str(lts.mass) + " kg")
print("capacity lts: " + str(lts.capacity) + "kWh")
print("capacity solid: " + str(lts.capacity_solid) + "kWh")
print("capacity phase change: " + str(lts.capacity_phaseChange) + "kWh")
print("capacity fluid: " + str(lts.capacity_fluid) + "kWh")

print(lts.timeseries)


for i in tqdm(user_profile.thermal_energy_demand.loc[start:end].index):
    lts.operate_storage_bivalent(i, hp)


print(lts.timeseries)
print(hp.timeseries)

lts.timeseries.plot(figsize=figsize, title="Temperature of Storage")

el_demand = hp.timeseries.el_demand.loc[start:end].sum() * environment.timebase / 60

print("energy demand hp: " + str(el_demand) + " kWh")
print("for t_over: " + str(t_over) + " K, and")
print("for t_under: " + str(t_under) + " K")
