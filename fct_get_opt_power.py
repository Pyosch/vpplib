# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 15:44:03 2020

@author: andre

defining a function for determining the optimum power of a heat pump and
heating rod. criterion is the amount of hours per year, the heat demand can't
be delivered by the heat pump. for these hours the haeting rod has to deliver
the exceeding demand.
arguments passed are:
    - the amount of hours per year, the heating rod has to be activated
    - the user profile
    - the environment
    - the heatpump
    - the heating rod
"""

def get_opt_power(hours_exceeding_demand, user_profile, environment, heat_pump,
                  heating_rod):
    # heat demand
    df = user_profile.get_thermal_energy_demand()
    
    # sorted heat demand
    df_sorted = df.sort_values(by = 'thermal_energy_demand', ascending = False)
    
    #conversion hours to given timesteps
    conversion = 60 / environment.timebase
    
    pwr_heatpump = round(float(df_sorted.iloc[hours_exceeding_demand *
                                        int(conversion)].values), 1)
    
    heat_pump.th_power = pwr_heatpump
    
    exceeding_demand = round(float(df_sorted.iloc[0].values - pwr_heatpump), 1)
    
    heating_rod.el_power = exceeding_demand/heating_rod.efficiency
    
    print('Thermal power heat pump [kW]: ' + str(heat_pump.th_power))
    print('Electrical power heating rod [kW]: ' + str(heating_rod.el_power))