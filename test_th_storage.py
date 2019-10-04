# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 15:33:53 2019

@author: patri, pyosch
"""
from model.VPPUserProfile import VPPUserProfile
from model.VPPEnvironment import VPPEnvironment
from model.VPPThermalEnergyStorage import VPPThermalEnergyStorage
from model.VPPHeatPump import VPPHeatPump
import matplotlib.pyplot as plt
import pandas as pd
#from tqdm import tqdm 

#Values for environment
start = '2017-01-01 00:00:00'
end = '2017-12-31 23:45:00'
year = '2017'

#Values for user_profile
yearly_heat_demand = 12500
building_type = 'DE_HEF33'
t_0 = 40

#Values for Thermal Storage
target_temperature = 60 # °C
hysteresis = 5 # °K
mass_of_storage = 500 # kg
yearly_heat_demand = 2500 # kWh

#Values for Heatpump
el_power = 5 #kW electric
rampUpTime = 1/15 #timesteps
rampDownTime = 1/15 #timesteps
min_runtime = 1 #timesteps
min_stop_time = 2 #timesteps
timebase = 15

environment = VPPEnvironment(timebase=timebase, start=start, end=end, year=year)

up = VPPUserProfile(yearly_heat_demand = yearly_heat_demand)

tes = VPPThermalEnergyStorage(environment=environment, user_profile = up,
                              mass = mass_of_storage, 
                              hysteresis = hysteresis, 
                              target_temperature = target_temperature)

hp = VPPHeatPump(identifier='hp1', environment=environment, user_profile = up,
                 el_power = el_power, rampUpTime = rampUpTime, 
                 rampDownTime = rampDownTime, 
                 min_runtime = min_runtime, 
                 min_stop_time = min_stop_time)

def test_get_heat_demand(tes):
    
    tes.user_profile.get_heat_demand()
    tes.user_profile.heat_demand.plot()
    plt.show()
    
test_get_heat_demand(tes)


loadshape = tes.user_profile.get_heat_demand()[0:]["heat_demand"]
outside_temp = tes.user_profile.mean_temp_hours.mean_temp
outside_temp.plot()
log, log_load, log_cop = [], [],[]
hp.lastRampUp = hp.user_profile.heat_demand.index[0]
hp.lastRampDown = hp.user_profile.heat_demand.index[0]
for i in hp.user_profile.heat_demand.index:
    heat_demand = hp.user_profile.heat_demand.heat_demand.loc[i]
    if tes.get_needs_loading(): 
        hp.rampUp(i)              
    else: 
        hp.rampDown(i)
    temp = tes.operate_storage(heat_demand, i, hp)
    if hp.isRunning: 
        log_load.append(el_power)
    else: 
        log_load.append(0)
    log.append(temp)

pd.DataFrame(log).plot(figsize = (16,9), title = "Yearly Temperature of Storage")
pd.DataFrame(log)[10000:10960].plot(figsize = (16,9),title = "10-Day View")
pd.DataFrame(log)[10000:10096].plot(figsize = (16,9),title = "Daily View")
pd.DataFrame(log_load).plot(figsize = (16,9), title = "Yearly Electrical Loadshape")
pd.DataFrame(log_load)[20000:20960].plot(figsize = (16,9),title = "10-Day View")
pd.DataFrame(log_load)[20000:20096].plot(figsize = (16,9),title = "Daily View")

