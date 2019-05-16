# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 10:18:08 2019

@author: Sascha Birk
"""

import heat
import matplotlib.pyplot as plt
import pandas as pd


start = '2017-01-01 00:00:00'
end = '2017-12-31 23:45:00'
periods = None
freq = "15 min"

df_index = pd.DataFrame(pd.date_range(start, end, periods, freq, name ='Time'))
#df_index = smart_home.new_scenario(column = 'weekday')

hp = heat.HeatPump(df_index)

hp.get_heat_demand()
hp.heat_demand.plot()
plt.show()

hp.get_cop()
hp.cop.plot()
plt.show()