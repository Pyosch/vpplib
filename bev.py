# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 15:16:19 2018

@author: Sascha Birk
"""

#import rvpp.smart_home as smart_home
import pandas as pd
import random
import calendar

class BEV:
    
    def __init__(self, year, battery_max = 16, charging_power = 11 ):
        """
        Parameters
        ----------
        year: int
            year in which the simulation takes place
            
        battery_max: int
            maximal battery charge in kWh
            
        charging_power: int
            maximal charging power in kW
        
        Attributes
        ----------
        date_time_index: pandas.core.indexes.datetimes.DatetimeIndex
            DatetimeIndex with 15 Minutes frequency for one year set in 
            Parameters
            
        date: pandas.core.series.Series
            Series containing only the date from date_time_index
            
        hour: pandas.core.series.Series
            Series containing the hours from the date_time_index
            
        weekday: pandas.core.indexes.numeric.Int64Index
            integers from 0 to 6 for the days from Monday to Sunday
            
        at_home: pandas.core.frame.DataFrame
            DataFrame containing 1 if car is at home and 0 if not
        """
        
        if calendar.isleap(year):
            hoy = 8784
        else:
            hoy = 8760
        self.date_time_index = pd.date_range(pd.datetime(year, 1, 1, 0), 
                                             periods=hoy * 4, freq='15Min')
        self.date = []
        self.hour = []
        self.weekday = []
        self.at_home = []
        self.battery_max = battery_max 
        self.charging_power = charging_power
        

# In[Separate date and hours]:

    def split_time(self):
        
        #Add column with Hours to determine start and end of charging
        df = pd.DataFrame(self.date_time_index.astype(
                'str').str.split().tolist(), columns="date hour".split())
        self.date = df.date
        self.hour = df.hour

# In[Determine weekdays according to date time index]:
        
    def set_weekday(self):
        """
        Add weekday: 0 = Monday
        if 'Time' is already the index use : df['weekday'] = df.index.weekday
        """
#        self.weekday = pd.DataFrame({ "weekday" : self.date_time_index.weekday})
        self.weekday = self.date_time_index.weekday
        
    def get_weekday(self):
        return self.weekday
    

# In[Determine times when car is at home]:
    
    def set_at_home(self, work_start, work_end, weekend_trip_start, weekend_trip_end):
        
        """
        Determine the Times when the car is at home. During the week (weekday < 5) and on the weekend (weekday >= 5).
        Pick departure and arrival times from the preconfigured lists: work_start, work_end, weekend_trip_start, weekend_trip_end.
        (len(...)-1) is necessary because len() starts counting at 1 and randrange() starts indexing at 0.
        If the car is at home add 1 to the list. If not add 0 to the list
        """

        lst = []
    
        for hour, weekday in zip(self.hour, self.weekday):
                        
            if (hour == '00:00:00') & (weekday < 5):
                departure = work_start[random.randrange(0,(len(work_start) - 1),1)]
                arrival = work_end[random.randrange(0,(len(work_end) - 1),1)]
    
            elif (hour == '00:00:00') & (weekday >= 5):
                departure = weekend_trip_start[random.randrange(0,(len(weekend_trip_start) - 1),1)]
                arrival = weekend_trip_end[random.randrange(0,(len(weekend_trip_end) - 1),1)]
    
            if (hour > arrival) | (hour < departure):
                lst.append(1)
            else:
                lst.append(0) 
    
        self.at_home = pd.DataFrame({ "at home" : lst})


# In[Charge car when it is at home, discharge car when not at home]:
#
#def charge(df, battery_min, battery_max, charging_power, efficiency, battery_usage, time_base ):
#    
#    #Determine the charge of the car battery and the power drawn by the charger.
#    #The charger power will add to the el. demand of the house.
#    #For later implementation in the house model, consider 'grid friendly' charging
#    
#    battery_charge = (battery_min + battery_max)/2
#    lst_battery = []
#    lst_charger = []
#
#    for i, d in df.iterrows():
#        if (d.at_home == 0) & (battery_charge > battery_min):
#            #if car is not at home discharge battery with X kW/h
#            battery_charge = battery_charge - battery_usage * time_base 
#
#            if battery_charge < battery_min:
#                battery_charge = battery_min
#
#            lst_battery.append(battery_charge)
#            lst_charger.append(0) #if car is not at home, chargers energy consumption is 0
#
#        #If car is at home, charge with charging power. If timescale is hours charging power results in kWh    
#        elif (d.at_home == 1) & (battery_charge < battery_max): 
#            battery_charge = battery_charge + (charging_power * efficiency * time_base)
#            charger = charging_power
#
#            #If battery would be overcharged, charge only with kWh left
#            if battery_charge > battery_max:
#                charger = charging_power - (battery_charge - battery_max)
#                battery_charge = battery_max
#
#            lst_battery.append(battery_charge)
#            lst_charger.append(charger)
#
#        #If battery is full and car is at home, 
#        #charger consumes no power and current state of charge of battery is returned
#        else:
#            lst_battery.append(battery_charge)
#            lst_charger.append(0)
#
#    df['car_capacity'] = pd.DataFrame(lst_battery)
#    df['car_charger'] = pd.DataFrame(lst_charger)
#
#    return df
#
## In[Generate complete loadshape]:
#
#def loadshape(work_start, work_end, weekend_trip_start, weekend_trip_end, battery_min, battery_max, charging_power, efficiency, battery_usage, time_base = (15/60)):
#    
#    df = smart_home.new_scenario()
#    
#    df = split_time(df)
#    
#    df = at_home(df, work_start, work_end, weekend_trip_start, weekend_trip_end)
#    
#    df = charge(df, battery_min, battery_max, charging_power, efficiency, battery_usage, time_base )
#    
#    return df
#
## In[Daily demand, only needed for KI-Szenarios]:
#    
#def demand_daily(df, min_distance, max_distance, bev_consumption): #distances in km, consumption in kWh/100km
#    
#    demand_lst = []
#    date_lst = []
#    df_daily_demand = pd.DataFrame()
#    
#    for i, d in df.iterrows():
#        if (d.hour == '00:00:00'):
#            bev_demand = bev_consumption/100 * random.randrange(min_distance, max_distance)
#            
#            demand_lst.append(bev_demand)
#            date_lst.append(d.Date)
#            
#    df_daily_demand['Date'] = date_lst
#    df_daily_demand['Daily_Demand'] = demand_lst
#    
#    df_daily_demand.set_index(df_daily_demand.Date, inplace = True)
#    del df_daily_demand['Date']
#    
#    return df_daily_demand
# 
## In[Input for testing]:
#
##import matplotlib.pyplot as plt
##
###time_base = 1 #for hourly loadshapes
##time_base = 15/60 #for loadshapes with steps, smaller than one hour (eg. 15 minutes)
##
###Input electric vehicle
##bev_percentage = 0 #%
##
##efficiency = 0.98
##charging_power = 11 #kW
###battery_charge = 8 #starting state of charge in kWh
##battery_max = 20 #max capacity in kWh
##battery_min = 2 #min capacity in kWh
##battery_usage = 1 #kW, discharge car battery with battery_usage * time_base. Determines charge needed when returned home
##weekend_trip_start = ['08:00:00', '08:15:00', '08:30:00', '08:45:00', '09:00:00', '09:15:00','09:30:00','09:45:00',
##                      '10:00:00', '10:15:00', '10:30:00', '10:45:00', '11:00:00', '11:15:00', '11:30:00', '11:45:00', 
##                      '12:00:00', '12:15:00', '12:30:00', '12:45:00', '13:00:00']
##
##weekend_trip_end = ['17:00:00', '17:15:00', '17:30:00', '17:45:00', '18:00:00', '18:15:00', '18:30:00', '18:45:00', 
##                    '19:00:00', '19:15:00', '19:30:00', '19:45:00', '20:00:00', '20:15:00', '20:30:00', '20:45:00', 
##                    '21:00:00', '21:15:00', '21:30:00', '21:45:00', '22:00:00', '22:15:00', '22:30:00', '22:45:00', 
##                    '23:00:00']
##
##work_start = ['07:00:00', '07:15:00', '07:30:00', '07:45:00', '08:00:00', '08:15:00', '08:30:00', '08:45:00', 
##              '09:00:00']
##
##work_end = ['16:00:00', '16:15:00', '16:30:00', '16:45:00', 
##            '17:00:00', '17:15:00', '17:30:00', '17:45:00', '18:00:00', '18:15:00', '18:30:00', '18:45:00', 
##            '19:00:00', '19:15:00', '19:30:00', '19:45:00', '20:00:00', '20:15:00', '20:30:00', '20:45:00', 
##            '21:00:00', '21:15:00', '21:30:00', '21:45:00', '22:00:00']    
##
### In[Test]:
## 
##df = hp.new_scenario()
##df = split_time(df)
##df = at_home(df, work_start, work_end, weekend_trip_start, weekend_trip_end)
##df = charge(df, battery_min, battery_max, charging_power, efficiency, battery_usage )
##df.set_index(df.Time, inplace = True)
##del df["Time"]
##df.Car_Cap.head(100).plot()
##plt.show()
##
##print(df.head(100))
#
#