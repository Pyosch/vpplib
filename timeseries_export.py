# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 15:50:38 2019

@author: pyosch
"""

import pandas as pd
import matplotlib.pyplot as plt

from model.VPPBEV import VPPBEV
from model.VPPPhotovoltaic import VPPPhotovoltaic
from model.VPPEnergyStorage import VPPEnergyStorage
from model.VPPHeatPump import VPPHeatPump
from model.VPPUserProfile import VPPUserProfile as UP
from model.VPPThermalEnergyStorage import VPPThermalEnergyStorage
from model.VPPCombinedHeatAndPower import VPPCombinedHeatAndPower

start = '2017-06-01 00:00:00'
end = '2017-06-07 23:45:00'
time_freq = "15 min"
timebase = 15/60 #for calculations from kW to kWh
scenario = 1
identifier = "house_1"

#plot
figsize=(14,7)

df_timeseries = pd.DataFrame(index = pd.date_range(start=start, end=end, 
                                         freq=time_freq, name ='Time'))

df_component_values = pd.DataFrame(index = [0])

#Values for pv
latitude = 50.941357
longitude = 6.958307
module_lib = 'SandiaMod'
module = 'Canadian_Solar_CS5P_220M___2009_'
inverter_lib = 'cecinverter'
inverter = 'ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_'
surface_tilt = 20
surface_azimuth = 200
modules_per_string = 1
strings_per_inverter = 1

#Values for el storage
chargeEfficiency = 0.98
dischargeEfficiency = 0.98
maxPower = 4 #kW
capacity = 4 #kWh
maxC = 1 #factor between 0.5 and 1.2

#Values for bev
start = start
end = end
time_freq = time_freq
battery_max = 16
battery_min = 4
battery_usage = 1
charging_power = 11
bev_chargeEfficiency = 0.98

#Values for heat pump
timebase = 1
heatpump_type = "Air"
heat_sys_temp = 60
heatpump_power = 10.6
full_load_hours = 2100
heat_demand_year = None
building_type = 'DE_HEF33'
year = '2017'
    
#Values for Thermal Storage
target_temperature = 60 # °C
hysteresis = 5 # °K
mass_of_storage = 500 # kg
cp = 4.2
heatloss_per_day = 0.13 
yearly_heat_demand = 2500 # kWh

#Values for chp
nominalPowerEl, nominalPowerTh = 4, 6 #kW
overall_efficiency = 0.8
rampUpTime = 1/15 #timesteps
rampDownTime = 1/15 #timesteps
minimumRunningTime = 1 #timesteps
minimumStopTime = 2 #timesteps

#%% baseload

#input data
baseload = pd.read_csv("./Input_House/Base_Szenario/df_S_15min.csv")
baseload.set_index(baseload.Time, inplace = True)
baseload.drop(labels="Time", axis=1, inplace = True)

df_timeseries["baseload"] = pd.DataFrame(baseload['0'].loc[start:end]/1000)

df_timeseries.baseload.plot(figsize=figsize, label="baseload [kW]")

#%% PV

weather_data = pd.read_csv("./Input_House/PV/2017_irradiation_15min.csv")
weather_data.set_index("index", inplace = True)

pv = VPPPhotovoltaic(timebase=1, identifier=(identifier+'_pv'), 
                     latitude=latitude, longitude=longitude, 
                     environment = None, userProfile = None,
                     start = start, end = end,
                     module_lib = module_lib, module = module, 
                     inverter_lib = inverter_lib, inverter = inverter,
                     surface_tilt = surface_tilt, surface_azimuth = surface_azimuth,
                     modules_per_string = modules_per_string, 
                     strings_per_inverter = strings_per_inverter)

df_timeseries["pv"] = pv.prepareTimeSeries(weather_data=weather_data)

df_timeseries.pv.plot(figsize=figsize, label="pv [kW]")

#%% el storage

#create storage object
storage = VPPEnergyStorage(timebase = timebase, identifier=(identifier+'_storage'), capacity=capacity, 
                           chargeEfficiency=chargeEfficiency, 
                           dischargeEfficiency=dischargeEfficiency, 
                           maxPower=maxPower, maxC=maxC, 
                           environment = None, userProfile = None)

df_component_values["el_storage_capacity"] = storage.capacity
df_component_values["el_storage_power"] = storage.maxPower
df_component_values["el_storage_charge_efficiency"] = storage.chargeEfficiency
df_component_values["el_storage_discharge_efficiency"] = storage.dischargeEfficiency


#%% BEV

bev = VPPBEV(timebase=timebase, identifier=(identifier+'_bev'), 
             start = start, end = end, time_freq = time_freq, 
             battery_max = battery_max, battery_min = battery_min, 
             battery_usage = battery_usage, 
             charging_power = charging_power, chargeEfficiency = bev_chargeEfficiency, 
             environment=None, userProfile=None)

df_component_values["bev_power"] = bev.charging_power
df_component_values["bev_efficiency"] = bev.bev_chargeEfficiency
df_component_values["bev_arrival_soc"] = bev.battery_min/bev.battery_max*100

def get_at_home(bev):
    
    weekend_trip_start = ['08:00:00', '08:15:00', '08:30:00', '08:45:00', 
                          '09:00:00', '09:15:00', '09:30:00', '09:45:00',
                          '10:00:00', '10:15:00', '10:30:00', '10:45:00', 
                          '11:00:00', '11:15:00', '11:30:00', '11:45:00', 
                          '12:00:00', '12:15:00', '12:30:00', '12:45:00', 
                          '13:00:00']
    
    weekend_trip_end = ['17:00:00', '17:15:00', '17:30:00', '17:45:00', 
                        '18:00:00', '18:15:00', '18:30:00', '18:45:00', 
                        '19:00:00', '19:15:00', '19:30:00', '19:45:00', 
                        '20:00:00', '20:15:00', '20:30:00', '20:45:00', 
                        '21:00:00', '21:15:00', '21:30:00', '21:45:00', 
                        '22:00:00', '22:15:00', '22:30:00', '22:45:00', 
                        '23:00:00']
    
    work_start = ['07:00:00', '07:15:00', '07:30:00', '07:45:00', 
                  '08:00:00', '08:15:00', '08:30:00', '08:45:00', 
                  '09:00:00']
    
    work_end = ['16:00:00', '16:15:00', '16:30:00', '16:45:00', 
                '17:00:00', '17:15:00', '17:30:00', '17:45:00', 
                '18:00:00', '18:15:00', '18:30:00', '18:45:00', 
                '19:00:00', '19:15:00', '19:30:00', '19:45:00', 
                '20:00:00', '20:15:00', '20:30:00', '20:45:00', 
                '21:00:00', '21:15:00', '21:30:00', '21:45:00', 
                '22:00:00']
    
    bev.timeseries = pd.DataFrame(index = pd.date_range(start=bev.start, end=bev.end, 
                                         freq=bev.time_freq, name ='Time'))
    bev.split_time() 
    bev.set_weekday()
    bev.set_at_home(work_start, work_end, weekend_trip_start, weekend_trip_end)
    
    return bev.at_home
    
df_timeseries["at_home"] = get_at_home(bev)

df_timeseries.at_home.plot(figsize=figsize, label="at home [0/1]")


#%% heat_pump

hp = VPPHeatPump(identifier = (identifier+'_hp'), timebase = timebase, 
                 heatpump_type = heatpump_type, 
                 heat_sys_temp = heat_sys_temp, environment = None, userProfile = None, 
                 heatpump_power = heatpump_power, full_load_hours = full_load_hours, 
                 heat_demand_year = None,
                 building_type = building_type, start = start,
                 end = end, year = year)

df_component_values["heat_pump_power_therm"] = hp.heatpump_power

if scenario == 1:
    
    df_timeseries["heat_pump"] = hp.prepareTimeSeries().el_demand
    df_timeseries.heat_pump.plot(figsize=figsize, label="heat pump [kW-el]")
    
elif scenario == 2:
    
    df_timeseries["heat_demand"] = hp.get_heat_demand()
    df_timeseries["cop"] = hp.get_cop()
    df_timeseries.cop.interpolate(inplace = True)
    
    df_timeseries.heat_demand.plot(figsize=figsize, label="heat demand[kW-therm]")
    df_timeseries.cop.plot(figsize=figsize, label="cop [-]")
    
else:
    print("Heat pump scenario ", scenario, " is not defined!")
    
    
#%% chp

up = UP(heat_sys_temp = target_temperature, #Das könnte problematisch werden
        yearly_heat_demand = yearly_heat_demand, full_load_hours = 2100)

tes = VPPThermalEnergyStorage(timebase, mass = mass_of_storage, 
                              hysteresis = hysteresis, 
                              target_temperature = target_temperature,
                              cp = cp, heatloss_per_day=heatloss_per_day,
                              userProfile = up)

chp = VPPCombinedHeatAndPower(environment = None, identifier='chp1', timebase=timebase, userProfile = up,
                 nominalPowerEl = nominalPowerEl, nominalPowerTh = nominalPowerTh, 
                 overall_efficiency = overall_efficiency, rampUpTime = rampUpTime, 
                 rampDownTime = rampDownTime, 
                 minimumRunningTime = minimumRunningTime, 
                 minimumStopTime = minimumStopTime)

#Formula: E = m * cp * T
df_component_values["therm_storage_capacity"] = tes.mass * tes.cp * (tes.target_temperature + tes.hysteresis + 273.15) #°K
df_component_values["thermal_storage_efficiency"] = 100 * (1 - tes.heatloss_per_day)

if scenario == 1:
    
    tes.userProfile.get_heat_demand()
    
    loadshape = tes.userProfile.get_heat_demand()[0:]["heat_demand"]
    outside_temp = tes.userProfile.mean_temp_hours.mean_temp
    log, log_load, log_el = [], [],[]
    chp.lastRampUp = chp.userProfile.heat_demand.index[0]
    chp.lastRampDown = chp.userProfile.heat_demand.index[0]
    for i in chp.userProfile.heat_demand.index:
        heat_demand = chp.userProfile.heat_demand.heat_demand.loc[i]
        if tes.get_needs_loading(): 
            chp.rampUp(i)              
        else: 
            chp.rampDown(i)
        temp = tes.operate_storage(heat_demand, i, chp)
        if chp.isRunning: 
            log_load.append(nominalPowerTh)
            log_el.append(nominalPowerEl)
        else: 
            log_load.append(0)
            log_el.append(0)
        log.append(temp)
    
    df_timeseries["chp_heat"] = pd.DataFrame(log_load, index = pd.date_range(start='2017', periods = 35040, freq=time_freq, name ='Time')).loc[start:end]
    df_timeseries["chp_el"] = pd.DataFrame(log_el, index = pd.date_range(start='2017', periods = 35040, freq=time_freq, name ='Time')).loc[start:end]
    
    df_timeseries.chp_heat.plot(figsize=figsize, label="chp gen[kW-therm]")
    df_timeseries.chp_el.plot(figsize=figsize, label="chp gen[kW-el]")

elif scenario == 2:
    
    df_component_values["chp_power_therm"] = chp.nominalPowerTh
    df_component_values["chp_power_el"] = chp.nominalPowerEl
    df_component_values["chp_efficiency"] = chp.overall_efficiency
    
else:
    print("chp scenario ", scenario, " is not defined!")
    
    
plt.legend()
print(df_component_values)

df_timeseries.to_csv("C:/Users/sbirk/Desktop/simulation/df_timeseries.csv")
df_component_values.to_csv("C:/Users/sbirk/Desktop/simulation/df_component_values.csv")