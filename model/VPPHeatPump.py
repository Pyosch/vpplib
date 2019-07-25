"""
Info
----
This file contains the basic functionalities of the VPPHeatPump class.

"""

import pandas as pd
import traceback
from .VPPComponent import VPPComponent


class VPPHeatPump(VPPComponent):
    
    def __init__(self, identifier, timebase = 1, heatpump_type = "Air", 
                 heat_sys_temp = 60, environment = None, userProfile = None, 
                 heatpump_power = 10.6, full_load_hours = 2100, heat_demand_year = None,
                 building_type = 'DE_HEF33', start = '2017-01-01 00:00:00',
                 end = '2017-12-31 23:45:00'):
        
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
        self.start = start
        self.end = end
        
        #heatpump parameters
        self.cop = None
        self.heatpump_type = heatpump_type
        self.heatpump_power = heatpump_power
        self.index_h = pd.DataFrame(pd.date_range(start, end, periods = None, freq = "H", name ='Time'))
        self.limit = 1
        
        #building parameters
        #TODO: export in seperate Building class
        mean_temp_days = pd.DataFrame(
                pd.date_range(start, end, freq="D", name = 'Time'))
        mean_temp_days['Mean_Temp'] = pd.read_csv(
                "./Input_House/heatpump_model/mean_temp_days_2017.csv", 
                header = None)
        
        self.heat_demand = None
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
        self.t_0 = 40 #°C
              
        
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
        #calculate the building parameters
        b_params = [] #[A, B, C, D, m_H, b_H, m_W, b_W]
        b_params = self.building_parameters(self.building_type, self.SigLinDe)
        
        h_de = self.h_del(self.mean_temp_days, b_params, self.t_0)
        
        heat_demand_daily = self.daily_demand(h_de, self.mean_temp_days.Mean_Temp, self.demand_daily)
        
        if self.heat_demand_year == None:
            Q_N = self.demandfactor(self.full_load_hours, self.heatpump_power)
            
        else:
            Q_N = self.heat_demand_year
            
        K_w = self.consumerfactor(Q_N, h_de)
        
        heat_demand_h = self.new_scenario(freq = "H")
        heat_demand_h.heat_demand = self.hourly_heat_demand(heat_demand_daily, K_w)
        
        heat_loadshape = self.hour_to_qarter(heat_demand_h, column = "heat_demand")
        
        self.heat_demand = heat_loadshape
        
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
            for i, tmp in self.mean_temp_hours.loc[self.start:self.end].iterrows():
                cop = (6.81 - 0.121 * (self.heat_sys_temp - tmp)
                       + 0.00063 * (self.heat_sys_temp - tmp)**2)
                cop_lst.append(cop)
        
        elif self.heatpump_type == "Ground":
            for i, tmp in self.mean_temp_hours.loc[self.start:self.end].iterrows():
                cop = (8.77 - 0.15 * (self.heat_sys_temp - tmp)
                       + 0.000734 * (self.heat_sys_temp - tmp)**2)
                cop_lst.append(cop)
        
        else:
            traceback.print_exc("Heatpump type is not defined!")
        
        self.cop = pd.DataFrame(data = cop_lst, index = self.index_h.Time)
        self.cop.columns = ['cop']
        
        return self.cop  
     
    #from VPPComponents
    def prepareTimeSeries(self):
        
        if self.cop == None:
            self.get_cop()
            
            
        if self.heat_demand == None:
            self.get_heat_demand()
            
        self.timeseries = self.heat_demand
        self.timeseries["cop"] = self.cop.cop
        self.timeseries.cop.interpolate(inplace = True)
        self.timeseries['el_demand'] = self.timeseries.heat_demand / self.timeseries.cop

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
        if type(timestamp) == int:
            
            heat_demand, cop , el_demand= self.timeseries.iloc[timestamp]
        
        elif type(timestamp) == str:
            
            heat_demand, cop , el_demand= self.timeseries.loc[timestamp]
        
        else:
            traceback.print_exc("timestamp needs to be of type int or string. Stringformat: YYYY-MM-DD hh:mm:ss")
        
        # TODO: cop would change if power of heatpump is limited. 
        # Dropping limiting factor for heatpumps
        
        observations = {'heat_demand':heat_demand, 'cop':cop, 'el_demand':el_demand}
        
        return observations


    # ===================================================================================
    # Basic Functions for Heatpump
    # ===================================================================================
    def new_scenario(self, periods = None, freq = "15 min", column = 'heat_demand'):
    
        df_main = pd.DataFrame(pd.date_range(self.start, self.end, periods, freq, name ='Time'))
        df_main[column] = 0
        
        return df_main
    
    #%%:
    def building_parameters(self, building_type, SigLinDe):
        
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
        
        for i, Sig in SigLinDe.iterrows():
            if Sig.Type == building_type:
    
                return(Sig.A, Sig.B, Sig.C, Sig.D, Sig.m_H, Sig.b_H, Sig.m_W, Sig.b_W)
         
    #%%:
                
    def h_del(self, mean_temp_days, b_params, t_0):
        
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
    
    #%%: 
        
    def daily_demand(self, h_del, Mean_Temp, demand_daily):
        
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
    

    #%%:
      
    def demandfactor(self, hours_year, heatpump_power,  thermal_power = 1, df_cop = 0):
        
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
    
    #%%:
    
    def consumerfactor(self, Q_N, h_del):
        
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
        
        #Consumerfactor (Kundenwert) K_w
        K_w = Q_N/(sum(h_del)) 
        return K_w
    
    #%%:
    
    def hourly_heat_demand(self, demand_daily, K_w):
        
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
        
        #demand_daily = float(demand_daily[0])
        
        heat_demand = demand_daily.astype(float) * K_w
        
        return pd.DataFrame(heat_demand)
    
   
    #%%:
        
    def hour_to_qarter(self, df_h, column = "heat_demand"):
        
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
        
        df_min = self.new_scenario(freq = "15 min")
        df_min.set_index(df_min.Time, inplace = True)
        
        df_h.set_index(df_h.Time, inplace = True)
        del df_min["Time"]
        df_min[column] = df_h["heat_demand"]
        df_min.interpolate(inplace = True)
    #    df_min.fillna(method='bfill',inplace = True)
        df_min.dropna(inplace = True)
        
        return df_min
