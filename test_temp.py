# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 14:01:39 2020

@author: andre
"""

import pandas as pd

temps = pd.read_csv("./input/thermal/dwd_temp_15min_2015.csv",
                         index_col="time"
                         )
temps.plot()
