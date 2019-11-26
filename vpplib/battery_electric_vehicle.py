"""
Info
----
This file contains the basic functionalities of the BatteryElectricVehicle class.

"""
from .component import Component

import pandas as pd
import random


class BatteryElectricVehicle(Component):

    def __init__(self, battery_max, battery_min, battery_usage,
                 charging_power, load_degradation_begin,
                 charge_efficiency, unit, identifier=None,
                 environment=None, user_profile=None, cost=None):

        # Call to super class
        super(BatteryElectricVehicle, self).__init__(unit, environment, user_profile, cost)
        
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

        self.limit = 1
        self.date = []
        self.hour = []
        self.weekday = []
        self.at_home = []
        self.battery_max = battery_max 
        self.battery_min = battery_min
        self.battery_usage = battery_usage
        self.charging_power = charging_power
        self.charge_efficiency = charge_efficiency
        self.load_degradation_begin = load_degradation_begin
        self.identifier = identifier
      
    def prepare_time_series(self):
        
        self.timeseries = pd.DataFrame(pd.date_range(start=self.environment.start, 
                                                     end=self.environment.end,
                                                     freq=self.environment.time_freq, name='Time'))
        self.timeseries['car_charger'] = 0
        self.timeseries.set_index(self.timeseries.Time, inplace=True)
        
        self.split_time()
        self.set_weekday()
        self.set_at_home()
        self.charge()
        self.timeseries.set_index('Time', inplace = True, drop = True)
        self.timeseries['at_home'] = self.at_home

    def reset_time_series(self):
        
        self.timeseries = None
        
        return self.timeseries
    
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

        battery_charge = self.battery_max  # initial state of charge at the first timestep
        lst_battery = []
        lst_charger = []
    
        for i, at_home in self.at_home.iterrows():
            if (at_home.item() == 0) & (battery_charge > self.battery_min):
                #if car is not at home discharge battery with X kW/h
                battery_charge = battery_charge - self.battery_usage * (self.environment.timebase/60) 
    
                if battery_charge < self.battery_min:
                    battery_charge = self.battery_min
    
                lst_battery.append(battery_charge)
                lst_charger.append(0) #if car is not at home, chargers energy consumption is 0
            
            #Function to apply the load_degradation to the load profile
            elif (at_home.item() == 1) & (battery_charge > self.battery_max * self.load_degradation_begin):
                degraded_charging_power = (self.charging_power *
                                           (1 - (battery_charge /
                                                 self.battery_max -
                                                 self.load_degradation_begin) / (1 - self.load_degradation_begin)))
                
                battery_charge = battery_charge + (degraded_charging_power * 
                                                   self.charge_efficiency * 
                                                   (self.environment.timebase/60))
                charger = degraded_charging_power
                
                if battery_charge > self.battery_max:
                    charger = self.charging_power - (battery_charge - self.battery_max)
                    battery_charge = self.battery_max
    
                lst_battery.append(battery_charge)
                lst_charger.append(charger)
    
            #If car is at home, charge with charging power. If timescale is hours charging power results in kWh    
            elif (at_home.item() == 1) & (battery_charge < self.battery_max): 
                battery_charge = battery_charge + (self.charging_power * 
                                                   self.charge_efficiency * 
                                                   (self.environment.timebase/60))
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
    
    def set_at_home(self):
        
        """
        Info
        ----
        Determine the Times when the car is at home. 
        During the week (weekday < 5) and on the weekend (weekday >= 5).
        Pick departure and arrival times from the preconfigured lists: 
            work_start, work_end, weekend_trip_start, weekend_trip_end.
        (len(...)-1) is necessary because len() starts counting at 1 and 
        randrange() starts indexing at 0.
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
        
        if (len(self.user_profile.week_trip_start) == 0 or
            len(self.user_profile.week_trip_end) == 0 or
            len(self.user_profile.weekend_trip_start) == 0 or
            len(self.user_profile.weekend_trip_end) == 0):
            self.user_profile.get_trip_times()

        lst = []
    
        for hour, weekday in zip(self.hour, self.weekday):
            if (hour == '00:00:00') & (weekday < 5):
                departure = self.user_profile.week_trip_start[
                        random.randrange(0,(len(
                                self.user_profile.week_trip_start) - 1),1)]
                        
                arrival = self.user_profile.week_trip_end[
                        random.randrange(0,(len(
                                self.user_profile.week_trip_end) - 1),1)]
    
            elif (hour == '00:00:00') & (weekday >= 5):
                departure = self.user_profile.weekend_trip_start[
                        random.randrange(0,(len(
                                self.user_profile.weekend_trip_start) - 1),1)]
                        
                arrival = self.user_profile.weekend_trip_end[
                        random.randrange(0,(len(
                                self.user_profile.weekend_trip_end) - 1),1)]
    
            if (hour > arrival) | (hour < departure):
                lst.append(1)
            else:
                lst.append(0) 
    
        self.at_home = pd.DataFrame({ "at home" : lst})
        self.at_home.index = self.timeseries.index

    # =========================================================================
    # Balancing Functions
    # =========================================================================

    # Override balancing function from super class.
    def value_for_timestamp(self, timestamp):
        
        if type(timestamp) == int:
            
            return self.timeseries['car_charger'].iloc[timestamp] * self.limit
        
        elif type(timestamp) == str:
            
            return self.timeseries['car_charger'].loc[timestamp] * self.limit
        
        else:
            raise ValueError("timestamp needs to be of type int or string. " +
                             "Stringformat: YYYY-MM-DD hh:mm:ss")

    def observations_for_timestamp(self, timestamp):
        
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
            raise ValueError("timestamp needs to be of type int or string. " +
                             "Stringformat: YYYY-MM-DD hh:mm:ss")
        
        observations = {'car_charger':car_charger, 
                        'car_capacity':car_capacity, 
                        'at_home':at_home}
        
        return observations