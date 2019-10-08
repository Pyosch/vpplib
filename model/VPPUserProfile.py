"""
Info
----
The class "VPPUserProfile" reflects different patterns of use and behaviour. 
This makes it possible, for example, to simulate different usage profiles of 
electric vehicles.

TODO: Collect information about parameters that must be represented in a use case.
"""

import traceback
import pandas as pd

class VPPUserProfile(object):

    def __init__(self, identifier=None,
                 latitude = None,
                 longitude = None,
                 yearly_heat_demand = 12500,
                 building_type = 'DE_HEF33',
                 daily_vehicle_usage = None,
                 comfort_factor = None,
                 t_0 = 40, year = '2017'):
        """
        Info
        ----
        This attributes can be used to derive profiles for different components. 
        The BEV for example will probably care more about the daily vehicle usage, than the comfort factor. 
        The heat pump will probably not care about the daily vehicle usage at all (and so on).
        
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

        
        self.identifier = identifier
        self.latitude = latitude
        self.longitude = longitude
        self.year = year
        
        self.daily_vehicle_usage = daily_vehicle_usage    # km
        self.comfort_factor = comfort_factor        # For people that likes to have their homes quite warm 
        
        mean_temp_days = pd.DataFrame(pd.date_range(self.year, periods=365, freq = "D", name="time"))
        mean_temp_days['Mean_Temp'] = pd.read_csv(
                "./Input_House/heatpump_model/mean_temp_days_2017.csv", 
                header = None)
        self.mean_temp_days = mean_temp_days
        self.heat_demand = None
        
        self.building_type = building_type #'DE_HEF33', 'DE_HEF34', 'DE_HMF33', 'DE_HMF34', 'DE_GKO34'
        self.mean_temp_hours = pd.read_csv(
                './Input_House/heatpump_model/mean_temp_hours_2017_indexed.csv', index_col="time") #for cop
        self.mean_temp_quarter_hours = self.temp_hour_to_qarter()
        self.demand_daily = pd.read_csv(
                './Input_House/heatpump_model/demand_daily.csv')
        self.t_0 = t_0 #°C
        
        #for SigLinDe calculations
        self.SigLinDe = pd.read_csv("./Input_House/heatpump_model/SigLinDe.csv", decimal=",")
        self.building_parameters = None
        self.h_del = None
        self.yearly_heat_demand = yearly_heat_demand
        self.heat_demand_daily = None
        self.consumerfactor = None
              
        
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
            
        self.get_consumerfactor()
        
        self.get_hourly_heat_demand()
        
        self.heat_demand = self.hour_to_qarter()
        
        return self.heat_demand
    
    #%%:
    # ===================================================================================
    # Basic Functions for heat demand
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
                
                self.building_parameters=(Sig.A, Sig.B, Sig.C, Sig.D, Sig.m_H, 
                                          Sig.b_H, Sig.m_W, Sig.b_W)
    
                return self.building_parameters
         
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
                traceback.print_exc("df.mean_temp is out of bounds")
            
        self.heat_demand_daily = pd.DataFrame(demand_daily_lst, index = pd.date_range(self.year, periods=8760, freq = "H", name="time"))
        
        return self.heat_demand_daily
    
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
        self.consumerfactor = self.yearly_heat_demand/(sum(self.h_del)) 
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
    #%%:
        
    def temp_hour_to_qarter(self):
        
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
        
        df = pd.DataFrame(index = pd.date_range(self.year, periods=35040, freq='15min', name="time"))
        self.mean_temp_hours.index = pd.to_datetime(self.mean_temp_hours.index)
        df["quart_temp"] = self.mean_temp_hours
        df.interpolate(inplace = True)
        
        return df