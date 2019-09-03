# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 15:33:53 2019

@author: patri
"""
from model.VPPUserProfile import VPPUserProfile as UP
from model.VPPThermalEnergyStorage import VPPThermalEnergyStorage
from model.VPPHeatPump import VPPHeatPump
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm 


start = '2017-01-01 00:00:00'
end = '2017-12-31 23:45:00'
year = '2017'
periods = None
freq = "15 min"

#Values for Thermal Storage
target_temperature = 60 # °C
hysteresis = 5 # °K
mass_of_storage = 500 # kg
yearly_heat_demand = 2500 # kWh

#Values for Heatpump
heatpump_power = 1 #kW
rampUpTime = 1/15 #timesteps
rampDownTime = 1/15 #timesteps
minimumRunningTime = 2 #timesteps
minimumStopTime = 2 #timesteps
timebase = 15


up = UP(heat_sys_temp = target_temperature, #Das könnte problematisch werden
        yearly_heat_demand = yearly_heat_demand, full_load_hours = 2100)

tes = VPPThermalEnergyStorage(timebase, mass = mass_of_storage, 
                              hysteresis = hysteresis, 
                              target_temperature = target_temperature, 
                              userProfile = up)

hp = VPPHeatPump(identifier='hp1', timebase=timebase, 
                 heatpump_power = heatpump_power, rampUpTime = rampUpTime, 
                 rampDownTime = rampDownTime, 
                 minimumRunningTime = minimumRunningTime, 
                 minimumStopTime = minimumStopTime, year=year)

def test_get_heat_demand(tes):
    
    tes.userProfile.get_heat_demand()
    tes.userProfile.heat_demand.plot()
    plt.show()
    
test_get_heat_demand(tes)

#def create_timeseries(tes, hp):
loadshape = tes.userProfile.get_heat_demand()[0:]["heat_demand"]
outside_temp = tes.userProfile.mean_temp_hours.mean_temp
thermal_power = hp.heatpump_power * timebase / 60 #thermal_energy?
tes.needs_loading = True
last_action = None
log, log_load, log_cop = [], [],[]
for i, heat_demand in tqdm(enumerate(loadshape)): 
    if tes.needs_loading: 
        if not last_action == "Ramp Up":
            if hp.rampUp(i): 
                last_action == "Ramp Up"                   
    else: 
        if not last_action == "Ramp Down":
            if hp.rampDown(i): 
                last_action == "Ramp Down"              
   
    
    if hp.isRunning(i): 
        el_demand, cop = hp.get_current_el_demand(outside_temp[int(i/(60/timebase))], heat_demand) 
        heat_demand -= thermal_power #warum?
    else: el_demand, cop = 0, 0
    
    temp, needs_loading = tes.charge(heat_demand)
    log.append(temp)
    log_load.append(el_demand)
    log_cop.append(cop)
pd.DataFrame(log).plot(title = "Yearly Temperature of Storage")
pd.DataFrame(log)[10000:10960].plot(title = "10-Day View")
pd.DataFrame(log)[10000:10096].plot(title = "Daily View")
pd.DataFrame(log_load).plot(title = "Electrical Loadshape")
pd.DataFrame(log_load)[10000:10960].plot(title = "Electrical Loadshape, 10-Day View")
pd.DataFrame(log_load)[10000:10096].plot(title = "Electrical Loadshape, Daily")
    
    #return pd.DataFrame(log_load)
    
#log_load = create_timeseries(tes, hp)
#test_get_heat_demand(tes)
