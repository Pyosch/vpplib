# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 08:30:32 2020

@author: andre


"""
import pandas as pd

def optimize_bivalent(heat_pump, heating_rod, mode, user_profile):
    if mode not in ["parallel", "alternative"]:
        print("error: mode needs to be \"parallel\" or \"alternative\"")
        
# =============================================================================
#     if type(heat_pump) != HeatPump:
#         print("error: heat_pump needs to be of type HeatPump")
#         
#     if type(heating_rod) != HeatingRod:
#         print("error: heating_rod needs to be of type HeatingRod")
# =============================================================================
        
# =============================================================================
#     if user_profile.thermal_energy_demand == None:
#         user_profile.get_thermal_energy_demand()
# =============================================================================
    
    heat_demand = user_profile.get_thermal_energy_demand()
    temperature = pd.read_csv("./input/thermal/dwd_temp_15min_2015.csv", index_col="time")
    
    # get point p0 (lowest temperature and corresponding (highest) heat demand)
    T_p0 = round(float(temperature['temperature'].min()), 1)
    P_p0 = round(float(heat_demand['thermal_energy_demand'].max()), 1)
    
    # get point p1 (heatstop temperature and corrsponding (0kW) heat demand)
    T_p1 = 20   # choose reasonable value
    P_p1 = 0
    
    # assume linear function P(T)=a*T+b between p0 and p1
    # calculate parameter a: gradient triangle
    a = (P_p1 - P_p0) / (T_p1 - T_p0)
    
    # calculate parameter b: b=P(T)-a*T
    b = 0 - a * 20
    
    # bivalence temerature (determine with tabels in Vaillant hand book)
    T_biv = 0
    
    # calculate corresponding heat demand (equals thermal power of heat pump)
    P_biv = a * T_biv + b
    heat_pump.th_power = round(float(P_biv), 1)
    
    heat_pump.el_power = heat_pump.th_power / heat_pump.get_current_cop(T_biv)
    th_power_hp_coldest = heat_pump.el_power * heat_pump.get_current_cop(T_p0)
    
    if mode == "parallel":
        heating_rod.el_power = round(float((P_p0 - th_power_hp_coldest) / heating_rod.efficiency), 1)
        
    else:
        heating_rod.el_power = round(float(P_p0 / heating_rod.efficiency), 1)