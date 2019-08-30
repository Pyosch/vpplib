"""
Info
----
This file contains the basic functionalities of the VPPBEV class.

"""
from .VPPComponent import VPPComponent

import pandas as pd
import random
import traceback

class VPPBEV(VPPComponent):

    def __init__(self, timebase, identifier, start = None, end = None, time_freq = "15 min", battery_max = 16, 
                 battery_min = 0, battery_usage = 1, charging_power = 11, load_degradiation_begin = 0.8, 
                 chargeEfficiency = 0.98, environment=None, userProfile=None):

        # Call to super class
        super(VPPBEV, self).__init__(timebase=timebase, environment=environment, userProfile=userProfile)
        
        """
        Info
        ----
        ...
        
        Parameters
        ----------  
        battery_max: int
            maximal battery charge in kWh
            
        charging_power: int
            maximal charging power in kW
        
        Attributes
        ----------
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
        
        self.start = start
        self.end = end
        self.time_freq = time_freq
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
        self.load_degradiation_begin = load_degradiation_begin
        self.identifier = identifier
      
    def prepareTimeSeries(self):
        
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
        
        self.timeseries = pd.DataFrame(pd.date_range(start=self.start, end=self.end, 
                                             freq=self.time_freq, name ='Time'))
        self.timeseries['car_charger'] = 0
        self.timeseries.set_index(self.timeseries.Time, inplace = True)
        
        self.split_time() 
        self.set_weekday()
        self.set_at_home(work_start, work_end, weekend_trip_start, weekend_trip_end)
        self.charge()
        self.timeseries.set_index('Time', inplace = True, drop = True)
        self.timeseries['at_home'] = self.at_home
    
    
    # ===================================================================================
    # Controlling functions
    # ===================================================================================
    def charge(self):
        
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
        
        
        battery_charge = self.battery_max #initial state of charge at the first timestep
        lst_battery = []
        lst_charger = []
    
        for i, at_home in self.at_home.iterrows():
            if (at_home.item() == 0) & (battery_charge > self.battery_min):
                #if car is not at home discharge battery with X kW/h
                battery_charge = battery_charge - self.battery_usage * self.timebase 
    
                if battery_charge < self.battery_min:
                    battery_charge = self.battery_min
    
                lst_battery.append(battery_charge)
                lst_charger.append(0) #if car is not at home, chargers energy consumption is 0
            
            #Function to apply the load_degradation to the load profile
            elif (at_home.item() == 1) & (battery_charge > self.battery_max * self.load_degradiation_begin): 
                degraded_charging_power = self.charging_power * (1 - (battery_charge / self.battery_max - self.load_degradiation_begin)/(1 - self.load_degradiation_begin))
                battery_charge = battery_charge + (degraded_charging_power * self.chargeEfficiency * self.timebase)
                charger = degraded_charging_power
                
                if battery_charge > self.battery_max:
                    charger = self.charging_power - (battery_charge - self.battery_max)
                    battery_charge = self.battery_max
    
                lst_battery.append(battery_charge)
                lst_charger.append(charger)
    
            #If car is at home, charge with charging power. If timescale is hours charging power results in kWh    
            elif (at_home.item() == 1) & (battery_charge < self.battery_max): 
                battery_charge = battery_charge + (self.charging_power * self.chargeEfficiency * self.timebase)
                charger = self.charging_power
    
                #If battery would be overcharged, charge only with kWh left
                if battery_charge > self.battery_max:
                    charger = self.charging_power - (battery_charge - self.battery_max)
                    battery_charge = self.battery_max
    
                lst_battery.append(battery_charge)
                lst_charger.append(charger)
    
            #If battery is full and car is at home, 
            #charger consumes no power and current state of charge of battery is returned
            else:
                lst_battery.append(battery_charge)
                lst_charger.append(0)
    
        self.timeseries['car_capacity'] = lst_battery
        self.timeseries.car_charger = lst_charger
    

    # In[Separate date and hours]:

    def split_time(self):
        
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
        
        df = pd.DataFrame(self.timeseries.index.astype(
                'str').str.split().tolist(), columns="date hour".split())
        self.date = df.date
        self.date.index = self.timeseries.index
        self.hour = df.hour
        self.hour.index = self.timeseries.index
        

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
        self.weekday = self.timeseries.index.weekday
   

    # In[Determine times when car is at home]:
    
    def set_at_home(self, work_start, work_end, weekend_trip_start, weekend_trip_end):
        
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
    
        self.at_home = pd.DataFrame({ "at home" : lst})
        self.at_home.index = self.timeseries.index
        

    # ===================================================================================
    # Balancing Functions
    # ===================================================================================

    # Override balancing function from super class.
    def valueForTimestamp(self, timestamp):
        
        if type(timestamp) == int:
            
            return self.timeseries['car_charger'].iloc[timestamp] * self.limit
        
        elif type(timestamp) == str:
            
            return self.timeseries['car_charger'].loc[timestamp] * self.limit
        
        else:
            traceback.print_exc("timestamp needs to be of type int or string. Stringformat: YYYY-MM-DD hh:mm:ss")
        
        
    def observationsForTimestamp(self, timestamp):
        
        """
        Info
        ----
        This function takes a timestamp as the parameter and returns a 
        dictionary with key (String) value (Any) pairs. 
        Depending on the type of component, different status parameters of the 
        respective component can be queried. 
        
        For example, a power store can report its "State of Charge".
        Returns an empty dictionary since this function needs to be 
        implemented by child classes.
        
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
        if type(timestamp) == int:
            
            car_charger, car_capacity , at_home= self.timeseries.iloc[timestamp]
        
        elif type(timestamp) == str:
            
            car_charger, car_capacity , at_home= self.timeseries.loc[timestamp]
        
        else:
            traceback.print_exc("timestamp needs to be of type int or string. Stringformat: YYYY-MM-DD hh:mm:ss")
        
        observations = {'car_charger':car_charger, 'car_capacity':car_capacity, 'at_home':at_home}
        
        return observations