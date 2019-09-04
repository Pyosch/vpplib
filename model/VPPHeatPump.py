"""
Info
----
This file contains the basic functionalities of the VPPHeatPump class.

"""

import pandas as pd
import traceback
from .VPPComponent import VPPComponent

class VPPHeatPump(VPPComponent):
    
    def __init__(self, identifier, timebase, heatpump_type = "Air", 
                 heat_sys_temp = 60, t_0 = 40, environment = None, userProfile = None, 
                 heatpump_power = None, thermal_power = True, 
                 full_load_hours = None, heat_demand_year = None,
                 rampUpTime = 1, rampDownTime = 1, minimumRunningTime = 45, minimumStopTime = 45,
                 building_type = 'DE_HEF33', start = None, end = None, year = None):
        
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
        
        # Call to super class
        super(VPPHeatPump, self).__init__(timebase, environment, userProfile)
        
        # Configure attributes
        self.identifier = identifier
        self.timebase = timebase
        self.start = start
        self.end = end
        self.year = year
        
        #heatpump parameters
        self.cop = None
        self.heatpump_type = heatpump_type
        self.heatpump_power = heatpump_power
        self.thermal_power = thermal_power
        self.limit = 1
        
        #Ramp parameters
        self.rampUpTime = rampUpTime
        self.rampDownTime = rampDownTime
        self.minimumRunningTime = minimumRunningTime
        self.minimumStopTime = minimumStopTime
        self.lastRampUp = 0
        self.lastRampDown = 0
        
        #building parameters
        #TODO: export in seperate Building class
        mean_temp_days = pd.DataFrame(pd.date_range(start=self.year, periods=365, freq = "D", name="time"))
        mean_temp_days['Mean_Temp'] = pd.read_csv(
                "./Input_House/heatpump_model/mean_temp_days_2017.csv", 
                header = None)
        
        self.heat_demand = None
        self.timeseries_year = None
        self.timeseries = None
        self.building_type = building_type #'DE_HEF33', 'DE_HEF34', 'DE_HMF33', 'DE_HMF34', 'DE_GKO34'
        self.SigLinDe = pd.read_csv("./Input_House/heatpump_model/SigLinDe.csv", decimal=",")
        self.mean_temp_days = mean_temp_days
        self.mean_temp_hours = pd.read_csv(
                './Input_House/heatpump_model/mean_temp_hours_2017_indexed.csv', index_col="time")
        self.demand_daily = pd.read_csv(
                './Input_House/heatpump_model/demand_daily.csv')
        self.full_load_hours = full_load_hours #According to BDEW multi family homes: 2000, single family homes: 2100
        self.heat_demand_year = heat_demand_year
        self.heat_sys_temp = heat_sys_temp
        self.t_0 = t_0 #°C
        
        #for SigLinDe calculations
        self.building_parameters = None
        self.h_del = None
        self.heat_demand_daily = None
        self.demandfactor = None
        self.consumerfactor = None
        
        self.isRunning = False
              
        
    def get_heat_demand(self):
        
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
        
        self.get_building_parameters()
        
        self.get_h_del()
        
        self.get_heat_demand_daily()
        
        if self.heat_demand_year == None:
            self.get_demandfactor()
            
        else:
            self.demandfactor = self.heat_demand_year
            
        self.get_consumerfactor()
        
        self.get_hourly_heat_demand()
        
        self.heat_demand = self.hour_to_qarter()
        
        return self.heat_demand
            
    
    def get_cop(self):
        
        """
        Info
        ----
        Calculate COP of heatpump according to heatpump type
        
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
        
        cop_lst = []
        
        if self.heatpump_type == "Air":
            for i, tmp in self.mean_temp_hours.iterrows():
                cop = (6.81 - 0.121 * (self.heat_sys_temp - tmp)
                       + 0.00063 * (self.heat_sys_temp - tmp)**2)
                cop_lst.append(cop)
        
        elif self.heatpump_type == "Ground":
            for i, tmp in self.mean_temp_hours.iterrows():
                cop = (8.77 - 0.15 * (self.heat_sys_temp - tmp)
                       + 0.000734 * (self.heat_sys_temp - tmp)**2)
                cop_lst.append(cop)
        
        else:
            traceback.print_exc("Heatpump type is not defined!")
        
        self.cop = pd.DataFrame(data = cop_lst, index = pd.date_range(self.year, periods=8760, freq = "H", name="time"))
        self.cop.columns = ['cop']
        
        return self.cop  
    
    def get_current_cop(self, tmp):
        
        """
        Info
        ----
        Calculate COP of heatpump according to heatpump type
        
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
        
        
        if self.heatpump_type == "Air":
            cop = (6.81 - 0.121 * (self.heat_sys_temp - tmp)
                       + 0.00063 * (self.heat_sys_temp - tmp)**2)
        
        elif self.heatpump_type == "Ground":
            cop = (8.77 - 0.15 * (self.heat_sys_temp - tmp)
                       + 0.000734 * (self.heat_sys_temp - tmp)**2)
        
        else:
            print("Heatpump type is not defined")
            return -9999

        return cop
     
    #from VPPComponents
    def prepareTimeSeries(self):
        
        if self.cop == None:
            self.get_cop()
            
            
        if self.heat_demand == None:
            self.get_heat_demand()
            
        if self.timeseries_year == None:
            self.get_timeseries_year()
        
        self.timeseries = self.timeseries_year.loc[self.start:self.end]
        
        return self.timeseries
    
    def get_timeseries_year(self):
        
        self.timeseries_year = self.heat_demand
        self.timeseries_year["cop"] = self.cop#.cop
        self.timeseries_year.cop.interpolate(inplace = True)
        self.timeseries_year['el_demand'] = self.timeseries_year.heat_demand / self.timeseries_year.cop
        
        return self.timeseries_year

    # ===================================================================================
    # Controlling functions
    # ===================================================================================
    def limitPowerTo(self, limit):
        
        """
        Info
        ----
        This function limits the power of the heatpump to the given percentage.
        It cuts the current power production down to the peak power multiplied by
        the limit (Float [0;1]).
        
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

        # Validate input parameter
        if limit >= 0 and limit <= 1:

            # Parameter is valid
            self.limit = limit

        else:
        
            # Paramter is invalid
            return

    # ===================================================================================
    # Balancing Functions
    # ===================================================================================

    # Override balancing function from super class.
    def valueForTimestamp(self, timestamp):

        if type(timestamp) == int:
            
            return self.timeseries.el_demand.iloc[timestamp] * self.limit
        
        elif type(timestamp) == str:
            
            return self.timeseries.el_demand.loc[timestamp] * self.limit
        
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
        if self.timeseries != None:
            if type(timestamp) == int:
                
                heat_demand, cop , el_demand = self.timeseries.iloc[timestamp]
            
            elif type(timestamp) == str:
                
                heat_demand, cop , el_demand = self.timeseries.loc[timestamp]
            
            else:
                traceback.print_exc("timestamp needs to be of type int or string. Stringformat: YYYY-MM-DD hh:mm:ss")
            
            # TODO: cop would change if power of heatpump is limited. 
            # Dropping limiting factor for heatpumps
            
            observations = {'heat_demand':heat_demand, 'cop':cop, 'el_demand':el_demand}
        else:
            if type(timestamp) == int:
                

                if self.isRunning: 
                    el_demand = self.heatpump_power
                    temp = self.userProfile.mean_temp_quarter_hours.quart_temp.iloc[timestamp]
                    cop = self.get_current_cop(temp)                   
                    heat_output = el_demand * cop
                else: 
                    el_demand, cop, heat_output = 0, 0, 0
                    
            elif type(timestamp) == pd._libs.tslibs.timestamps.Timestamp:
                
                if self.isRunning: 
                    el_demand = self.heatpump_power
                    temp = self.userProfile.mean_temp_quarter_hours.quart_temp.loc[timestamp]
                    cop = self.get_current_cop(temp)                   
                    heat_output = el_demand * cop
                else: 
                    el_demand, cop, heat_output = 0, 0, 0
            
            else:
                traceback.print_exc("timestamp needs to be of type int or string. Stringformat: YYYY-MM-DD hh:mm:ss")
            observations = {'heat_output':heat_output, 'cop':cop, 'el_demand':el_demand}
        return observations


    #%%:
    # ===================================================================================
    # Basic Functions for Heatpump
    # ===================================================================================
    
    def get_building_parameters(self):
        
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
        
        for i, Sig in self.SigLinDe.iterrows():
            if Sig.Type == self.building_type:
                
                self.building_parameters=(Sig.A, Sig.B, Sig.C, Sig.D, Sig.m_H, Sig.b_H, Sig.m_W, Sig.b_W)
    
                return(Sig.A, Sig.B, Sig.C, Sig.D, Sig.m_H, Sig.b_H, Sig.m_W, Sig.b_W)
         
    #%%:
                
    def get_h_del(self):
        
        """
        Info
        ----
        Calculate the daily heat demand
        
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
        
        A, B, C, D, m_H, b_H, m_W, b_W = self.building_parameters
        
        #Calculating the daily heat demand h_del for each day of the year
        h_lst = []
        
    
        for i, temp in self.mean_temp_days.iterrows():
            
            #H and W are for linearisation in SigLinDe function below 8°C
            H = m_H * temp.Mean_Temp + b_H
            W = m_W * temp.Mean_Temp + b_W
            if H > W:
                h_del = ((A/(1+((B/(temp.Mean_Temp - self.t_0))**C))) + D) + H
                h_lst.append(h_del)
    
            else:
                h_del = ((A/(1+((B/(temp.Mean_Temp - self.t_0))**C))) + D) + W
                h_lst.append(h_del)
    
        df_h_del = pd.DataFrame(h_lst)
        self.h_del = df_h_del[0]
        
        return df_h_del[0]
    
    #%%: 
        
    def get_heat_demand_daily(self):
        
        """
        Info
        ----
        distribute daily demand load over 24 hours according to the outside temperature
        
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
        
        demand_daily_lst = []
        df = pd.DataFrame()
        df["h_del"] = self.h_del
        df["Mean_Temp"] = self.mean_temp_days.Mean_Temp
        
        for i, d in df.iterrows():
        
            if (d.Mean_Temp <= -15):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x['Temp. <= -15 °C']
                    demand_daily_lst.append(demand)
        
            elif ((d.Mean_Temp > -15) & (d.Mean_Temp <= -10)):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x['-15 °C < Temp. <= -10 °C']
                    demand_daily_lst.append(demand)
        
            elif ((d.Mean_Temp > -10) & (d.Mean_Temp <= -5)):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x['-10 °C < Temp. <= -5 °C']
                    demand_daily_lst.append(demand)
        
            elif ((d.Mean_Temp > -5) & (d.Mean_Temp <= 0)):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x['-5 °C < Temp. <= 0 °C']
                    demand_daily_lst.append(demand)
        
            elif ((d.Mean_Temp > 0) & (d.Mean_Temp <= 5)):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x['0 °C < Temp. <= 5 °C']
                    demand_daily_lst.append(demand)
        
            elif ((d.Mean_Temp > 5) & (d.Mean_Temp <= 10)):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x['5 °C < Temp. <= 10 °C']
                    demand_daily_lst.append(demand)
        
            elif ((d.Mean_Temp > 10) & (d.Mean_Temp <= 15)):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x['10 °C < Temp. <= 15 °C']
                    demand_daily_lst.append(demand)
        
            elif ((d.Mean_Temp > 15) & (d.Mean_Temp <= 20)):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x['15 °C < Temp. <= 20 °C']
                    demand_daily_lst.append(demand)
        
            elif ((d.Mean_Temp > 20) & (d.Mean_Temp <= 25)):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x['20 °C < Temp. <= 25 °C']
                    demand_daily_lst.append(demand)
        
            elif (d.Mean_Temp > 25):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x['Temp > 25 °C']
                    demand_daily_lst.append(demand)
        
            else:
                demand_daily_lst.append(-9999) #to see if something is wrong
            
        self.heat_demand_daily = pd.DataFrame(demand_daily_lst, index = pd.date_range(self.year, periods=8760, freq = "H", name="time"))
        
        return self.heat_demand_daily
    

    #%%:
      
    def get_demandfactor(self):
        
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
        
        if self.thermal_power:
            #Demandfactor (Verbrauchswert) Q_N 
            self.demandfactor = self.heatpump_power * self.full_load_hours #if heatpump_power is thermal power
    
        else:
            
            #seasonal performance factor (Jahresarbeitszahl) spf
            #needed if only el. power of heatpump is known 
            spf = sum(self.cop.cop)/len(self.cop.cop)
    
            #Demandfactor (Verbrauchswert) Q_N 
            self.demandfactor = self.heatpump_power * spf * self.full_load_hours #if heatpump_power is el. power
            
        return self.demandfactor
    
    #%%:
    
    def get_consumerfactor(self):
        
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
        
        #consumerfactor (Kundenwert) K_w
        self.consumerfactor = self.demandfactor/(sum(self.h_del)) 
        return self.consumerfactor
    
    #%%:
    
    def get_hourly_heat_demand(self):
        
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
        
        self.hourly_heat_demand = self.heat_demand_daily * self.consumerfactor
        
        return self.hourly_heat_demand
    
   
    #%%:
        
    def hour_to_qarter(self):
        
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
        
        self.heat_demand = pd.DataFrame(index = pd.date_range(self.year, periods=35040, freq='15min', name="time"))
        self.heat_demand["heat_demand"] = self.hourly_heat_demand
        self.heat_demand.interpolate(inplace = True)
        
        return self.heat_demand

    
    #%% ramping functions
    
    
    def isLegitRampUp(self, timestamp):
        
        if type(timestamp) == int:
            if timestamp - self.lastRampDown > self.minimumStopTime:
                self.isRunning = True
            else: self.isRunning = False
        
        elif type(timestamp) == pd._libs.tslibs.timestamps.Timestamp:
            if self.lastRampDown + self.minimumStopTime * timestamp.freq < timestamp:
                self.isRunning = True
            else: self.isRunning = False
            
        else:
            traceback.print_exc("timestamp needs to be of type int or pandas._libs.tslibs.timestamps.Timestamp")
        
    def isLegitRampDown(self, timestamp):
        
        if type(timestamp) == int:
            if timestamp - self.lastRampUp > self.minimumRunningTime:
                self.isRunning = False
            else: self.isRunning = True
        
        elif type(timestamp) == pd._libs.tslibs.timestamps.Timestamp:
            if self.lastRampUp + self.minimumRunningTime * timestamp.freq < timestamp:
                self.isRunning = False
            else: self.isRunning = True
            
        else:
            traceback.print_exc("timestamp needs to be of type int or pandas._libs.tslibs.timestamps.Timestamp")
        
    def rampUp(self, timestamp):
        
        """
        Info
        ----
        This function ramps up the combined heat and power plant. The timestamp is neccessary to calculate
        if the combined heat and power plant is running in later iterations of balancing. The possible
        return values are:
            - None:       Ramp up has no effect since the combined heat and power plant is already running
            - True:       Ramp up was successful
            - False:      Ramp up was not successful (due to constraints for minimum running and stop times)
        
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
        if self.isRunning:
            return None
        else:
            if self.isLegitRampUp(timestamp):
                self.isRunning = True
                return True
            else: 
                return False


    def rampDown(self, timestamp):
        
        """
        Info
        ----
        This function ramps down the combined heat and power plant. The timestamp is neccessary to calculate
        if the combined heat and power plant is running in later iterations of balancing. The possible
        return values are:
            - None:       Ramp down has no effect since the combined heat and power plant is not running
            - True:       Ramp down was successful
            - False:      Ramp down was not successful (due to constraints for minimum running and stop times)
        
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
    

        if not self.isRunning:
            return None
        else:
            if self.isLegitRampDown(timestamp):
                self.isRunning = False
                return True
            else: 
                return False
