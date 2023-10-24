# -*- coding: utf-8 -*-
"""
Info
----
This file contains the basic functionalities of the ElectricalEnergyStorage class.

"""
#Leistungen
#P_ac = Eingangsstrom                                       ac
#P_dc = Eingangsstrom in Gleichstrom                        dc
#P_nominal = Maximaler Strom Elektrolyseur gleichstrom      dc
#P_max = P_nominal                                          dc
#P_min = mindestLeistung Elektrolyseur                      dc
#P_nenn =  P_nominal                                        dc
#P_electronics =Eigenverbrauch des Elektrolyseurs           dc
#P_cell = Leistung Zelle                                    dc
#P_Elektrolyseur = P_nominal                                dc oder ac? P_Elektrolyseur
#P_Elektrolyseur=p_in  wird nicht mehr benötigt  

from .component import Component
import pandas as pd
import numpy as np
import datetime as dt
import time
from configparser import ConfigParser
from simses.main import SimSES
from scipy.interpolate import interp1d


class ElectrolysisSimses(Component):
    """.

    Info
    ----
    Standard values are taken from
    "simses/simulation/system_tests/configs/simulation.test_23.ini"

    Parameters
    ----------
    max_power : float
        nominal power in kW
    capacity : float
        nominal energy capacity in kWh
    soc : float
        initial state of charge
        between 0.0 and 1!
    soc_min: float
        minimal state of charge
        between 0.0 and 1!
    soc_max: float
        maximal state of charge
        between 0.0 and 1!
    efficiency: float
        charging/discharging efficiency, only used when model == 'simple'
    identifier : str
        name of the Energy Storage System
    model : str
        model to use for the Energy Storage simulation.
        The default is 'simple'.
    result_path : str, optional
        DESCRIPTION. The default is None
    environment: class,
        Instance fo the Environment class containing information about
        time dependent variables.
    user_profile : TYPE, optional
        DESCRIPTION. The default is None.
    unit : TYPE, optional
        DESCRIPTION. The default is None.
    cost : TYPE, optional
        DESCRIPTION. The default is None.

    Raises
    ------
    ValueError
        If soc_min > soc_max.
    """

    def __init__(self,
                 electrolyzer_power: float,
                 fuelcell_power: float,
                 capacity: float,
                 tank_size: float,
                 soc_start: float,
                 soc_min: float,
                 soc_max: float,
                 identifier=None,
                 result_path: str = None,
                 environment=None,
                 user_profile=None,
                 unit=None,
                 cost=None
                 ):

        # self.max_power = max_power

        # Call to super class
        super().__init__(
            unit, environment, user_profile, cost
        )

        if soc_max < soc_min:
            raise ValueError('soc_max must be higher than soc_min!')
        self.identifier = identifier

        if electrolyzer_power:
            self.electrolyzer_power = electrolyzer_power * 1000
        else:
            self.electrolyzer_power = 0

        if fuelcell_power:
            self.fuelcell_power = fuelcell_power * 1000
        else:
            self.fuelcell_power = 0

        if capacity:
            self.capacity = capacity * 1000
        else:
            self.capacity = 0

        self.tank_size = tank_size
        self.soc_min = soc_min
        self.soc_max = soc_max
        self.soc_start = soc_start
        self.df = pd.DataFrame(columns=['P', 'SOC'],
                               index=pd.date_range(
                                   start=self.environment.start,
                                   end=self.environment.end,
                                   freq=self.environment.time_freq))

        if self.identifier is None:
            simulation_name = 'NoName'
        else:
            simulation_name = self.identifier  # TODO: Add timestamp (?)
        self.simulation_config: ConfigParser = ConfigParser()
        # self.storage_config = StorageSystemConfig(self.simulation_config)

        # GENERAL config from "simses-master\simses\commons\config\simulation"
        self.simulation_config.add_section('GENERAL')
        # SimSES needs step size in sec
        self.simulation_config.set('GENERAL', 'TIME_STEP',
                                   str(self.environment.timebase * 60))
        self.simulation_config.set('GENERAL', 'START',
                                   str(dt.datetime.strptime(
                                       self.environment.start,
                                       "%Y-%m-%d %H:%M:%S")
                                       - dt.timedelta(
                                       minutes=self.environment.timebase*9))
                                   )
        self.simulation_config.set('GENERAL', 'END',
                                   self.environment.end)
        # possible extensions to GENERAL:
        # self.simulation_config.set('GENERAL', 'LOOP', 1)
        # self.simulation_config.set('GENERAL', 'EXPORT_DATA', True)
        # self.simulation_config.set('GENERAL', 'EXPORT_INTERVAL', 1)

        # Config for ELECTROLYZER
        self.simulation_config.add_section('ELECTROLYZER')

        # According to battery config, EOL is defined btwn. 0-1
        self.simulation_config.set('ELECTROLYZER',
                                   'EOL',
                                   str(0.8))

        self.simulation_config.set('ELECTROLYZER', 'PRESSURE_CATHODE', str(20))
        self.simulation_config.set('ELECTROLYZER', 'PRESSURE_ANODE', str(2))
        self.simulation_config.set('ELECTROLYZER', 'TOTAL_PRESSURE', str(20))
        self.simulation_config.set('ELECTROLYZER', 'TEMPERATURE', str(75))

        # Config for FUEL_CELL
        self.simulation_config.add_section('FUEL_CELL')

        # According to battery config, EOL is defined btwn. 0-1
        self.simulation_config.set('FUEL_CELL',
                                   'EOL',
                                   str(0.8))

        self.simulation_config.set('FUEL_CELL', 'PRESSURE_CATHODE', str(20))
        self.simulation_config.set('FUEL_CELL', 'PRESSURE_ANODE', str(2))
        self.simulation_config.set('FUEL_CELL', 'TEMPERATURE', str(75))

        # Config for the hydrogen storage
        self.simulation_config.add_section('HYDROGEN')
        self.simulation_config.set(
            'HYDROGEN', 'START_SOC', str(self.soc_start))
        self.simulation_config.set('HYDROGEN', 'MIN_SOC', str(self.soc_min))
        self.simulation_config.set('HYDROGEN', 'MAX_SOC', str(self.soc_max))

        # Config for STORAGE_SYSTEM, the overall system settings
        self.simulation_config.add_section('STORAGE_SYSTEM')

        # Config AC
        self.simulation_config.set('STORAGE_SYSTEM', 'STORAGE_SYSTEM_AC',
                                   'system_1,'
                                   # 5500.0
                                   + str(abs(self.electrolyzer_power))
                                   + ',333,'
                                   + 'fix,no_housing,no_hvac')

        # Config DC
        self.simulation_config.set('STORAGE_SYSTEM', 'STORAGE_SYSTEM_DC',
                                   'system_1,fix,hydrogen')

        # Config ACDC converter
        self.simulation_config.set(
            'STORAGE_SYSTEM',
            'ACDC_CONVERTER',
            'fix,FixEfficiencyAcDcConverter')

        # Config DCDC converter
        self.simulation_config.set(
            'STORAGE_SYSTEM',
            'DCDC_CONVERTER',
            'fix,FixEfficiencyDcDcConverter')

        self.simulation_config.set('STORAGE_SYSTEM',
                                   'STORAGE_TECHNOLOGY',
                                   # Config uses Watt hours
                                   'hydrogen, ' + \
                                   str(self.capacity)
                                   + ',hydrogen,'
                                   + 'NoFuelCell,'
                                   + str(abs(self.fuelcell_power))+','
                                   + 'PemElectrolyzer,'
                                   + str(abs(self.electrolyzer_power))
                                   + ','
                                   + 'PressureTank,'
                                   + str(self.tank_size)  # '700'
                                   )

        self.simses: SimSES = SimSES(
            str(result_path + '\\').replace('\\', '/'),
            simulation_name,
            do_simulation=True,
            do_analysis=True,
            simulation_config=self.simulation_config)

    def operate_storage(self, timestep, load):
        """.

        Parameters
        ----------
        timestep : TYPE
            DESCRIPTION.
        load : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        self.simses.run_one_simulation_step(
            time.mktime(
                dt.datetime.strptime(str(timestep),
                                     "%Y-%m-%d %H:%M:%S").timetuple()
            ),
            (load * -1000)
        )

        return (self.simses.state.soc,
                (self.simses.state.get(
                    self.simses.state.AC_POWER_DELIVERED) / 1000))

    def prepare_time_series(self):
        """.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        soc_lst = list()
        ac_lst = list()

        for timestep in pd.date_range(start=self.environment.start,
                                      end=self.environment.end,
                                      freq=self.environment.time_freq):

            soc, ac = self.operate_storage(
                timestep,
                self.residual_load[timestep]
            )

            soc_lst.append(soc)
            ac_lst.append(ac)

        self.timeseries = pd.DataFrame(
            {"state_of_charge": soc_lst,
             "ac_power": ac_lst},
            index=pd.date_range(start=self.environment.start,
                                end=self.environment.end,
                                freq=self.environment.time_freq)
        )

        return self.timeseries

    def reset_time_series(self):

        self.timeseries = None

        return self.timeseries

    def value_for_timestamp(self, timestamp):

        if type(timestamp) == int:

            return self.timeseries["ac_power"].iloc[timestamp]

        elif type(timestamp) == str:

            return self.timeseries["ac_power"].loc[timestamp]

        else:
            raise ValueError(
                "timestamp needs to be of type int or string."
                + " Stringformat: YYYY-MM-DD hh:mm:ss"
            )

    def observations_for_timestamp(self, timestamp):
        """.

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

            state_of_charge, ac_power = self.timeseries.iloc[timestamp]

        elif type(timestamp) == str:

            state_of_charge, ac_power = self.timeseries.loc[timestamp]

        else:
            raise ValueError(
                "timestamp needs to be of type int or string."
                + " Stringformat: YYYY-MM-DD hh:mm:ss"
            )

        observations = {
            "state_of_charge": state_of_charge,
            "ac_power": ac_power,
            "electrolyzer_power": self.electrolyzer_power,
            "fuelcell_power": self.fuelcell_power,
            "max_capacity": self.capacity * self.soc_max,
        }

        return observations

class ElectrolysisMoritz():
    
    def __init__(self,P_elektrolyseur):

        #P_elektrolyseur = (self.cell_area*self.max_current_density*self.n_cell)*self.n_stacks   # wieso wird die Leistung vom Elektrolyseur berechnet und nicht zb die Stacks
        self_n_stacks= P_elektrolyseur/(self.cell_area*self.max_current_density*self.n_cell)     # Ist die Leistung des Elektrolyseurs in dc oder ac
        # Constants
        self.F = 96485.34  # Faraday's constant [C/mol]
        self.R = 8.314  # ideal gas constant [J/(mol*K)]
        self.n = 2  # number of electrons transferred in reaction
        self.gibbs = 237.24e3
        self.E_th_0 = 1.481  # thermoneutral voltage at standard state
        self.M = 2.016  # molecular weight [g/mol]
        self.lhv = 33.33  # lower heating value of H2 [kWh/kg]
        self.hhv = 39.41  # higher heating value of H2 [kWh/kg]
        self.roh_H2 = 0.08988 #Density in kg/m3
        self.roh_O = 1.429 #Density kg/m3
        self.T = 50 # Grad Celsius
        
        #Leistungen/Stromdichte
        self.max_current_density = 2 * self.cell_area                                      # Habe ich hinzugefügt um eine maximale Stromdichte zu haben #self.max_current_density wie komme sonst auf diesen Wert durch I/A oder wird der festgelegt
        #self.P_nominal = self.P_stack * self.n_stacks
        self.p_nominal = P_elektrolyseur
        self.P_min = self.P_nominal * 0.1
        self.P_max = self.P_nominal

        # Stack parameters
        self.n_cells = 10  # Number of cells
        self.cell_area = 2500  # [cm^2] Cell active area
        self.temperature = 50  # [C] stack temperature
        self.max_current = 2.5  # [A/cm^2] current density #2 * self.cell_area              # Ist das nicht das selbe wie self.max_current_density

        self.p_atmo = 101325#2000000  # (Pa) atmospheric pressure / pressure of water
        self.p_anode = self.p_atmo  # (Pa) pressure at anode, assumed atmo
        self.p_cathode = 3000000

    def operate_storage(self, timestep, load):              #Ursprung: Saschas Modell /TODO: Name beibehalten / Rest anpassen / Load = Residuallast / Moritz Load = Spitzenlast
        
        # self.simses.run_one_simulation_step(                              #Was soll hier anstatt von Simses hin?
        #     time.mktime(
        #         dt.datetime.strptime(str(timestep),
        #                              "%Y-%m-%d %H:%M:%S").timetuple()
        #     ),
        #     (load * -1000)
        # )

        # return (self.simses.state.soc,
        #         (self.simses.state.get(
        #             self.simses.state.AC_POWER_DELIVERED) / 1000))

    def prepare_time_series(self):                          #Ursprung: Saschas Modell /TODO: Name beibehalten / in dieser Funktion soll das Dataframe initialisiert werden / nicht in __init__
        """.                                                # Kann man über self auf timseries zugreifen?

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        soc_lst = list()                
        ac_lst = list()

        for timestep in pd.date_range(start=self.environment.start,
                                      end=self.environment.end,
                                      freq=self.environment.time_freq):

            soc, ac = self.operate_storage(
                timestep,
                self.residual_load[timestep]
            )

            soc_lst.append(soc)
            ac_lst.append(ac)                   #hier müssen wir irgendwie P_ac einbeziehen als timeseries

        self.timeseries = pd.DataFrame(
            {"state_of_charge": soc_lst,
             "P_ac": ac_lst},
            index=pd.date_range(start=self.environment.start,
                                end=self.environment.end,
                                freq=self.environment.time_freq)
        )

        return self.timeseries

    def power_electronics(self, P_nenn):              #Ursprung: Moritz Modell (elektrolyzer_modell.py(statisch)) / unverändert / notwendig für Funktion AC to DC
        '''
        :param self.timeseries['P_ac']:        Power AC in W 
        :param P_nenn:      nominal Power in W
        :return:            self-consumption in kW
        '''
        for timestep in pd.date_range(start=self.environment.start,
                                      end=self.environment.end,
                                      freq=self.environment.time_freq):
        # Wirkungsgradkurve definieren
            relative_performance = [0.0,0.09,0.12,0.15,0.189,0.209,0.24,0.3,0.4,0.54,0.7,1.001]
            eta = [0.86,0.91,0.928,0.943,0.949,0.95,0.954,0.96,0.965,0.97,0.973,0.977]
        # Interpolationsfunktion erstellen
            f_eta = interp1d(relative_performance, eta)

        # Eigenverbrauch berechnen
            eta_interp = f_eta(self.timeseries['P_ac'] / P_nenn)  # Interpoliere den eta-Wert

            self.timeseries['P_electronics'] = self.timeseries['P_ac'] * (1 - eta_interp)  # Berechne den Eigenverbrauch [kW]

             
        return self.timeseries['P_electronics']
    
    def power_dc(self):                                     #Ursprung: Moritz Modell (elektrolyzer_modell.py(statisch)) / verändert
        '''
        :param:                 DataFrame mit 'P_ac' (Power AC in W)
        :return:                DataFrame mit 'P_dc' (Power DC in W)
        '''
        
        self.timeseries['P_dc'] = self.timeseries['P_ac'] - self.timeseries.apply(lambda row: self.power_electronics(row['P_ac'], self.stack_nominal() / 100), axis=1)
        return self.timeseries

    def calc_H2O_mfr(self, df):                #Ursprung: Moritz Modell (elektrolyzer_modell.py(statisch)) / verändert / Eingangsprodukt: Wasser
    
    #def calc_H2O_mfr(self, H2_mfr):                         
        # '''
        # H2_mfr: Hydrogen mass flow in kg
        # O_mfr: Oxygen mass flow in kg
        # return: needed water mass flow in kg
        # '''
        # M_H2O = 18.010 #mol/g
        # roh_H2O = 997 #kg/m3

        # ratio_M = M_H2O/self.M # (mol/g)/(mol/g)
        # H2O_mfr = H2_mfr * ratio_M + 40#H2O_mfr in kg
        # #H2O_mfr = H2O_mfr_kg / roh_H2O

        # return H2O_mfr

        '''
        H2_mfr: Hydrogen mass flow in kg                            
        O_mfr: Oxygen mass flow in kg
        return: needed water mass flow in kg
        '''
        df['H20 [kg]'] = 0.0
        df['heat energy [kW/h]'] = 0.0
        df['Surplus electricity [kW]'] = 0.0
        df['heat [kW/h]'] = 0.0

        M_H2O = 18.010 #mol/g
        roh_H2O = 997 #kg/m3

        ratio_M = M_H2O/self.M # (mol/g)/(mol/g)
        H2O_mfr = H2_mfr * ratio_M + 40#H2O_mfr in kg

        for i in range(len(df.index)):                                      
            P_elektrolyseur = df.loc[df.index[i], 'power total [kW]'] # P_elektrolyseur war vorher P_in #Was ist p_in
            H2_mfr = df.loc[df.index[i], "hydrogen [Nm3]"]
            # Check if the status is 'production'
            if df.loc[df.index[i], 'status'] == 'production':
                # Check if the power generation is less than or equal to the nominal power
                if df.loc[df.index[i], 'power total [kW]'] <= self.P_max:    # P_nominal = P_maximal
                    M_H2O = 18.010                                      # mol/g
                    roh_H2O = 997                                       # kg/m3
                    ratio_M = M_H2O/self.M                              # (mol/g)/(mol/g)
                    H2O_mfr = H2_mfr * ratio_M + 40                     # H2O_mfr in kg
                    df.loc[df.index[i], 'H2O [kg]'] = H2O_mfr
                    df.loc[df.index[i], 'specific consumption'] = self.timeseries['P_dc'] 
                else:
                    # Calculate H2O production using nominal power and specific energy consumptio
                    H2O_mfr = H2_mfr * ratio_M + 40                     # H2O_mfr in kg (TODO: Warum +40??)
                    df.loc[df.index[i], 'specific consumption'] = self.timeseries['P_dc']  - self.P_max
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[i], 'power total [kW]'] - self.P_max
                # Update the H2O production column for the current time step
                df.loc[df.index[i], 'H2O [kg]'] = H2O_mfr

            elif df.loc[df.index[i], 'status'] == 'booting':
                    df.loc[df.index[i], 'heat energy loss [kW]'] = 0.0085*self.P_max #0.85% of P_nominal energy losses for heat
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = self.timeseries['P_dc']  - (0.0085*self.P_max)
            else:
                df.loc[df.index[i], 'Surplus electricity [kW]'] = self.timeseries['P_dc'] 

        return df  

    def calc_H2_production(self, df):                       #Ursprung: Moritz Modell (dynamic_operate_modell.py(dynamisch)) / Ausgangsprodukt: Wasserstoff
        
        """
        :param P_dc:        Dataframe mit Power DC in W
        :return:            Dataframe mit 'hydrogen mass flow rate [kg/dt]', 'specific consumption', 'Surplus electricity [kW]', 'heat energy loss [kW]'
        """
        # power_left = P_dc #[kW]

        #I = self.calculate_cell_current(P_dc) #[A]
        # V = self.calc_cell_voltage(I, self.temperature) #[V]
        #eta_F = self.calc_faradaic_efficiency(I)
        # mfr = (eta_F * I * self.M * self.n_cells) / (self.n * self.F)
        # #power_left -= self.calc_stack_power(I, self.temperature) * 1e3
        # H2_mfr = (mfr*3600)/1000 #kg/dt

        #Initialisierung neuer Spalten für Wasserstoffproduktion, Wärmeenergie und überschüssigen Strom
        df['hydrogen mass flow rate [kg/dt]'] = 0.0
        df['heat energy [kW/h]'] = 0.0
        df['Surplus electricity [kW]'] = 0.0
        df['heat [kW/h]'] = 0.0

        #Berechnung der Wasserstoffproduktion, der Wärmeenergie und des Stromüberschusses für jeden Zeitschritt
        for i in range(len(df.index)):
            P_ = df.loc[df.index[i], 'power total [kW]']          # Frage: Wo wird 'power total' vorher im df als Zeile hinzugefügt und um welches P handelt es sich? P_ac, P_in, P_nom?? (Katrin)
            P_dc = df.loc[df.index[i], 'P_dc']                      # hier wird P_dc aus dem Dataframe 'df' genommen
            
            # Check if the status is 'production'
            if df.loc[df.index[i], 'status'] == 'production':
                # Check if the power generation is less than or equal to the nominal power
                if df.loc[df.index[i], 'power total [kW]'] <= self.P_max: #P_nominal = P_MAXIMAL
                    hydrogen_production = (((self.calc_faradaic_efficiency(self.calculate_cell_current(P_dc)) *(self.calculate_cell_current(P_dc)) * self.M * self.n_cells) / (self.n * self.F))*3600)/1000     #kg/dt
                    df.loc[df.index[i], 'hydrogen [kg/dt]'] = hydrogen_production
                    df.loc[df.index[i], 'specific consumption'] = P_dc
                else:
                    # Calculate hydrogen production using nominal power and specific energy consumptio
                    hydrogen_production = (((self.calc_faradaic_efficiency(self.calculate_cell_current(P_dc)) *(self.calculate_cell_current(P_dc)) * self.M * self.n_cells) / (self.n * self.F))*3600)/1000     #kg/dt #P_nominal richtige variabel?
                    df.loc[df.index[i], 'specific consumption'] = P_dc - self.P_max
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[i], 'power total [kW]'] - self.P_max
                # Update the hydrogen production column for the current time step
                df.loc[df.index[i], 'hydrogen [kg/dt]'] = hydrogen_production

            elif df.loc[df.index[i], 'status'] == 'booting':
                    df.loc[df.index[i], 'heat energy loss [kW]'] = 0.0085*self.P_max                         #0.85% of P_nominal energy losses for heat
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = P_dc - (0.0085*self.P_max)
            else:
                df.loc[df.index[i], 'Surplus electricity [kW]'] = P_dc

        return df    

    def heat_sys(self, q_cell, mfr_H2O):                    #Ursprung: Moritz Modell (elektrolyzer_modell.py(statisch)) / Ausgangsprodukt: Wärme
        '''
        Q_cell: in kWh
        mfr_H20: in kg/dt
        return: q_loss in kW
                q_H20_fresh in kW
        '''
        c_pH2O = 0.001162 #kWh/kg*k
        dt = self.T - 20 #operate temp. - ambient temp.

        q_H2O_fresh = - c_pH2O * mfr_H2O * dt * 1.5 #multyplied with 1.5 for transport water
        q_loss = - (q_cell + q_H2O_fresh) * 0.14

        return q_loss, q_H2O_fresh
        
    # def status_codes(self,dt,df):                         #Ursprung: Moritz Modell (dynamic_operate_modell.py(dynamisch))
    #     ''' 
    #     :param:     p_in über eine Zeitreihe
    #     return:     df mit Status-Codes 
    #     '''
        
    #     P_min = self.P_min
    #     long_gap_threshold = int(60/dt)             #Zeitschritte                                                     # muss aufgerundet werden oder sonst könnten kommazahlen entstehen
    #     short_gap_threshold = int(5/dt)             #Zeitschritte                                                     # muss aufgerundet werden oder sonst könnten kommazahlen entstehen
    #     # Maske/Filter, um Zeilen zu finden, in denen die Leistung unter P_min liegt
    #     below_threshold_mask = df['power total [kW]'] < P_min

    #     # Kurze Unterbrechungen (bis zu 4 Schritten) in denen Leistung < P_min
    #     short_gaps = below_threshold_mask.rolling(window=short_gap_threshold).sum()
    #     hot_mask = (short_gaps <= 4) & below_threshold_mask
    #     df.loc[hot_mask, 'status'] = 'hot'

    #     # Mittlere Unterbrechungen (zwischen 5 - 60 Schritten) in denen Leistung < P_min
    #     middle_gaps = below_threshold_mask.rolling(window=long_gap_threshold).sum()
    #     hot_standby_mask = ((5 <= middle_gaps) & (middle_gaps < 60)) & below_threshold_mask
    #     df.loc[hot_standby_mask, 'status'] = 'hot standby'
        
    #     # Lange Unterbrechungen (über 60 Schritte) in denen Leistung < P_min
    #     long_gaps = below_threshold_mask.rolling(window=long_gap_threshold).sum()
    #     cold_standby_mask = (long_gaps >= 60) & below_threshold_mask
    #     df.loc[cold_standby_mask, 'status'] = 'cold standby'

    #     # Produktionszeiträume (wenn P über P_min liegt) werden markiert.
    #     production_mask = df['power total [kW]'] >= P_min
    #     df.loc[production_mask, 'status'] = 'production'

    #     # Status Codes werden hinzugefügt, um verschiedene Zustände zu codieren.
    #     df['status codes'] = df['status'].replace({
    #         'cold standby': 0,
    #         'hot standby': 1,
    #         'hot': 2,
    #         'production': 4
    #     })

    #     # add 'booting' status
    #     booting_mask = pd.Series(False, index=df.index)
    #     # Identify rows where production is True and previous row is hot standby or cold standby
    #     booting_mask |= (df['status'].eq('production') & df['status'].shift(1).isin(['hot standby', 'cold standby']))

    #     # Identify rows where production is True and status is cold standby for up to 5 rows before

    #     booting_mask |= (df['status'].eq('production') & df['status'].shift(30).eq('cold standby'))

    #     # Identify rows where production is True and status is hot standby for up to 30 rows before
    #     for i in range(1, 15):
    #         booting_mask |= (df['status'].eq('production') & df['status'].shift(i).eq('hot standby'))

    #     df.loc[booting_mask, 'status'] = 'booting'

    #     # add status codes
    #     df['status codes'] = df['status'].replace({
    #         'cold standby': 0,
    #         'hot standby': 1,
    #         'hot': 2,
    #         'production': 4,
    #         'booting': 3
    #     })
    #     return df