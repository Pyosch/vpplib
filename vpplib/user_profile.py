# -*- coding: utf-8 -*-
"""
Info
----
The class "UserProfile" reflects different patterns of use and behaviour.
This makes it possible, for example, to simulate different usage profiles of 
electric vehicles.

"""

import traceback
import pandas as pd
import os

class UserProfile(object):
    def __init__(
        self,
        identifier=None,
        latitude=None,
        longitude=None,
        thermal_energy_demand_yearly=None,
        mean_temp_days=None,
        mean_temp_hours=None,
        mean_temp_quarter_hours=None,
        building_type=None,  #'DE_HEF33'
        max_connection_power=None,
        comfort_factor=None,
        t_0=40,
    ):
        """
        Info
        ----
        This attributes can be used to derive profiles for different 
        components. 
        
        
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

        # For people that likes to have their homes quite warm
        self.comfort_factor = comfort_factor

        # Define the maximal connection power for a certain user
        self.max_connection_power = max_connection_power

        if mean_temp_days is None:
            self.mean_temp_days = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                        'input/thermal/dwd_temp_days_2015.csv').replace('\\', '/'),
                                            index_col='time')
            self.mean_temp_days.index = pd.to_datetime(self.mean_temp_days.index)
        else:
            self.mean_temp_days = mean_temp_days

        
        self.year = str(next(iter(self.mean_temp_days.index)))[:4]

        self.thermal_energy_demand = None

        # 'DE_HEF33', 'DE_HEF34', 'DE_HMF33', 'DE_HMF34', 'DE_GKO34'
        self.building_type = building_type
        # for cop
        if mean_temp_hours is None:
            self.mean_temp_hours = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(__file__)).replace('\\', '/'),
                "input/thermal/dwd_temp_hours_2015.csv"), index_col="time"
            )
            self.mean_temp_hours.index = pd.to_datetime(self.mean_temp_hours.index)
            
        else:
            self.mean_temp_hours = mean_temp_hours

        if mean_temp_quarter_hours is None:
            self.mean_temp_quarter_hours = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(__file__)).replace('\\', '/'),
                "input/thermal/dwd_temp_15min_2015.csv"), index_col="time"
            )
            self.mean_temp_quarter_hours.index = pd.to_datetime(
                self.mean_temp_quarter_hours.index
            )
        else:
            self.mean_temp_quarter_hours = mean_temp_quarter_hours
            

        self.demand_daily = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(__file__)).replace('\\', '/'),
                                                     "input/thermal/demand_daily.csv"))
        self.t_0 = t_0  # °C

        # for SigLinDe calculations
        self.SigLinDe = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(__file__)).replace('\\', '/'),
            "./input/thermal/SigLinDe.csv"), decimal=","
        )
        self.building_parameters = None
        self.h_del = None
        self.thermal_energy_demand_yearly = thermal_energy_demand_yearly
        self.thermal_energy_demand_daily = None
        self.consumerfactor = None


    def get_thermal_energy_demand(self):

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

        self.get_thermal_energy_demand_daily()

        self.get_consumerfactor()

        self.get_thermal_energy_demand_hourly()

        self.thermal_energy_demand = self.hour_to_quarter()

        return self.thermal_energy_demand

    # %%:
    # =========================================================================
    # Basic Functions for get_thermal_energy_demand
    # =========================================================================

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

                self.building_parameters = (
                    Sig.A,
                    Sig.B,
                    Sig.C,
                    Sig.D,
                    Sig.m_H,
                    Sig.b_H,
                    Sig.m_W,
                    Sig.b_W,
                )

                return self.building_parameters

    # %%:

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

        # Calculating the daily heat demand h_del for each day of the year
        h_lst = []

        for i, temp in self.mean_temp_days.iterrows():

            # H and W are for linearisation in SigLinDe function below 8°C
            H = m_H * temp.temperature + b_H
            W = m_W * temp.temperature + b_W
            if H > W:
                h_del = (
                    (A / (1 + ((B / (temp.temperature - self.t_0)) ** C))) + D
                ) + H
                h_lst.append(h_del)

            else:
                h_del = (
                    (A / (1 + ((B / (temp.temperature - self.t_0)) ** C))) + D
                ) + W
                h_lst.append(h_del)

        self.h_del = pd.DataFrame(
            h_lst, index=self.mean_temp_days.index, columns=["h_del"]
        )

        return self.h_del

    # %%:

    def get_thermal_energy_demand_daily(self):

        """
        Info
        ----
        distribute daily demand load over 24 hours according to the outside 
        temperature
        
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
        df = self.h_del.copy()
        df["Mean_Temp"] = self.mean_temp_days.temperature

        for i, d in df.iterrows():

            if d.Mean_Temp <= -15:
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x["Temp. <= -15 °C"]
                    demand_daily_lst.append(demand)

            elif (d.Mean_Temp > -15) & (d.Mean_Temp <= -10):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x["-15 °C < Temp. <= -10 °C"]
                    demand_daily_lst.append(demand)

            elif (d.Mean_Temp > -10) & (d.Mean_Temp <= -5):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x["-10 °C < Temp. <= -5 °C"]
                    demand_daily_lst.append(demand)

            elif (d.Mean_Temp > -5) & (d.Mean_Temp <= 0):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x["-5 °C < Temp. <= 0 °C"]
                    demand_daily_lst.append(demand)

            elif (d.Mean_Temp > 0) & (d.Mean_Temp <= 5):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x["0 °C < Temp. <= 5 °C"]
                    demand_daily_lst.append(demand)

            elif (d.Mean_Temp > 5) & (d.Mean_Temp <= 10):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x["5 °C < Temp. <= 10 °C"]
                    demand_daily_lst.append(demand)

            elif (d.Mean_Temp > 10) & (d.Mean_Temp <= 15):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x["10 °C < Temp. <= 15 °C"]
                    demand_daily_lst.append(demand)

            elif (d.Mean_Temp > 15) & (d.Mean_Temp <= 20):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x["15 °C < Temp. <= 20 °C"]
                    demand_daily_lst.append(demand)

            elif (d.Mean_Temp > 20) & (d.Mean_Temp <= 25):
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x["20 °C < Temp. <= 25 °C"]
                    demand_daily_lst.append(demand)

            elif d.Mean_Temp > 25:
                for i, x in self.demand_daily.iterrows():
                    demand = d.h_del * x["Temp > 25 °C"]
                    demand_daily_lst.append(demand)

            else:
                traceback.print_exc("df.mean_temp is out of bounds")

        self.thermal_energy_demand_daily = pd.DataFrame(
            demand_daily_lst,
            index=self.mean_temp_hours.index
        )

        return self.thermal_energy_demand_daily

    # %%:

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

        # consumerfactor (Kundenwert) K_w
        self.consumerfactor = self.thermal_energy_demand_yearly / (
            sum(self.h_del["h_del"])
        )
        return self.consumerfactor

    # %%:

    def get_thermal_energy_demand_hourly(self):

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

        self.thermal_energy_demand_hourly = (
            self.thermal_energy_demand_daily * self.consumerfactor
        )

        return self.thermal_energy_demand_hourly

    # %%:

    def hour_to_quarter(self):

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

        self.thermal_energy_demand = pd.DataFrame(
            index=self.mean_temp_quarter_hours.index
        )
        self.thermal_energy_demand[
            "thermal_energy_demand"
        ] = self.thermal_energy_demand_hourly
        self.thermal_energy_demand.interpolate(inplace=True)

        return self.thermal_energy_demand
