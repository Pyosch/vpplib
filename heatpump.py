# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 17:05:20 2018

@author: Sascha Birk
"""
import pandas as pd
import smart_home as smart_home



# In[2]:
def building_parameters(building_type, SigLinDe):
    

    for i, Sig in SigLinDe.iterrows():
        if Sig.Type == building_type:

            return(Sig.A, Sig.B, Sig.C, Sig.D, Sig.m_H, Sig.b_H, Sig.m_W, Sig.b_W)
     
# In[3]:
#Calculate the daily heat demand
            
def h_del(mean_temp_days, b_params, t_0):
    
    A, B, C, D, m_H, b_H, m_W, b_W = b_params
    
    #Calculating the daily heat demand h_del for each day of the year
    h_lst = []
    

    for i, temp in mean_temp_days.iterrows():
        
        #H and W are for linearisation in SigLinDe function below 8°C
        H = m_H * temp.Mean_Temp + b_H
        W = m_W * temp.Mean_Temp + b_W
        if H > W:
            h_del = ((A/(1+((B/(temp.Mean_Temp - t_0))**C))) + D) + H
            h_lst.append(h_del)

        else:
            h_del = ((A/(1+((B/(temp.Mean_Temp - t_0))**C))) + D) + W
            h_lst.append(h_del)

    df_h_del = pd.DataFrame(h_lst)
    return df_h_del[0]

# In[4]: 
#distribute daily demand load over 24 hours according to the outside temperature
    
def daily_demand(h_del, Mean_Temp, demand_daily):
    
    demand_daily_lst = []
    df = pd.DataFrame()
    df["h_del"] = h_del
    df["Mean_Temp"] = Mean_Temp
    
    for i, d in df.iterrows():
    
        if (d.Mean_Temp <= -15):
            for i, x in demand_daily.iterrows():
                demand = d.h_del * x['Temp. <= -15 °C']
                demand_daily_lst.append(demand)
    
        elif ((d.Mean_Temp > -15) & (d.Mean_Temp <= -10)):
            for i, x in demand_daily.iterrows():
                demand = d.h_del * x['-15 °C < Temp. <= -10 °C']
                demand_daily_lst.append(demand)
    
        elif ((d.Mean_Temp > -10) & (d.Mean_Temp <= -5)):
            for i, x in demand_daily.iterrows():
                demand = d.h_del * x['-10 °C < Temp. <= -5 °C']
                demand_daily_lst.append(demand)
    
        elif ((d.Mean_Temp > -5) & (d.Mean_Temp <= 0)):
            for i, x in demand_daily.iterrows():
                demand = d.h_del * x['-5 °C < Temp. <= 0 °C']
                demand_daily_lst.append(demand)
    
        elif ((d.Mean_Temp > 0) & (d.Mean_Temp <= 5)):
            for i, x in demand_daily.iterrows():
                demand = d.h_del * x['0 °C < Temp. <= 5 °C']
                demand_daily_lst.append(demand)
    
        elif ((d.Mean_Temp > 5) & (d.Mean_Temp <= 10)):
            for i, x in demand_daily.iterrows():
                demand = d.h_del * x['5 °C < Temp. <= 10 °C']
                demand_daily_lst.append(demand)
    
        elif ((d.Mean_Temp > 10) & (d.Mean_Temp <= 15)):
            for i, x in demand_daily.iterrows():
                demand = d.h_del * x['10 °C < Temp. <= 15 °C']
                demand_daily_lst.append(demand)
    
        elif ((d.Mean_Temp > 15) & (d.Mean_Temp <= 20)):
            for i, x in demand_daily.iterrows():
                demand = d.h_del * x['15 °C < Temp. <= 20 °C']
                demand_daily_lst.append(demand)
    
        elif ((d.Mean_Temp > 20) & (d.Mean_Temp <= 25)):
            for i, x in demand_daily.iterrows():
                demand = d.h_del * x['20 °C < Temp. <= 25 °C']
                demand_daily_lst.append(demand)
    
        elif (d.Mean_Temp > 25):
            for i, x in demand_daily.iterrows():
                demand = d.h_del * x['Temp > 25 °C']
                demand_daily_lst.append(demand)
    
        else:
            demand_daily_lst.append(-9999) #to see if something is wrong
        
    return pd.DataFrame(demand_daily_lst)

# In[5]:   
#Calculate COP of heatpump according to heatpump type

def cop(mean_temp_hours, heatpump_type = "Air", water_temp = 60):
    
    cop_lst = []
    
    if heatpump_type == "Air":
        for i, tmp in mean_temp_hours.iterrows():
            cop = (6.81 - 0.121 * (water_temp - tmp)
                   + 0.00063 * (water_temp - tmp)**2)
            cop_lst.append(cop)
    
    elif heatpump_type == "Ground":
        for i, tmp in mean_temp_hours.iterrows():
            cop = (8.77 - 0.15 * (water_temp - tmp)
                   + 0.000734 * (water_temp - tmp)**2)
            cop_lst.append(cop)
    
    else:
        print("Heatpump type is not defined")
        return -9999

    df_cop = pd.DataFrame(cop_lst)
    return df_cop

# In[6]:
  
def demandfactor(hours_year, heatpump_power,  thermal_power = 1, df_cop = 0):
    
    if thermal_power:
        #Demandfactor (Verbrauchswert) Q_N 
        Q_N = heatpump_power * hours_year #if heatpump_power is thermal power

    else:
        
        #seasonal performance factor (Jahresarbeitszahl) spf
        #needed if only el. power of heatpump is known 
        spf = sum(df_cop[0])/len(df_cop[0])

        #Demandfactor (Verbrauchswert) Q_N 
        Q_N = heatpump_power * spf * hours_year #if heatpump_power is el. power
        
    return Q_N

# In[7]:

def consumerfactor(Q_N, h_del):
    
    #Consumerfactor (Kundenwert) K_w
    K_w = Q_N/(sum(h_del)) 
    return K_w

# In[8]:

def hourly_heat_demand(demand_daily, K_w):
    
    #demand_daily = float(demand_daily[0])
    
    heat_demand = demand_daily.astype(float) * K_w
    return pd.DataFrame(heat_demand)

# In[9]:

def hourly_el_demand(heat_demand, df_cop):
    
    el_demand = heat_demand / df_cop
    return pd.DataFrame(el_demand)

# In[10]:
    
def hour_to_qarter(df_h, column = "Demand"):
    
    df_min = smart_home.new_scenario(freq = "15 min")
    df_min.set_index(df_min.Time, inplace = True)
    
    df_h.set_index(df_h.Time, inplace = True)
    del df_min["Time"]
    df_min[column] = df_h["Demand"]
    df_min.interpolate(inplace = True)
#    df_min.fillna(method='bfill',inplace = True)
    df_min.dropna(inplace = True)
    return df_min

# In[heat demand for KI-Szenario]:
    
def heat_loadshape(building_type, SigLinDe, mean_temp_days, t_0, demand_daily, mean_temp_hours, heatpump_type, water_temp, hours_year, heatpump_power):
    #calculate the building parameters
    b_params = [] #[A, B, C, D, m_H, b_H, m_W, b_W]
    b_params = building_parameters(building_type, SigLinDe)
    
    h_de = h_del(mean_temp_days, b_params, t_0)
    
    heat_demand_daily = daily_demand(h_de, mean_temp_days.Mean_Temp, demand_daily)
    
    Q_N = demandfactor(hours_year, heatpump_power)
        
    K_w = consumerfactor(Q_N, h_de)
    
    heat_demand_h = smart_home.new_scenario(freq = "H")
    heat_demand_h.Demand = hourly_heat_demand(heat_demand_daily, K_w)
    
    heat_loadshape = hour_to_qarter(heat_demand_h, column = "Demand")
    
    return heat_loadshape
    

# In[Complete loadshape]:
# For testing purposes. Use smart_home.hp_loadshape instead
    
#import heatpump as heatpump
#def loadshape(building_type, SigLinDe, mean_temp_days, t_0, demand_daily, mean_temp_hours, heatpump_type, water_temp, hours_year, heatpump_power):
#    #calculate the building parameters
#    b_params = [] #[A, B, C, D, m_H, b_H, m_W, b_W]
#    b_params = heatpump.building_parameters(building_type, SigLinDe)
#    
#    h_del = heatpump.h_del(mean_temp_days, b_params, t_0)
#    
#    heat_demand_daily = heatpump.daily_demand(h_del, mean_temp_days.Mean_Temp, demand_daily)
#        
#    df_cop = heatpump.cop(mean_temp_hours, heatpump_type, water_temp)
#    
#    Q_N = heatpump.demandfactor(hours_year, heatpump_power)
#        
#    K_w = heatpump.consumerfactor(Q_N, h_del)
#    
#    heat_demand_h = heatpump.hourly_heat_demand(heat_demand_daily, K_w)
#    
#    el_demand_h = heatpump.hourly_el_demand(heat_demand_h, df_cop)
#    el_demand_h.dropna(inplace = True)
#    
#    df_h = heatpump.new_scenario(freq = "H")
#    df_h["Demand"] = el_demand_h
#    df_h.dropna(inplace = True)
#    
#    hp_loadshape = heatpump.hour_to_qarter(df_h)
#    return hp_loadshape