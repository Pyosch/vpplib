# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 13:42:13 2018

@author: Sascha Birk
"""


import pandas as pd
import calendar
import demandlib.bdew as bdew


class Building:
    """        
    Parameters
    ----------
    
    
    Attributes
    ---------
    
    """
    
    def __init__(self, building_name, year = 2017):
        
        if calendar.isleap(year):
            hours = 8784
        else:
            hours = 8760
        self.date_time_index = pd.date_range(pd.datetime(year, 1, 1, 0), 
                                             periods=hours, freq='H')
        self.name = building_name
        self.heat = None
        self.heatdemand = None
        self.heat_storage = None
        
    def set_name(self, unit_name):
        self.name = unit_name
        
    def get_name(self):
        return self.name
    
    def set_heat(self, annual_heat_demand, mean_temp_hours, 
                       holidays = None, shlp_type='EFH'):
        
        self.heat = bdew.HeatBuilding(
                self.date_time_index, holidays = holidays, 
                temperature = mean_temp_hours, shlp_type = shlp_type,
                building_class = 1, wind_class = 1, 
                annual_heat_demand = annual_heat_demand, name = self.name)
        
    def get_heat(self):
        return self.heat
        
    def set_heatdemand(self):
        self.heatdemand = self.heat.get_bdew_profile()
        
    def get_heatdemand(self):
        return self.heatdemand
    
    def set_cop(self):
        self.cop = self.heat.get_cop()
        
    def get_cop(self):
        return self.cop
    
    