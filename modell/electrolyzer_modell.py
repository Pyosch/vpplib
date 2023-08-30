import math
import numpy as np
import scipy
import pandas as pd
from scipy.signal import tf2ss, cont2discrete
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.optimize import minimize_scalar

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

class Electrolyzer:
    '''    Membrane : Zirfon
    Anode : Nickel 99.99%
    Cathode : Nickel 99.99%
    Electrolyte : KOH at 30 wt.%
    '''
    def __init__(self,P_elektrolyseur, P_ac, dt=15): # p_ac = eingangsleistung

          
        
        
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
        self.max_current = 2,5  # [A/cm^2] current density #2 * self.cell_area              # Ist das nicht das selbe wie self.max_current_density

        self.p_atmo = 101325#2000000  # (Pa) atmospheric pressure / pressure of water
        self.p_anode = self.p_atmo  # (Pa) pressure at anode, assumed atmo
        self.p_cathode = 3000000

    def calc_cell_voltage(self, I, T):
        """
        I [Adc]: stack current
        T [degC]: stack temperature
        return :: V_cell [Vdc/cell]: cell voltage
        """
        T_K = T + 273.15 #Celvin

        # Cell reversible voltage:
        E_rev_0 = self.gibbs / (self.n * self.F)  # Reversible cell voltage at standard state
        p_atmo = self.p_atmo
        p_anode = 200000
        p_cathode = 3000000

        # Arden Buck equation T=C, https://www.omnicalculator.com/chemistry/vapour-pressure-of-water#vapor-pressure-formulas
        p_h2O_sat = (0.61121 * np.exp((18.678 - (T / 234.5)) * (T / (257.14 + T)))) * 1e3  # (Pa)

       # General Nernst equation
        E_rev = E_rev_0 + ((self.R * T_K) / (self.n * self.F)) * (
           np.log( ((p_anode - p_h2O_sat) / p_atmo)* np.sqrt((p_cathode - p_h2O_sat) / p_atmo)))

        #E_rev = E_rev_0 - ((E_rev_0* 10**-3 * T_K) + 9.523 * 10**-5 * np.log(T_K) + 9.84*10**-8* T_K**2) #empirical equation


        T_anode = T_K #[K]

        T_cathode = T_K #[K]

        # anode charge transfer coefficient
        alpha_a = 2

        # cathode charge transfer coefficient
        alpha_c = 0.5

        # anode exchange current density
        i_0_a = 2 * 10 ** (-7)

        # cathode exchange current density
        i_0_c = 10 ** (-3)

        i = I / self.cell_area# A/cm^2

        # derived from Butler-Volmer eqs
        # V_act_a = ((self.R * T_anode) / (alpha_a * self.F)) * np.arcsinh(i / (2*i_0_a))
        #V_act_c = ((self.R * T_cathode) / (alpha_c * self.F)) * np.arcsinh(i / (2*i_0_c))
        # alternate equations for Activation overpotential
        # Option 2: Dakota: I believe this may be more accurate, found more
        # frequently in lit review
        # https://www.sciencedirect.com/science/article/pii/S0360319918309017

        z_a = 4 # stoichiometric coefficient of electrons transferred at anode
        z_c = 2 # stoichometric coefficient of electrons transferred at cathode
        i_0_a = 10**(-9) # anode exchange current density TODO: update to be f(T)?
        i_0_c = 10**(-3) # cathode exchange current density TODO: update to be f(T)?

        V_act_a = ((self.R*T_anode)/(alpha_a*z_a*self.F)) * np.log(i/i_0_a)
        V_act_c = ((self.R*T_cathode)/(alpha_c*z_c*self.F)) * np.log(i/i_0_c)

        # pulled from https://www.sciencedirect.com/science/article/pii/S0360319917309278?via%3Dihub
        lambda_nafion = 25
        t_nafion = 0.01  # cm

        sigma_nafion = ((0.005139 * lambda_nafion) - 0.00326) * np.exp(
            1268 * ((1 / 303) - (1 / T_K)))
        R_ohmic_ionic = t_nafion / sigma_nafion

        R_ohmic_elec = 50e-3

        V_ohmic = i * (R_ohmic_elec + R_ohmic_ionic) #[V]

        V_cell = E_rev + V_act_a + V_act_c + V_ohmic #[V]

        return V_cell

    def create_polarization(self):  # Spannungswerte berechnet
        currents = np.arange(1, (self.max_current_density*self.cell_area+ 10), 10)
        voltage = []
        for i in range(len(currents)):
            voltage.append(self.calc_cell_voltage(currents[i],self.T))
        df = pd.DataFrame({"current_A": currents, "voltage_U": voltage})
        df['power_W'] = df["current_A"]*df["voltage_U"]
        #df['current_A'] = df['current_A']/self.cell_area
        return df

    def calculate_cell_current(self, P_dc):
        '''
        P_in: Power DC in Watt
        P_cell: Power each cell
        return I: Current each cell in Ampere
        '''
        P_cell = P_dc /self.n_cells  #[kW]
        df = self.create_polarization()
        x = df['power_W'].to_numpy()
        y = df['current_A'].to_numpy()
        f = interp1d(x, y, kind='linear')
        return  f(P_cell)

    # def stack_nominal(self):                                                                                          # wird nicht mehr benötigt oder
    #     '''
    #     stack nominal in kW
    #     :return:
    #     '''
    #     P_nominal = (self.create_polarization().iloc[500,0] * self.create_polarization().iloc[500,1]*self.n_cells) /1000
    #     return P_nominal

    def power_electronics(self, P_nenn, P_ac):
        '''
        :param P_ac:        Power AC in W
        :param P_nenn:      nominal Power in W
        :return:            self-consumption in kW
        '''
        # Wirkungsgradkurve definieren
        relative_performance = [0.0,0.09,0.12,0.15,0.189,0.209,0.24,0.3,0.4,0.54,0.7,1.001]
        eta = [0.86,0.91,0.928,0.943,0.949,0.95,0.954,0.96,0.965,0.97,0.973,0.977]
        # Interpolationsfunktion erstellen
        f_eta = interp1d(relative_performance, eta)

        # Eigenverbrauch berechnen
        eta_interp = f_eta(P_ac / P_nenn)  # Interpoliere den eta-Wert

        P_electronics = P_ac * (1 - eta_interp)  # Berechne den Eigenverbrauch [kW]

        return P_electronics

    def power_dc(self, P_ac):# Berechnung P_dc                                                              #muss noch als df abgeändert werden
        '''
        :param P_ac:        Power AC in W
        :return:            Power DC in W
        '''
        P_dc = P_ac - self.power_electronics(P_ac, self.stack_nominal()/100) #[kW]

        return P_dc
    def status_codes(self,dt,df): 
            #''' Inputparameter ist p_in über eine Zeitreihe
        #return: df mit status Codes '''
        # P_min = self.P_min
        
        P_min = self.P_min
        long_gap_threshold = 60/dt          #Zeitschritte                                                     # muss aufgerundet werden oder sonst könnten kommazahlen entstehen
        short_gap_threshold = 5/dt          #Zeitschritte                                                     # muss aufgerundet werden oder sonst könnten kommazahlen entstehen
        # create a mask for power values below P_min
        below_threshold_mask = df['power total [kW]'] < P_min

        # find short gaps (up to 4 steps) where power is below P_min
        short_gaps = below_threshold_mask.rolling(window=short_gap_threshold).sum()
        hot_mask = (short_gaps <= 4) & below_threshold_mask
        df.loc[hot_mask, 'status'] = 'hot'

        # find middle gaps (between 5 and 60 steps) where power is below P_min
        middle_gaps = below_threshold_mask.rolling(window=long_gap_threshold).sum()
        hot_standby_mask = ((5 <= middle_gaps) & (middle_gaps < 60)) & below_threshold_mask
        df.loc[hot_standby_mask, 'status'] = 'hot standby'
        # find long gaps (over 60 steps) where power is below P_min
        long_gaps = below_threshold_mask.rolling(window=long_gap_threshold).sum()
        cold_standby_mask = (long_gaps >= 60) & below_threshold_mask
        df.loc[cold_standby_mask, 'status'] = 'cold standby'

        # mark production periods (above P_min)
        production_mask = df['power total [kW]'] >= P_min
        df.loc[production_mask, 'status'] = 'production'

        # add status codes
        df['status codes'] = df['status'].replace({
            'cold standby': 0,
            'hot standby': 1,
            'hot': 2,
            'production': 4
        })

        # add 'booting' status
        booting_mask = pd.Series(False, index=df.index)
        # Identify rows where production is True and previous row is hot standby or cold standby
        booting_mask |= (df['status'].eq('production') & df['status'].shift(1).isin(['hot standby', 'cold standby']))

        # Identify rows where production is True and status is cold standby for up to 5 rows before

        booting_mask |= (df['status'].eq('production') & df['status'].shift(30).eq('cold standby'))

        # Identify rows where production is True and status is hot standby for up to 30 rows before
        for i in range(1, 15):
            booting_mask |= (df['status'].eq('production') & df['status'].shift(i).eq('hot standby'))

        df.loc[booting_mask, 'status'] = 'booting'

        # add status codes
        df['status codes'] = df['status'].replace({
            'cold standby': 0,
            'hot standby': 1,
            'hot': 2,
            'production': 4,
            'booting': 3
        })
        return df
    
    def calc_hydrogen_production(self,P_max,P_dc,df):    #vorher run # for schleife rein           #P_dc muss eigentlich aus dem df geholt werden muss geändert werden

        """
        :param P_dc:        Power DC in W
        :return:            H2_mfr [kg/dt]: hydrogen mass flow rate
        """
        # power_left = P_dc #[kW]

         #I = self.calculate_cell_current(P_dc) #[A]
        # V = self.calc_cell_voltage(I, self.temperature) #[V]
         #eta_F = self.calc_faradaic_efficiency(I)
        # mfr = (eta_F * I * self.M * self.n_cells) / (self.n * self.F)
        # #power_left -= self.calc_stack_power(I, self.temperature) * 1e3
        # H2_mfr = (mfr*3600)/1000 #kg/dt
        df['hydrogen [Nm3]'] = 0.0
        df['heat energy [kW/h]'] = 0.0
        df['Surplus electricity [kW]'] = 0.0
        df['heat [kW/h]'] = 0.0

        for i in range(len(df.index)):
            P_in = df.loc[df.index[i], 'power total [kW]']
            # Check if the status is 'production'
            if df.loc[df.index[i], 'status'] == 'production':
                # Check if the power generation is less than or equal to the nominal power
                if df.loc[df.index[i], 'power total [kW]'] <= P_max: #P_nominal = P_MAXIMAL
                    hydrogen_production = (self.calc_faradaic_efficiency(self.calculate_cell_current(P_dc)) *(self.calculate_cell_current(P_dc)) * self.M * self.n_cells) / (self.n * self.F)
                    df.loc[df.index[i], 'hydrogen [Nm3]'] = hydrogen_production
                    df.loc[df.index[i], 'specific consumption'] = P_dc
                else:
                    # Calculate hydrogen production using nominal power and specific energy consumptio
                    hydrogen_production = (self.calc_faradaic_efficiency(self.calculate_cell_current(P_max)) *(self.calculate_cell_current(P_max)) * self.M * self.n_cells) / (self.n * self.F) #P_nominal richtige variabel?
                    df.loc[df.index[i], 'specific consumption'] = P_dc - P_max
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[i], 'power total [kW]'] - P_max
                # Update the hydrogen production column for the current time step
                df.loc[df.index[i], 'hydrogen [Nm3]'] = hydrogen_production

            elif df.loc[df.index[i], 'status'] == 'booting':
                    df.loc[df.index[i], 'heat energy loss [kW]'] = 0.0085*P_max #0.85% of P_nominal energy losses for heat
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = P_dc - (0.0085*P_max)
            else:
                df.loc[df.index[i], 'Surplus electricity [kW]'] = P_dc

        return df

    def calc_O_mfr(self, H2_mfr, P_dc, df):                   
        '''
        Input parameter: H2_mfr = massen flow rate H2 in kg/dt oder df
        return: Oxygen flow rate in kg/dt as a df
        '''

        df["oxygen flow rate in kg/dt"] = 0.0
        #df['hydrogen [Nm3]'] = 0.0
        df['heat energy [kW/h]'] = 0.0
        df['Surplus electricity [kW]'] = 0.0
        df['heat [kW/h]'] = 0.0

        for i in range(len(df.index)):
            
            P_dc = df.loc[df.index[i], 'power total [kW]']
            P_max = self.P_nominal                                      # create an instance (?)
            roh_O = 1.429                                               # density of oxygen in kg/m3
            
            # Check if the status is 'production'
            if df.loc[df.index[i], 'status'] == 'production':           # df.loc (=Zugriff auf eine Gruppe von Spalten und Zeilen nach Beschriftung(en))
                # Check if the power generation is less than or equal to the nominal power
                if df.loc[df.index[i], 'power total [kW]'] <= P_max:    # P_nominal = P_MAXIMAL  
                    oxygen_production_m3 = (H2_mfr/self.roh_H2)/2       # [m^3/dt]
                    oxygen_production = oxygen_production_m3*roh_O      # [kg/dt]
                    df.loc[df.index[i], "oxygen flow rate in kg/dt"] = oxygen_production
                    df.loc[df.index[i], 'specific consumption'] = P_dc
                else:
                    # Calculate oxygen production using nominal power and specific energy consumption
                    oxygen_production_m3 = (H2_mfr/self.roh_H2)/2       #[m^3/dt]
                    oxygen_production = oxygen_production_m3*roh_O      #[kg/dt]
                    df.loc[df.index[i], 'specific consumption'] = P_dc - P_max
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[i], 'power total [kW]'] - P_max
                # Update the oxygen production column for the current time step
                df.loc[df.index[i], 'hydrogen [Nm3]'] = oxygen_production

            elif df.loc[df.index[i], 'status'] == 'booting':
                    df.loc[df.index[i], 'heat energy loss [kW]'] = 0.0085*P_max #0.85% of P_nominal energy losses for heat
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = P_dc - (0.0085*P_max)
            else:
                df.loc[df.index[i], 'Surplus electricity [kW]'] = P_dc

        return df

    def calc_H2O_mfr(self, P_max, P_dc, df):                         #vorher H2_mfr als input
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
        #H2O_mfr = H2O_mfr_kg / roh_H2O

        for i in range(len(df.index)):
            P_in = df.loc[df.index[i], 'power total [kW]']
            H2_mfr = df.loc[df.index[i], "hydrogen [Nm3]"]
            # Check if the status is 'production'
            if df.loc[df.index[i], 'status'] == 'production':
                # Check if the power generation is less than or equal to the nominal power
                if df.loc[df.index[i], 'power total [kW]'] <= P_max:    # P_nominal = P_maximal
                    M_H2O = 18.010                                      # mol/g
                    roh_H2O = 997                                       # kg/m3
                    ratio_M = M_H2O/self.M                              # (mol/g)/(mol/g)
                    H2O_mfr = H2_mfr * ratio_M + 40                     # H2O_mfr in kg
                    df.loc[df.index[i], 'H2O [kg]'] = H2O_mfr
                    df.loc[df.index[i], 'specific consumption'] = P_dc
                else:
                    # Calculate H2O production using nominal power and specific energy consumptio
                    H2O_mfr = H2_mfr * ratio_M + 40                     # H2O_mfr in kg (TODO: Warum +40??)
                    df.loc[df.index[i], 'specific consumption'] = P_dc - P_max
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[i], 'power total [kW]'] - P_max
                # Update the H2O production column for the current time step
                df.loc[df.index[i], 'H2O [kg]'] = H2O_mfr

            elif df.loc[df.index[i], 'status'] == 'booting':
                    df.loc[df.index[i], 'heat energy loss [kW]'] = 0.0085*P_max #0.85% of P_nominal energy losses for heat
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = P_dc - (0.0085*P_max)
            else:
                df.loc[df.index[i], 'Surplus electricity [kW]'] = P_dc

        return df

    def calc_faradaic_efficiency(self, I):
        """
            #     I [A]: stack current
            #     return :: eta_F [-]: Faraday's efficiency
            #     Reference: https://res.mdpi.com/d_attachment/energies/energies-13-04792/article_deploy/energies-13-04792-v2.pdf
            #     """
        p = 20 #electrolyze pressure in bar
        i = I/self.cell_area

        a_1 = -0.0034
        a_2 = -0.001711
        b = -1
        c = 1

        eta_f = (a_1*p+a_2)*((i)**b)+c

        return eta_f



    def gas_drying(self,mfr_H2):
        '''
        input n_h2: mass flow in kg/h
        :param n_H2:
        :return:
        '''
        M_H2 = 2.016*10**-3  # kg/mol Molare Masse H2
        nH2 = (mfr_H2/3600)/M_H2 #kg/h in kg/s in mol/s
        cp_H2 = 14300  # J/kg*K Wärmekapazität H2

        X_in = 0.1 #Mol H2O/Mol H2
        X_out = 1 #minimum needed
        n = (X_in/(X_out-X_in))*nH2
        dT=300-20 #Temperaturdifferenz zwischen Adsorbtion und Desorption

        P_hz = cp_H2*M_H2*n*dT #[W]

        Q_des = 48600*n #J/s
        P_gasdrying = P_hz + Q_des #in W
        return P_gasdrying

    def compression(self,p2):
        '''
        :param p2: needed pressure in bar
        :param T: electrolyze temperature
        :return: needed Power for compression in kW/kg
        '''
        #w_isotherm = R * T * Z * ln(p2 / p1)
        #p1=101325 #p atmo in pascal
        T2 = 273.15+30 # [K]
        p1 = 30 #bar
        Z = 0.95
        k = 1.4
        kk = k / (k - 1)
        eta_Ver = 0.75
        w_isentrop = kk * self.R * T2 * Z*(((p2 / p1)**kk) - 1)
        #T2 = T*(p2 / p1) ** kk
        P_compression = (((w_isentrop/self.M)/1000) * (1/3600)) / eta_Ver
        return P_compression

    def heat_cell(self, P_dc):
        '''
        P_dc: in W
        return: q cell in W
        '''
        V_th = self.E_th_0 # 
        I = self.calculate_cell_current(P_dc) #[A]
        U_cell = self.calc_cell_voltage(I, self.temperature) # [V]

        q_cell = self.n_cells*(U_cell - V_th)*I
        return q_cell

    def heat_sys(self, q_cell, mfr_H2O):
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

    def calc_mfr_cool(self, q_system):
        '''
        q_system in kWh
        return: mfr cooling water in kg/h
        '''
        q_system = q_system                                             #Wärme des Systems in kWh
        c_pH2O = 0.001162 #kWh/kg*k
        #operate temperature - should temperature
        mfr_cool = ((q_system)/(c_pH2O*(50-20)))

        return mfr_cool

    def calc_pump(self, mfr_H2O, P_stack, P_dc, pressure):
        '''
        mfr_H2o: in kg/h
        P_stack: kw
        P_dc:kw
        pressure: in Pa
        return: kW
        '''
        # Wirkungsgradkurve Kreiselpumpe: https://doi.org/10.1007/978-3-642-40032-2
        relative_performance_pump = [0.0,0.05,0.1,0.15,0.2,0.25,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.001]
        eta_pump = [0.627,0.644,0.661,0.677,0.691,0.704,0.715,0.738,0.754,0.769,0.782,0.792,0.797,0.80]
        # Interpolationsfunktion erstellen
        f_eta_pump = interp1d(relative_performance_pump, eta_pump, kind='linear')
        # Wirkungsgrad berechnen für aktuellen
        eta_interp_pump = f_eta_pump(P_dc/(P_stack))  # Interpoliere den eta-Wert

        #Druckverlust Leitungen in Pa
        relative_performance_pressure = [0.0, 0.02, 0.07, 0.12, 0.16, 0.2, 0.25, 0.32, 0.36, 0.4, 0.47, 0.54, 0.59,
                                         0.63, 0.67, 0.71, 0.74, 0.77, 0.8, 0.83, 0.86, 0.89, 0.92, 0.95, 0.98, 1.01]
        dt_pressure = [0.0, 330, 1870, 3360, 5210, 8540, 12980, 21850, 27020, 32930, 44000, 59500, 70190, 80520, 90850,
                        100810,110400, 119990, 128840, 138420, 148010, 158330, 169760, 181190, 191890, 200000]
        # Interpolationsfunktion erstellen
        f_dt_pressure = interp1d(relative_performance_pressure, dt_pressure)
        # Eigenverbrauch berechnen
        dt_interp_pressure = f_dt_pressure(P_dc/(P_stack))  # Interpoliere den eta-Wert

        vfr_H2O = (mfr_H2O/997) #mass in volume with 997 kg/m3
        P_pump_fresh =  (vfr_H2O/3600) * (2000000) * (1-eta_interp_pump)
        P_pump_cool = (vfr_H2O / 3600) * (dt_interp_pressure) * (1 - eta_interp_pump)

        return P_pump_fresh, P_pump_cool
    


    #def eta_total(self, P_dc,):
        #H2_mfr= self.run(P_dc)                                     # Massenstrom Wasserstoff in kg/dt
       
        # O_mfr = self.calc_O_mfr(H2_mfr_cal)                             # Massenstrom Sauerstoff in kg/dt 
        # H2O_mfr = self.calc_H2O_mfr(H2_mfr_cal, O_mfr)                  # Massenstrom Wasser in kg
        # H2_mfr= self.run(P_dc)                                     # Massenstrom Wasserstoff in kg/dt
        #H2_mfr= self.run(P_dc)                                     # Massenstrom Wasserstoff in kg/dt
        # O_mfr = self.calc_O_mfr(H2_mfr_cal)                             # Massenstrom Sauerstoff in kg/dt
        # H2O_mfr = self.calc_H2O_mfr(H2_mfr_cal, O_mfr)                  # Massenstrom Wasser in kg
        # P_gasdrying = self.gas_drying(H2_mfr_cal)                       # Calculate power for gas drying
        # P_compression = self.compression(3000000)                       # Calculate power for compression /warum nicht P_dc?
        # q_cell = self.heat_cell(P_dc)                                   # Erzeugte Wärme in Zelle in W
        # q_loss, q_H2O_fresh = self.heat_sys(q_cell, H2O_mfr)            # Wärmeverluste in W
        # q_system = (P_dc + P_gasdrying + P_compression) / 3600       # Gesamtwärme des Systems in kWh
        # mfr_cool = self.calc_mfr_cool(q_system)                         # Massenstrom Kühlung in kg/dt
        # P_pump_fresh, P_pump_cool = self.calc_pump(H2O_mfr, P_dc, 2000000)  # Calculate pump power
        # P_total_in = P_dc - P_gasdrying - P_compression - P_pump_fresh - P_pump_cool
       
        #eta_run= P_dc/(H2_mfr*self.lhv)                       #kWh/kg

       # return eta_run

   
    # def __init__(self, n_stacks):
    #     self.n_stacks = n_stacks
    #     self.P_stack= 531 #fixed nominal power of stack
    #     self.P_nominal = self.P_stack * n_stacks
    #     self.P_min = self.P_nominal * 0.1
    #     self.P_max = self.P_nominal

   
# Definition einer Timeseries:
# 
# Times Series
ds = pd.Series(data, index=index)

# Dataframe (zweidimensionale Datenstruktur, in Tabellenform, wie Exceltabelle oder SQL-Tabelle)
df = pd.DataFrame(data, index=index)

# df['neue_spalte'] = df['alte_spalte'] * 2

# Indexbasierte Auswahl
# df.loc[df['spalte'] > 5]

# Integerbasierte Auswahl
# df.iloc[2:5, 1:3]

# Bessere Praxis (explizite Indexierung)
# df.loc['zeile', 'spalte']

# Ersetze fehlende Werte durch den Mittelwert
# df['spalte'].fillna(df['spalte'].mean(), inplace=True)