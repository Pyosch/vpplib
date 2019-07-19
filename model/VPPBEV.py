"""
Info
----
This file contains the basic functionalities of the VPPBEV class.

"""
from .VPPComponent import VPPComponent

import pandas as pd
import calendar
import random

class VPPBEV(VPPComponent):

    def __init__(self, timebase, identifier, year, battery_max = 16, 
                 battery_min = 0, battery_usage = 1, charging_power = 11, 
                 chargeEfficiency = 0.98, environment=None, userProfile=None):

        # Call to super class
        super(VPPBEV, self).__init__(timebase=timebase, environment=environment, userProfile=userProfile)
        
        """
        Info
        ----
        ...
        
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
        
        Notes
        -----
        
        ...
        
        References
        ----------
        
        ...
        
        Returns
        -------
        
        ...
        
        """
        
        if calendar.isleap(year):
            hoy = 8784
        else:
            hoy = 8760
        self.date_time_index = pd.date_range(pd.datetime(year, 1, 1, 0), 
                                             periods=hoy * 4, freq='15Min')
        self.timebase = timebase #time_base = 15/60 #for loadshapes with steps, smaller than one hour (eg. 15 minutes)
        self.limit = 1
        self.date = []
        self.hour = []
        self.weekday = []
        self.at_home = []
        self.battery_max = battery_max 
        self.battery_min = battery_min
        self.battery_usage = battery_usage
        self.charging_power = charging_power
        self.chargeEfficiency = chargeEfficiency
        self.set_weekday()
        self.identifier = identifier
      
    def prepareTimeSeries(self):
        
        self.timeseries = self.new_scenario(column = 'car_charger')
        
        #TODO: export to VPPUserProfile
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
        
        self.df = self.prepareBEVLoadshape(work_start, work_end, 
                                         weekend_trip_start, weekend_trip_end, 
                                         self.battery_min, self.battery_max, self.charging_power, 
                                         self.chargeEfficiency, self.battery_usage, self.timebase, self.timeseries)

    
    def prepareBEVLoadshape(self, work_start, work_end, weekend_trip_start, 
                            weekend_trip_end, battery_min, battery_max, 
                            charging_power, efficiency, battery_usage, 
                            time_base, df):
        
        """
        Info
        ----
        ...
        
        Parameters
        ----------
        
        ...
        	
        Attributes
        ----------
        
        ...
        
        Notes
        -----
        
        ...
        
        References
        ----------
        
        ...
        
        Returns
        -------
        
        ...
        
        """
    
        self.split_time(df)    
        df = self.set_at_home(df, work_start, work_end, weekend_trip_start, weekend_trip_end)
        df = self.charge(df, battery_min, battery_max, charging_power, efficiency, battery_usage, time_base)
        self.timeseries.set_index('Time', inplace = True, drop = True)
        
        return df


    def new_scenario(self, start = '2017-01-01 00:00:00', 
                     end = '2017-12-31 23:45:00', 
                     periods = None, freq = "15 min", column = 'Demand'):
    
        df_main = pd.DataFrame(pd.date_range(start, end, periods, freq, name ='Time'))
        df_main[column] = 0
        
        return df_main
    
    def loadshape(self, work_start, work_end, weekend_trip_start, 
                  weekend_trip_end, battery_min, battery_max, charging_power, 
                  efficiency, battery_usage, time_base = (15/60)):
        
        """
        Info
        ----
        ...
        
        Parameters
        ----------
        
        ...
        	
        Attributes
        ----------
        
        ...
        
        Notes
        -----
        
        ...
        
        References
        ----------
        
        ...
        
        Returns
        -------
        
        ...
        
        """
        
        df = self.new_scenario()
        df = self.split_time(df)
        df = self.at_home(df, work_start, work_end, weekend_trip_start, weekend_trip_end)
        df = self.charge(df, battery_min, battery_max, charging_power, efficiency, battery_usage, time_base )
        
        return df
    
    # ===================================================================================
    # Controlling functions
    # ===================================================================================
    def charge(self, df, battery_min, battery_max, charging_power, efficiency, 
               battery_usage, time_base ):
        
        """
        Info
        ----
        Determine the charge of the car battery and the power drawn by the charger.
        The charger power will add to the el. demand of the house.
        
        
        Parameters
        ----------
        
        ...
        	
        Attributes
        ----------
        
        ...
        
        Notes
        -----
        
        For later implementation consider 'grid friendly' charging
        
        References
        ----------
        
        ...
        
        Returns
        -------
        
        ...
        
        """
        
        load_degradiation_begin = 0.8
        battery_charge = battery_max #initial state of charge at the first timestep
        lst_battery = []
        lst_charger = []
    
        for i, d in df.iterrows():
            if (d.at_home == 0) & (battery_charge > battery_min):
                #if car is not at home discharge battery with X kW/h
                battery_charge = battery_charge - battery_usage * time_base 
    
                if battery_charge < battery_min:
                    battery_charge = battery_min
    
                lst_battery.append(battery_charge)
                lst_charger.append(0) #if car is not at home, chargers energy consumption is 0
            
            #Function to apply the load_degradation to the load profile
            elif (d.at_home == 1) & (battery_charge > battery_max * load_degradiation_begin): 
                degraded_charging_power = charging_power * (1 - (battery_charge / battery_max - load_degradiation_begin)/(1 - load_degradiation_begin))
                battery_charge = battery_charge + (degraded_charging_power * efficiency * time_base)
                charger = degraded_charging_power
                
                if battery_charge > battery_max:
                    charger = charging_power - (battery_charge - battery_max)
                    battery_charge = battery_max
    
                lst_battery.append(battery_charge)
                lst_charger.append(charger)
    
            #If car is at home, charge with charging power. If timescale is hours charging power results in kWh    
            elif (d.at_home == 1) & (battery_charge < battery_max): 
                battery_charge = battery_charge + (charging_power * efficiency * time_base)
                charger = charging_power
    
                #If battery would be overcharged, charge only with kWh left
                if battery_charge > battery_max:
                    charger = charging_power - (battery_charge - battery_max)
                    battery_charge = battery_max
    
                lst_battery.append(battery_charge)
                lst_charger.append(charger)
    
            #If battery is full and car is at home, 
            #charger consumes no power and current state of charge of battery is returned
            else:
                lst_battery.append(battery_charge)
                lst_charger.append(0)
    
        df['car_capacity'] = lst_battery
        df['car_charger'] = lst_charger
    
        return df

# In[Separate date and hours]:

    def split_time(self, df):
        
        """
        Info
        ----
        Add column with Hours to determine start and end of charging.
        
        Parameters
        ----------
        
        ...
        	
        Attributes
        ----------
        
        ...
        
        Notes
        -----
        
        ...
        
        References
        ----------
        
        ...
        
        Returns
        -------
        
        ...
        
        """
        
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
        """
        Info
        ----
        ...
        
        Parameters
        ----------
        
        ...
        	
        Attributes
        ----------
        
        ...
        
        Notes
        -----
        
        ...
        
        References
        ----------
        
        ...
        
        Returns
        -------
        
        ...
        
        """
        self.weekday = self.date_time_index.weekday
   

# In[Determine times when car is at home]:
    
    def set_at_home(self, df, work_start, work_end, weekend_trip_start, weekend_trip_end):
        
        """
        Info
        ----
        Determine the Times when the car is at home. During the week (weekday < 5) and on the weekend (weekday >= 5).
        Pick departure and arrival times from the preconfigured lists: work_start, work_end, weekend_trip_start, weekend_trip_end.
        (len(...)-1) is necessary because len() starts counting at 1 and randrange() starts indexing at 0.
        If the car is at home add 1 to the list. If not add 0 to the list
        
        Parameters
        ----------
        
        ...
        	
        Attributes
        ----------
        
        ...
        
        Notes
        -----
        
        ...
        
        References
        ----------
        
        ...
        
        Returns
        -------
        
        ...
        
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
    
        df["at_home"] = pd.DataFrame({ "at home" : lst})
        
        return df

    # ===================================================================================
    # Balancing Functions
    # ===================================================================================

    # Override balancing function from super class.
    def valueForTimestamp(self, timestamp):
        # -> Function stub <-
        
        if type(timestamp) == int:
            
            return self.timeseries['car_charger'][self.timeseries.index[timestamp]] * self.limit
        
        if type(timestamp) == str:
            
            return self.timeseries['car_charger'][timestamp] * self.limit
        
        else:
            return -9999
        
       # return self.timeseries.iloc[timestamp][3]
    
    