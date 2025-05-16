# -*- coding: utf-8 -*-
"""
User Profile Module
------------------
This module contains the UserProfile class which models different patterns of use and behavior
in a virtual power plant environment.

The UserProfile class provides functionality to generate thermal energy demand profiles
based on building characteristics, weather data, and user preferences. It can be used to
simulate different usage patterns for various components in the virtual power plant.
"""

import traceback
import pandas as pd
import os

class UserProfile(object):
    """
    A class representing a user profile with specific usage patterns and behaviors.
    
    The UserProfile class models the thermal energy demand of a building based on its
    characteristics, location, and user preferences. It implements the SigLinDe method
    (Sigmoid function for Linearized Demand) to calculate thermal energy demand profiles
    at different temporal resolutions (daily, hourly, quarter-hourly).
    
    Attributes
    ----------
    identifier : str, optional
        Unique identifier for the user profile
    latitude : float, optional
        Latitude of the building location
    longitude : float, optional
        Longitude of the building location
    comfort_factor : float, optional
        Factor representing user preference for thermal comfort (higher values indicate
        preference for warmer indoor temperatures)
    max_connection_power : float, optional
        Maximum electrical connection power available to the user in kW
    mean_temp_days : pandas.DataFrame
        Daily mean temperature data with datetime index
    mean_temp_hours : pandas.DataFrame
        Hourly mean temperature data with datetime index
    mean_temp_quarter_hours : pandas.DataFrame
        Quarter-hourly mean temperature data with datetime index
    year : str
        Year of the simulation data
    thermal_energy_demand : pandas.DataFrame
        Quarter-hourly thermal energy demand profile
    building_type : str, optional
        Type of building according to the SigLinDe classification (e.g., 'DE_HEF33')
    t_0 : float
        Reference temperature for SigLinDe calculations in °C (default: 40)
    building_parameters : tuple
        Parameters A, B, C, D, m_H, b_H, m_W, b_W from the SigLinDe model
    h_del : pandas.DataFrame
        Daily heat demand calculated using the SigLinDe method
    thermal_energy_demand_yearly : float, optional
        Annual thermal energy demand in kWh
    thermal_energy_demand_daily : pandas.DataFrame
        Daily thermal energy demand profile
    thermal_energy_demand_hourly : pandas.DataFrame
        Hourly thermal energy demand profile
    consumerfactor : float
        Scaling factor to adjust the calculated demand to match the annual demand
    """
    
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
        Initialize a UserProfile object.
        
        Parameters
        ----------
        identifier : str, optional
            Unique identifier for the user profile
        latitude : float, optional
            Latitude of the building location
        longitude : float, optional
            Longitude of the building location
        thermal_energy_demand_yearly : float, optional
            Annual thermal energy demand in kWh
        mean_temp_days : pandas.DataFrame, optional
            Daily mean temperature data with datetime index.
            If None, default data from input/thermal/dwd_temp_days_2015.csv is used.
        mean_temp_hours : pandas.DataFrame, optional
            Hourly mean temperature data with datetime index.
            If None, default data from input/thermal/dwd_temp_hours_2015.csv is used.
        mean_temp_quarter_hours : pandas.DataFrame, optional
            Quarter-hourly mean temperature data with datetime index.
            If None, default data from input/thermal/dwd_temp_15min_2015.csv is used.
        building_type : str, optional
            Type of building according to the SigLinDe classification
            (e.g., 'DE_HEF33', 'DE_HEF34', 'DE_HMF33', 'DE_HMF34', 'DE_GKO34')
        max_connection_power : float, optional
            Maximum electrical connection power available to the user in kW
        comfort_factor : float, optional
            Factor representing user preference for thermal comfort
        t_0 : float, optional
            Reference temperature for SigLinDe calculations in °C (default: 40)
            
        Notes
        -----
        If temperature data is not provided, the class will load default data from
        the input/thermal directory. The SigLinDe parameters are loaded from
        input/thermal/SigLinDe.csv.
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
        Calculate the thermal energy demand profile at quarter-hourly resolution.
        
        This method orchestrates the entire thermal energy demand calculation process
        by calling the necessary sub-methods in sequence:
        1. Get building parameters from the SigLinDe model
        2. Calculate daily heat demand (h_del)
        3. Distribute daily demand to hourly values based on temperature
        4. Calculate the consumer factor to scale the demand
        5. Apply the consumer factor to get hourly thermal energy demand
        6. Interpolate hourly values to quarter-hourly resolution
        
        Returns
        -------
        pandas.DataFrame
            Quarter-hourly thermal energy demand profile with datetime index
            and 'thermal_energy_demand' column in kWh
            
        Notes
        -----
        This is the main method to call when generating a thermal energy demand profile.
        The resulting profile can be used by thermal energy generators like heat pumps,
        heating rods, or combined heat and power units.
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
        Retrieve building parameters from the SigLinDe model based on building type.
        
        This method looks up the building parameters in the SigLinDe table based on
        the specified building_type. The parameters are used in the SigLinDe method
        to calculate the thermal energy demand.
        
        Returns
        -------
        tuple
            A tuple containing the SigLinDe parameters:
            - A, B, C, D: Parameters of the sigmoid function
            - m_H, b_H: Parameters for linearization below 8°C (heating)
            - m_W, b_W: Parameters for linearization below 8°C (hot water)
            
        Notes
        -----
        The SigLinDe model uses a sigmoid function with linearization for low
        temperatures to model the relationship between outdoor temperature and
        thermal energy demand.
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
        Calculate the daily heat demand using the SigLinDe method.
        
        This method applies the SigLinDe (Sigmoid function for Linearized Demand) method
        to calculate the daily heat demand based on daily mean temperatures. The SigLinDe
        method combines a sigmoid function with linearization for low temperatures.
        
        Returns
        -------
        pandas.DataFrame
            Daily heat demand with datetime index and 'h_del' column
            
        Notes
        -----
        The SigLinDe formula is:
        h_del = (A / (1 + ((B / (T - t_0)) ** C))) + D + max(H, W)
        
        where:
        - A, B, C, D are parameters of the sigmoid function
        - T is the daily mean temperature
        - t_0 is the reference temperature (default: 40°C)
        - H = m_H * T + b_H (linearization for heating at low temperatures)
        - W = m_W * T + b_W (linearization for hot water at low temperatures)
        
        References
        ----------
        Hellwig, M. (2003). Entwicklung und Anwendung parametrisierter Standard-Lastprofile.
        Dissertation, TU München.
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
        Distribute daily heat demand to hourly values based on temperature ranges.
        
        This method distributes the daily heat demand (h_del) to hourly values
        according to typical daily load profiles for different temperature ranges.
        The distribution patterns are loaded from the demand_daily.csv file, which
        contains hourly distribution factors for different temperature ranges.
        
        Returns
        -------
        pandas.DataFrame
            Hourly thermal energy demand with datetime index
            
        Notes
        -----
        The method uses different hourly distribution patterns depending on the
        daily mean temperature, with 10 different temperature ranges from below -15°C
        to above 25°C. For each temperature range, a specific hourly distribution
        pattern is applied to distribute the daily heat demand across the 24 hours
        of the day.
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
        Calculate the consumer factor to scale the thermal energy demand.
        
        The consumer factor (Kundenwert) is a scaling factor that adjusts the
        calculated thermal energy demand to match the specified annual demand.
        It is calculated as the ratio of the specified annual thermal energy
        demand to the sum of the calculated daily heat demands.
        
        Returns
        -------
        float
            The consumer factor (scaling factor)
            
        Notes
        -----
        The consumer factor accounts for building-specific characteristics that
        are not captured by the standard SigLinDe model, such as building size,
        insulation quality, and user behavior.
        """
        # consumerfactor (Kundenwert) K_w
        self.consumerfactor = self.thermal_energy_demand_yearly / (
            sum(self.h_del["h_del"])
        )
        return self.consumerfactor

    # %%:

    def get_thermal_energy_demand_hourly(self):
        """
        Apply the consumer factor to get the hourly thermal energy demand.
        
        This method scales the hourly thermal energy demand values by multiplying
        them with the consumer factor to match the specified annual demand.
        
        Returns
        -------
        pandas.DataFrame
            Hourly thermal energy demand with datetime index, scaled by the consumer factor
            
        Notes
        -----
        This step ensures that the total annual thermal energy demand matches the
        specified value while preserving the temporal patterns determined by the
        SigLinDe method and the hourly distribution factors.
        """
        self.thermal_energy_demand_hourly = (
            self.thermal_energy_demand_daily * self.consumerfactor
        )

        return self.thermal_energy_demand_hourly

    # %%:

    def hour_to_quarter(self):
        """
        Convert hourly thermal energy demand to quarter-hourly resolution.
        
        This method creates a quarter-hourly thermal energy demand profile by
        assigning the hourly values to the corresponding quarter-hourly timestamps
        and then interpolating to fill in the missing values.
        
        Returns
        -------
        pandas.DataFrame
            Quarter-hourly thermal energy demand with datetime index and
            'thermal_energy_demand' column
            
        Notes
        -----
        The interpolation is performed using pandas' interpolate method, which
        by default uses linear interpolation. This creates a smoother profile
        that better represents the continuous nature of thermal energy demand.
        """
        self.thermal_energy_demand = pd.DataFrame(
            index=self.mean_temp_quarter_hours.index
        )
        self.thermal_energy_demand[
            "thermal_energy_demand"
        ] = self.thermal_energy_demand_hourly
        self.thermal_energy_demand.interpolate(inplace=True)

        return self.thermal_energy_demand
