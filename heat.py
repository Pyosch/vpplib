# -*- coding: utf-8 -*-
import pandas as pd
import demandlib.bdew as bdew
import heatpump
from Model.VPPComponent import VPPComponent


class HeatPump(VPPComponent):
    
    def __init__(self, identifier, df_index, timebase = 1, heatpump_type = "Air", 
                 heat_sys_temp = 60, environment = None, useCase = None, 
                 heatpump_power = 10.6, full_load_hours = 2100, 
                 building_type = 'DE_HEF33', start = '2017-01-01 00:00:00',
                 end = '2017-12-31 23:45:00'):
        
        # Call to super class
        super(HeatPump, self).__init__(timebase, environment, useCase)
        
        # Configure attributes
        self.identifier = identifier
        
        #heatpump parameters
        self.cop = None
        self.heatpump_type = heatpump_type
        self.heatpump_power = heatpump_power
        self.index_h = pd.DataFrame(pd.date_range(start, end, periods = None, freq = "H", name ='Time'))
        

        
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
                './Input_House/heatpump_model/mean_temp_hours_2017.csv', 
                header = None)
        self.demand_daily = pd.read_csv(
                './Input_House/heatpump_model/demand_daily.csv')
        self.full_load_hours = full_load_hours #According to BDEW multi family homes: 2000, single family homes: 2100
        self.heat_sys_temp = heat_sys_temp
        self.t_0 = 40 #°C
        
        
        
    def get_heat_demand(self):
        
        self.heat_demand = heatpump.heat_loadshape(self.building_type,
                                                   self.SigLinDe,
                                                   self.mean_temp_days, 
                                                   self.t_0, 
                                                   self.demand_daily, 
                                                   self.mean_temp_hours, 
                                                   self.heatpump_type, 
                                                   self.heat_sys_temp, #water_temp
                                                   self.full_load_hours, #hours_year
                                                   self.heatpump_power)
        return self.heat_demand
            
     #Calculate COP of heatpump according to heatpump type

    def get_cop(self):
        
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
            print("Heatpump type is not defined")
            return -9999
        
        #TODO: split cop to 15 min values
        
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

    # ===================================================================================
    # Controlling functions
    # ===================================================================================

    # This function limits the power of the photovoltaik to the given percentage.
    # It cuts the current power production down to the peak power multiplied by
    # the limit (Float [0;1]).
    def limitPowerTo(self, limit):

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

        # -> Function stub <-
        return self.timeseries[timestamp] * self.limit


class HeatStorage:
    """        
    Parameters
    ----------
    
    
    Attributes
    ---------
    
    """
    
    def __init__(self, storage_max, curr_charge = 0, storage_min = 10):
        self.max = storage_max
        self.curr_charge = curr_charge
        self.min = storage_min
        
        
#    def charge(self):
        # TODO: Ladevorgang für den Speicher erstellen. 
        #       Vermutlich verknüpfung mit dem Wärmepumpen Objekt nötig für Leistung und cop
        
class BDEWHeatPump(bdew.HeatBuilding):
    
    def __init__(self, df_index, heatpump_type = "Air", heat_sys_temp = 60, el_power = 10.6, **kwargs):
        
        super().__init__(df_index, **kwargs)
        self.cop = None
        self.heatpump_type = heatpump_type
        self.heat_sys_temp = heat_sys_temp
        self.el_power = el_power

    def get_cop(self):
        """ Calculation of the coefficient of performance depending
        on the outside temperature
        
        Parameters
        ----------
        heatpump_type: string
            defines the technology used. Ground is more efficient than Air.
        heat_sys_temp: int
            temperature needed for the heating system in °C
            
        el_power: int
            Electrical power of heatpump in kW
            
        References
        ----------
        ..  [1]: 'https://www.researchgate.net/publication/255759857_A_review_of_domestic_heat_pumps'
            Research paper about domestic heatpumps, containing the formulas used
        """
    
        cop_lst = []
        
        if self.heatpump_type == "Air":
            for tmp in self.temperature:
                cop = (6.81 - 0.121 * (self.heat_sys_temp - tmp)
                       + 0.00063 * (self.heat_sys_temp - tmp)**2)
                cop_lst.append(cop)
        
        elif self.heatpump_type == "Ground":
            for tmp in self.temperature:
                cop = (8.77 - 0.15 * (self.heat_sys_temp - tmp)
                       + 0.000734 * (self.heat_sys_temp - tmp)**2)
                cop_lst.append(cop)
        
        else:
            # TODO Raise Error
            print("Heatpump type is not defined")
            return None
    
        self.cop = pd.DataFrame({"cop" : cop_lst})
        self.cop.set_index(self.df.index, inplace = True)
    
                
        return self.cop

        
def get_cop(heatbuilding, heatpump_type = "Air", water_temp = 60):
    """ Calculation of the coefficient of performance depending
    on the outside temperature
    
    Parameters
    ----------
    heatbuilding: object
        HeatBuilding object from demandlib.bdew countaining the index 
        and outside temperature
    heatpump_type: string
        defines the technology used. Ground is more efficient than Air.
    water_temp: int
        temperature needed for the heating system
        
    References
    ----------
    ..  [1]: 'https://www.researchgate.net/publication/255759857_A_review_of_domestic_heat_pumps'
        Research paper about domestic heatpumps, containing the formulas used
    """

    cop_lst = []
    
    if heatpump_type == "Air":
        for tmp in heatbuilding.temperature:
            cop = (6.81 - 0.121 * (water_temp - tmp)
                   + 0.00063 * (water_temp - tmp)**2)
            cop_lst.append(cop)
    
    elif heatpump_type == "Ground":
        for tmp in heatbuilding.temperature:
            cop = (8.77 - 0.15 * (water_temp - tmp)
                   + 0.000734 * (water_temp - tmp)**2)
            cop_lst.append(cop)
    
    else:
        # TODO Raise Error
        print("Heatpump type is not defined")
        return None

    heatbuilding.cop = pd.DataFrame({"cop" : cop_lst})
    heatbuilding.cop.set_index(heatbuilding.df.index, inplace = True)

            
    return heatbuilding.cop
