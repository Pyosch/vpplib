# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 16:57:02 2019

@author: patri
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 15:33:53 2019

@author: patri
"""
from model.VPPUserProfile import VPPUserProfile
from model.VPPEnvironment import VPPEnvironment
from model.VPPThermalEnergyStorage import VPPThermalEnergyStorage
from model.VPPCombinedHeatAndPower import VPPCombinedHeatAndPower
import matplotlib.pyplot as plt
import pandas as pd
#from tqdm import tqdm 


start = '2017-01-01 00:00:00'
end = '2017-12-31 23:45:00'
year = '2017'
periods = None
time_freq = "15 min"

#Values for Thermal Storage
target_temperature = 60 # °C
hysteresis = 5 # °K
mass_of_storage = 500 # kg
yearly_heat_demand = 2500 # kWh

#Values for chp
el_power = 4 #kw
th_power = 6 #kW
overall_efficiency = 0.8
rampUpTime = 1/15 #timesteps
rampDownTime = 1/15 #timesteps
min_runtime = 1 #timesteps
min_stop_time = 2 #timesteps
timebase = 15


environment = VPPEnvironment(timebase=timebase, start=start, end=end, year=year,
                             time_freq=time_freq)

user_profile = VPPUserProfile(yearly_heat_demand = yearly_heat_demand)

tes = VPPThermalEnergyStorage(environment=environment, 
                              user_profile = user_profile,
                              mass = mass_of_storage, 
                              hysteresis = hysteresis, 
                              target_temperature = target_temperature)

chp = VPPCombinedHeatAndPower(unit = "kW", identifier='chp1',
                              environment = environment, 
                              user_profile = user_profile,
                              el_power = el_power, 
                              th_power = th_power, 
                              overall_efficiency = overall_efficiency, 
                              rampUpTime = rampUpTime,
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
log, log_load, log_el = [], [],[]
#for i, heat_demand in tqdm(enumerate(loadshape)): 
chp.lastRampUp = chp.user_profile.heat_demand.index[0]
chp.lastRampDown = chp.user_profile.heat_demand.index[0]
for i in chp.user_profile.heat_demand.index:
    heat_demand = chp.user_profile.heat_demand.heat_demand.loc[i]
    if tes.get_needs_loading(): 
        chp.rampUp(i)              
    else: 
        chp.rampDown(i)
    temp = tes.operate_storage(heat_demand, i, chp)
    if chp.isRunning: 
        log_load.append(th_power)
        log_el.append(el_power)
    else: 
        log_load.append(0)
        log_el.append(0)
    log.append(temp)

pd.DataFrame(log).plot(figsize = (16,9), title = "Yearly Temperature of Storage")
pd.DataFrame(log)[10000:10960].plot(figsize = (16,9),title = "10-Day View")
pd.DataFrame(log)[10000:10096].plot(figsize = (16,9),title = "Daily View")
pd.DataFrame(log_load).plot(figsize = (16,9), title = "Yearly Thermal Loadshape")
pd.DataFrame(log_load)[20000:20960].plot(figsize = (16,9),title = "10-Day View")
pd.DataFrame(log_load)[20000:20096].plot(figsize = (16,9),title = "Daily View")
pd.DataFrame(log_el).plot(figsize = (16,9), title = "Yearly Electrical Loadshape")
pd.DataFrame(log_el)[20000:20960].plot(figsize = (16,9),title = "10-Day View")
pd.DataFrame(log_el)[20000:20096].plot(figsize = (16,9),title = "Daily View")

