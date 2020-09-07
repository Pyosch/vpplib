# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 07:19:01 2020

@author: andre
"""
import pandas as pd

timeseries = pd.DataFrame(
        columns = ["temperature", "state_of_charge", "m_ice", "m_water"],
        index = pd.date_range(
                start = "2015-01-01 00:00:00",
                end = "2015-01-06 23:45:00",
                freq = "15 min",
                name = "time"
                )
        )
        
print(str(len(timeseries.index)))

for i in range(len(timeseries.index)):
    timeseries.temperature.iloc[i] = i
    timeseries.state_of_charge.iloc[i] = 2 * i
    timeseries.m_ice.iloc[i] = 3 * i
    timeseries.m_water.iloc[i] = 4 * i
    
print(timeseries)

max = timeseries.temperature.max()
i_20 = timeseries.temperature.iloc[20]

print(str(max))
print(str(i_20))
print(type(max))
print(type(i_20))