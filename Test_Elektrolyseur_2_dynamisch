import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

class operate_electrolyzer:
    def __init__(self, n_stacks):
        self.n_stacks = n_stacks
        self.P_stack= 531 #fixed nominal power of stack
        self.P_nominal = self.P_stack * n_stacks
        self.P_min = self.P_nominal * 0.1
        self.P_max = self.P_nominal

    def power_profile(self, df):
        '''
        input: Df with P_in Data
        dt=1min
        Output: Df with Status, heat, hydrogen_production,
        '''
        price = pd.read_csv('../prices/day_ahead_prices_2015_ger.csv', sep=';', header=0, index_col=0, decimal=',',
                            date_parser=lambda idx: pd.to_datetime(idx, utc=True))
        price = price.resample('1min').interpolate(method='linear')
        price = price.loc['2015-01-01 00:00:00+00:00':'2015-12-31 23:45:00+00:00']
        df['Day-ahead Price [EUR/kWh]'] = price[' Day-ahead Price [EUR/kWh] ']
        P_min = self.P_min


        P_min = self.P_min
        long_gap_threshold = 60
        short_gap_threshold = 5
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
        P_nominal = self.P_nominal
        # Load power curve data
        power_curve = pd.read_csv('../plots/my_power_curve.csv', sep=',', decimal='.', header=0)

        # Define function to calculate specific energy consumption
        def operation_funcion(P_nominal, P_in):
            '''
            :param P_nominal: nominal power of the electrolyzer
            :param P_in: actual power generation of the electrolyzer
            :return: specific energy consumption in kWh/Nm3 for P_in
            '''

            x = power_curve['relative power [%]'].to_numpy()
            x = (x * P_nominal) / 100
            y = power_curve['energy consumption [kWh/m3]'].to_numpy()

            f = interp1d(x, y, kind='linear')

            return f(P_in)
        def heat_funcion(P_nominal, P_in):
            '''
            calculate ind interpolate eta heat for each P_in
            '''
            x = [0.08,0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95,1.01]
            for i in range(len(x)):
                x[i] = x[i]*P_nominal
            y = [0.01,0.017,0.035,0.046,0.059,0.068,0.078,0.086,0.093,0.10,0.109,0.116,0.123,0.129,0.136,0.144,0.148,0.153,0.159,0.163]
            f = interp1d(x, y, kind='linear')
            return f(P_in)

        # Initialize new columns for hydrogen production, heat energy, and surplus electricity
        df['hydrogen [Nm3]'] = 0.0
        df['heat energy [kW/h]'] = 0.0
        df['Surplus electricity [kW]'] = 0.0
        df['heat [kW/h]'] = 0.0

        # Calculate hydrogen production, heat energy, and surplus electricity for each time step
        for i in range(len(df.index)):
            P_in = df.loc[df.index[i], 'power total [kW]']
            # Check if the status is 'production'
            if df.loc[df.index[i], 'status'] == 'production':
                # Check if the power generation is less than or equal to the nominal power
                if df.loc[df.index[i], 'power total [kW]'] <= P_nominal:
                    # Calculate specific energy consumption and hydrogen production
                    specific_energy_consumption = operation_funcion(P_nominal, P_in * 0.99)
                    hydrogen_production = (P_in / 60) / specific_energy_consumption
                    df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption
                    df.loc[df.index[i], 'heat [kW/h]'] = P_nominal * heat_funcion(P_nominal, P_in)
                else:
                    # Calculate hydrogen production using nominal power and specific energy consumption
                    specific_energy_consumption = operation_funcion(P_nominal, P_nominal * 0.99)
                    hydrogen_production = (P_nominal / 60) / specific_energy_consumption
                    df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[i], 'power total [kW]'] - P_nominal
                    df.loc[df.index[i], 'heat [kW/h]'] = P_nominal * heat_funcion(P_nominal, P_nominal)
                # Update the hydrogen production column for the current time step
                df.loc[df.index[i], 'hydrogen [Nm3]'] = hydrogen_production

            elif df.loc[df.index[i], 'status'] == 'booting':
                    df.loc[df.index[i], 'heat energy loss [kW]'] = 0.0085*P_nominal #0.85% of P_nominal energy losses for heat
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = P_in - (0.0085*P_nominal)
            else:
                df.loc[df.index[i], 'Surplus electricity [kW]'] = P_in

        return df


    def calculate_full_load_hours(self, df):
        '''
        Calculates the full load hours of the electrolyzer.

        :param df: DataFrame containing the hydrogen production data
        :param P_nominal: nominal power of the electrolyzer in kW
        :return: full load hours of the electrolyzer
        '''
        P_nominal = self.P_nominal
        # Convert hydrogen production to kWh
        for i in range(len(df.index)):
            if df.loc[df.index[i], 'status'] == 'production':
                if df.loc[df.index[i], 'power total [kW]'] <= P_nominal:
                    df.loc[df.index[i], 'consumed energy [kWh]'] = df.loc[df.index[i], 'power total [kW]']
                else:
                    df.loc[df.index[i],'consumed energy [kWh]'] = P_nominal
        # Calculate full load hours
        full_load_hours = ((df['consumed energy [kWh]'].sum()/60)/P_nominal)
        return full_load_hours

    def calculate_hydrogen_production_elogen(self, df):
        '''
        Calculates hydrogen production for each time step based on the power generation.
        :param df: DataFrame containing the power generation data and status information
        :param P_nominal: nominal power of the electrolyzer
        :return: DataFrame with a new column 'hydrogen [Nm3]' containing the hydrogen production for each time step
        '''
        P_nominal = self.P_nominal
        # Load power curve data
        power_curve = pd.read_csv('plots/elogen_powercurve_data.csv', sep=';', decimal=',', header=0)

        # Define function to calculate specific energy consumption
        def operation_funcion(P_nominal, P_in):
            '''
            :param P_nominal: nominal power of the electrolyzer
            :param P_in: actual power generation of the electrolyzer
            :return: specific energy consumption in kWh/Nm3 for P_in
            '''

            x = power_curve['relative Leistung [%]'].to_numpy()
            x = (x * P_nominal) / 100
            y = power_curve['Energieverbrauch [kWh/Nm3]'].to_numpy()

            f = interp1d(x, y, kind='linear')

            return f(P_in)

        # Initialize new columns for hydrogen production, heat energy, and surplus electricity
        df['hydrogen [Nm3]'] = 0.0
        df['heat energy [kW/h]'] = 0.0
        df['Surplus electricity [kW]'] = 0.0

        # Calculate hydrogen production, heat energy, and surplus electricity for each time step
        for i in range(len(df.index)):
            # Check if the status is 'production'
            if df.loc[df.index[i], 'status'] == 'production':
                # Check if the power generation is less than or equal to the nominal power
                if df.loc[df.index[i], 'power total [kW]'] <= P_nominal:
                    # Calculate specific energy consumption and hydrogen production
                    P_in = df.loc[df.index[i], 'power total [kW]']
                    specific_energy_consumption = operation_funcion(P_nominal, P_in * 0.99)
                    hydrogen_production = (P_in / 60) / specific_energy_consumption
                else:
                    # Calculate hydrogen production using nominal power and specific energy consumption
                    specific_energy_consumption = operation_funcion(P_nominal, P_nominal * 0.99)
                    hydrogen_production = (P_nominal / 60) / specific_energy_consumption

                # Update the hydrogen production column for the current time step
                df.loc[df.index[i], 'hydrogen [Nm3]'] = hydrogen_production
                # Check if the power generation is greater than the nominal power
                if df.loc[df.index[i], 'power total [kW]'] > P_nominal:
                    # Calculate surplus electricity
                    surplus_electricity = df.loc[df.index[i], 'power total [kW]'] - P_nominal
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = surplus_electricity

            # Check if the status is 'booting'
            if df.loc[df.index[i], 'status'] == 'booting':
                # Set heat energy to 8.5 kW
                df.loc[df.index[i], 'heat energy [kW/h]'] = 8.5

        return df

    def hydrogen_production_peakload(self, df):
        '''
        input: Df with P_in Data
        dt=1min
        Output: Df with Status, heat, hydrogen_production,
        peakload = upper 15 %
        '''
        P_min = self.P_min
        quantile = df['power total [kW]'].quantile(0.80)
        df2 = pd.DataFrame()
        df2['power total [kW]'] = df['power total [kW]'] - quantile
        df2['power total [kW]'] = df2['power total [kW]'].clip(lower=0.0)

        long_gap_threshold = 60
        short_gap_threshold = 5
        # create a mask for power values below P_min
        below_threshold_mask = df2['power total [kW]'] == 0.0

        # find short gaps (up to 4 steps) where power is below P_min
        short_gaps = below_threshold_mask.rolling(window=short_gap_threshold).sum()
        hot_mask = (short_gaps <= 4) & below_threshold_mask
        df2.loc[hot_mask, 'status'] = 'hot'

        # find middle gaps (between 5 and 60 steps) where power is below P_min
        middle_gaps = below_threshold_mask.rolling(window=long_gap_threshold).sum()
        hot_standby_mask = ((5 <= middle_gaps) & (middle_gaps < 60)) & below_threshold_mask
        df2.loc[hot_standby_mask, 'status'] = 'hot standby'

        # find long gaps (over 60 steps) where power is below P_min
        long_gaps = below_threshold_mask.rolling(window=long_gap_threshold).sum()
        cold_standby_mask = (long_gaps >= 60) & below_threshold_mask
        df2.loc[cold_standby_mask, 'status'] = 'cold standby'

        # mark production periods (above P_min)
        production_mask = df2['power total [kW]'] > 0.0
        df2.loc[production_mask, 'status'] = 'production'

        # add status codes
        df2['status codes'] = df2['status'].replace({
            'cold standby': 0,
            'hot standby': 1,
            'hot': 2,
            'production': 4
        })

        # add 'booting' status
        booting_mask = pd.Series(False, index=df2.index)

        # Identify rows where production is True and previous row is hot standby or cold standby
        booting_mask |= (df2['status'].eq('production') & df2['status'].shift(1).isin(['hot standby', 'cold standby']))

        # Identify rows where production is True and status is cold standby for up to 5 rows before

        booting_mask |= (df2['status'].eq('production') & df2['status'].shift(30).eq('cold standby'))

        # Identify rows where production is True and status is hot standby for up to 30 rows before
        for i in range(1, 31):
            booting_mask |= (df2['status'].eq('production') & df2['status'].shift(i).eq('hot standby'))

        df2.loc[booting_mask, 'status'] = 'booting'

        # add status codes
        df2['status codes'] = df2['status'].replace({
            'cold standby': 0,
            'hot standby': 1,
            'hot': 2,
            'production': 4,
            'booting': 3
        })
        P_nominal = self.P_nominal
        # Load power curve data
        power_curve = pd.read_csv('../plots/my_power_curve.csv', sep=',', decimal='.', header=0)

        # Define function to calculate specific energy consumption
        def operation_funcion(P_nominal, P_in):
            '''
            :param P_nominal: nominal power of the electrolyzer
            :param P_in: actual power generation of the electrolyzer
            :return: specific energy consumption in kWh/Nm3 for P_in
            '''

            x = power_curve['relative power [%]'].to_numpy()
            x = (x * P_nominal) / 100
            y = power_curve['energy consumption [kWh/m3]'].to_numpy()

            f = interp1d(x, y, kind='linear')

            return f(P_in)

        def heat_funcion(P_nominal, P_in):
            '''
            calculate ind interpolate eta heat for each P_in
            '''
            x = [0.08,0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95,1.01]
            for i in range(len(x)):
                x[i] = x[i]*P_nominal
            y = [0.01,0.017,0.035,0.046,0.059,0.068,0.078,0.086,0.093,0.10,0.109,0.116,0.123,0.129,0.136,0.144,0.148,0.153,0.159,0.163]
            f = interp1d(x, y, kind='linear')
            return f(P_in)

        # Initialize new columns for hydrogen production, heat energy, and surplus electricity
        df['hydrogen [Nm3]'] = 0.0
        df['heat energy [kW/h]'] = 0.0
        df['Surplus electricity [kW]'] = 0.0
        df['heat [kW/h]'] = 0.0

        # Calculate hydrogen production, heat energy, and surplus electricity for each time step

        for i in range(len(df.index)):
            # Check if the status is 'production'
            P_in = df2.loc[df2.index[i], 'power total [kW]']
            if df.loc[df.index[i], 'power total [kW]'] >= quantile:
                # Check if the power generation is less than or equal to the nominal power
                if df2.loc[df2.index[i], 'power total [kW]'] <= P_min:
                    hydrogen_production = 0.0
                elif df2.loc[df2.index[i], 'power total [kW]'] <= P_nominal:
                    # Calculate specific energy consumption and hydrogen production
                    specific_energy_consumption = operation_funcion(P_nominal, P_in*0.99)
                    hydrogen_production = (P_in / 60) / specific_energy_consumption
                    df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[
                                                                          df.index[i], 'power total [kW]'] - df2.loc[
                                                                          df2.index[i], 'power total [kW]']
                    df.loc[df.index[i], 'heat [kW/h]'] = P_nominal * heat_funcion(P_nominal, P_in)
                else:
                    # Calculate hydrogen production using nominal power and specific energy consumption
                    specific_energy_consumption = operation_funcion(P_nominal, P_nominal * 0.99)
                    hydrogen_production = (P_nominal / 60) / specific_energy_consumption
                    df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[i], 'power total [kW]'] - P_nominal
                    df.loc[df.index[i], 'heat [kW/h]'] = P_nominal * heat_funcion(P_nominal, P_nominal)

                # Update the hydrogen production column for the current time step
                df.loc[df.index[i], 'hydrogen [Nm3]'] = hydrogen_production
            elif df2.loc[df.index[i], 'status'] == 'booting':
                df.loc[df.index[
                    i], 'heat energy loss [kW]'] = 0.0085 * P_nominal  # 0.85% of P_nominal energy losses for heat
                df.loc[df.index[i], 'Surplus electricity [kW]'] = P_in - (0.0085 * P_nominal)
            else:
                df.loc[df.index[i], 'Surplus electricity [kW]'] = P_in

        return df


    def hydrogen_production_baseload(self, df):
        '''
        input: Df with P_in Data
        dt=1min
        Output: Df with Status, heat, hydrogen_production
        baseload: 60 %
        '''
        P_min = self.P_min
        long_gap_threshold = 60
        short_gap_threshold = 5

        quantile = df['power total [kW]'].quantile(0.62)
        if quantile > self.P_nominal:
            quantile = self.P_nominal
        else:
            quantile = quantile
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
        for i in range(1, 31):
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
        P_nominal = self.P_nominal
        # Load power curve data
        power_curve = pd.read_csv('../plots/my_power_curve.csv', sep=',', decimal='.', header=0)

        # Define function to calculate specific energy consumption
        def operation_funcion(P_nominal, P_in):
            '''
            :param P_nominal: nominal power of the electrolyzer
            :param P_in: actual power generation of the electrolyzer
            :return: specific energy consumption in kWh/Nm3 for P_in
            '''

            x = power_curve['relative power [%]'].to_numpy()
            x = (x * P_nominal) / 100
            y = power_curve['energy consumption [kWh/m3]'].to_numpy()

            f = interp1d(x, y, kind='linear')

            return f(P_in)

        def heat_funcion(P_nominal, P_in):
            '''
            calculate ind interpolate eta heat for each P_in
            '''
            x = [0.08,0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95,1.01]
            for i in range(len(x)):
                x[i] = x[i]*P_nominal
            y = [0.01,0.017,0.035,0.046,0.059,0.068,0.078,0.086,0.093,0.10,0.109,0.116,0.123,0.129,0.136,0.144,0.148,0.153,0.159,0.163]
            f = interp1d(x, y, kind='linear')
            return f(P_in)

        # Initialize new columns for hydrogen production, heat energy, and surplus electricity
        df['hydrogen [Nm3]'] = 0.0
        df['heat energy [kW/h]'] = 0.0
        df['Surplus electricity [kW]'] = 0.0
        df['heat [kW/h]'] = 0.0

        # Calculate hydrogen production, heat energy, and surplus electricity for each time step
        for i in range(len(df.index)):
            # Check if the status is 'production'
            P_in = df.loc[df.index[i], 'power total [kW]']
            if df.loc[df.index[i], 'status'] == 'production':
                # Check if the power generation is less than or equal to the quantile
                if df.loc[df.index[i], 'power total [kW]'] <= quantile:
                    if df.loc[df.index[i], 'power total [kW]'] > P_nominal:
                        specific_energy_consumption = operation_funcion(P_nominal, quantile * 0.99)
                        hydrogen_production = (quantile / 60) / specific_energy_consumption
                        df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption
                        df.loc[df.index[i], 'heat [kW/h]'] = quantile * heat_funcion(P_nominal, quantile)
                        df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[i], 'power total [kW]'] - quantile
                        surplus_electricity = df.loc[df.index[i], 'power total [kW]'] - P_nominal
                        df.loc[df.index[i], 'Surplus electricity [kW]'] = surplus_electricity
                    else:
                        # Calculate specific energy consumption and hydrogen production
                        specific_energy_consumption = operation_funcion(P_nominal, P_in * 0.99)
                        hydrogen_production = (P_in / 60) / specific_energy_consumption
                        df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption
                        df.loc[df.index[i], 'heat [kW/h]'] = P_nominal * heat_funcion(P_nominal, P_in)
                        df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[i], 'power total [kW]'] - P_in
                    df.loc[df.index[i], 'hydrogen [Nm3]'] = hydrogen_production
            else:
                if df.loc[df.index[i], 'status'] == 'booting':
                    df.loc[df.index[i], 'heat energy loss [kW]'] = 0.0085 * quantile  # 0.85% of P_nominal energy losses for heat
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = P_in - (0.0085 * quantile)
                else:
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = P_in

        return df

    def production_combine(self, df):
        '''
        input: Df with P_in Data
        dt=1min
        Output: Df with Status, heat, hydrogen_production
        '''
        P_min = self.P_min
        long_gap_threshold = 60
        short_gap_threshold = 5

        quantile = df['power total [kW]'].quantile(0.80)
        print(quantile)
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
        for i in range(1, 31):
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
        P_nominal = self.P_nominal
        P_middle = P_nominal * 0.5
        # Load power curve data
        power_curve = pd.read_csv('../plots/my_power_curve.csv', sep=',', decimal='.', header=0)

        # Define function to calculate specific energy consumption
        def operation_funcion(P_nominal, P_in):
            '''
            :param P_nominal: nominal power of the electrolyzer
            :param P_in: actual power generation of the electrolyzer
            :return: specific energy consumption in kWh/Nm3 for P_in
            '''

            x = power_curve['relative power [%]'].to_numpy()
            x = (x * P_nominal) / 100
            y = power_curve['energy consumption [kWh/m3]'].to_numpy()

            f = interp1d(x, y, kind='linear')

            return f(P_in)

        def heat_funcion(P_nominal, P_in):
            '''
            calculate ind interpolate eta heat for each P_in
            '''
            x = [0.08,0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95,1.01]
            for i in range(len(x)):
                x[i] = x[i]*P_nominal
            y = [0.01,0.017,0.035,0.046,0.059,0.068,0.078,0.086,0.093,0.10,0.109,0.116,0.123,0.129,0.136,0.144,0.148,0.153,0.159,0.163]
            f = interp1d(x, y, kind='linear')
            return f(P_in)

        # Initialize new columns for hydrogen production, heat energy, and surplus electricity
        df['hydrogen [Nm3]'] = 0.0
        df['heat energy [kW/h]'] = 0.0
        df['Surplus electricity [kW]'] = 0.0
        df['heat [kW/h]'] = 0.0

        # Calculate hydrogen production, heat energy, and surplus electricity for each time step
        for i in range(len(df.index)):
            # Check if the status is 'production'
            P_in = df.loc[df.index[i], 'power total [kW]']
            if df.loc[df.index[i], 'status'] == 'production':
                # Check if the power generation is less than or equal to the quantile
                if df.loc[df.index[i], 'power total [kW]'] < quantile:
                    if df.loc[df.index[i], 'power total [kW]'] > P_middle: #and df.loc[df.index[i], 'power total [kW]'] <= P_nominal:
                        specific_energy_consumption = operation_funcion(P_nominal, P_middle * 0.99)
                        hydrogen_production = (P_middle / 60) / specific_energy_consumption
                        df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption
                        df.loc[df.index[i], 'heat [kW/h]'] = P_middle * heat_funcion(P_nominal, P_middle)
                        df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[
                            i], 'power total [kW]'] - P_middle
                    else: #P_in < P_middle
                        specific_energy_consumption = operation_funcion(P_nominal, P_in * 0.99)
                        hydrogen_production = (P_in / 60) / specific_energy_consumption
                        df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption
                        df.loc[df.index[i], 'heat [kW/h]'] = P_in * heat_funcion(P_nominal, P_in)
                        df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[
                            i], 'power total [kW]'] - P_in
                else:
                    if df.loc[df.index[i], 'power total [kW]'] <= P_nominal:
                        # Calculate hydrogen production using nominal power and specific energy consumption
                        specific_energy_consumption = operation_funcion(P_nominal, P_in * 0.99)
                        hydrogen_production = (P_in / 60) / specific_energy_consumption
                        df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption
                        df.loc[df.index[i], 'heat [kW/h]'] = P_in * heat_funcion(P_nominal, P_in)
                        df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[i], 'power total [kW]'] - P_in
                        # Update the hydrogen production column for the current time step
                    else:
                        # Calculate hydrogen production using nominal power and specific energy consumption
                        specific_energy_consumption = operation_funcion(P_nominal, P_nominal * 0.99)
                        hydrogen_production = (P_nominal / 60) / specific_energy_consumption
                        df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption
                        df.loc[df.index[i], 'heat [kW/h]'] = P_nominal * heat_funcion(P_nominal, P_nominal)
                        df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[i], 'power total [kW]'] - P_nominal
                        # Update the hydrogen production column for the current time step
                df.loc[df.index[i], 'hydrogen [Nm3]'] = hydrogen_production
            elif df.loc[df.index[i], 'status'] == 'booting':
                df.loc[df.index[i], 'heat energy loss [kW]'] = 0.0085 * P_nominal  # 0.85% of P_nominal energy losses for heat
                df.loc[df.index[i], 'Surplus electricity [kW]'] = P_in - (0.0085 * quantile)
            else:
                df.loc[df.index[i], 'Surplus electricity [kW]'] = P_in

        return df

    def modulation_pnenn(self, df):
        '''
        modulate simulation with p_nenn
        '''
        P_min = self.P_stack*0.2
        long_gap_threshold = 60
        short_gap_threshold = 5
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
        for i in range(1, 6):
            booting_mask |= (df['status'].eq('production') & df['status'].shift(i).eq('cold standby'))

        # Identify rows where production is True and status is hot standby for up to 30 rows before
        for i in range(1, 31):
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

        # Load power curve data
        power_curve = pd.read_csv('../plots/my_power_curve.csv', sep=',', decimal='.', header=0)

        # Define function to calculate specific energy consumption
        def operation_function(P_nominal, P_in):
            '''
            :param P_nominal: nominal power of the electrolyzer
            :param P_in: actual power generation of the electrolyzer
            :return: specific energy consumption in kWh/Nm3 for P_in
            '''

            x = power_curve['relative power [%]'].to_numpy()
            x = (x * P_nominal) / 100
            y = power_curve['energy consumption [kWh/m3]'].to_numpy()

            f = interp1d(x, y, kind='linear')

            return f(P_in)
        def heat_funcion(P_nominal, P_in):
            '''
            calculate ind interpolate eta heat for each P_in
            '''
            x = [0.08,0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95,1.01]
            for i in range(len(x)):
                x[i] = x[i]*P_nominal
            y = [0.01,0.017,0.035,0.046,0.059,0.068,0.078,0.086,0.093,0.10,0.109,0.116,0.123,0.129,0.136,0.144,0.148,0.153,0.159,0.163]
            f = interp1d(x, y, kind='linear')
            return f(P_in)

        # Initialize new columns for hydrogen production, heat energy, and surplus electricity
        df['hydrogen [Nm3]'] = 0.0
        df['heat energy [kW/h]'] = 0.0
        df['Surplus electricity [kW]'] = 0.0
        df['heat [kW/h]'] = 0.0

        #n_stacks = self.n_stacks
        n = 4
        P_stack = self.P_stack  # Assuming all stacks have the same P_nominal
        P_nominal = P_stack*n
        P_min_stack = P_stack * 0.2  # Assuming all stacks have the same P_min

        # Create column for hydrogen production of each stack

        for i in range(len(df.index)):
            # Check if the status is 'production'
            P_in = df.loc[df.index[i], 'power total [kW]']
            if df.loc[df.index[i], 'status'] == 'production':
                if P_in >= P_stack*1:
                    if P_in >= P_stack*2:
                        if P_in >= P_stack*3:
                            if P_in >= P_stack*4: #P_in bigger than electrolyzer
                                df.loc[df.index[i], 'stack 1'] = ((P_stack/60)) /operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'eta 1'] =  operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'stack 2'] = ((P_stack/60)) /operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'eta 2'] = operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'stack 3'] = ((P_stack/60)) /operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'eta 3'] = operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'stack 4'] = ((P_stack/60)) /operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'eta 4'] = operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'Surplus electricity [kW]'] = P_in-P_stack*4
                            else: #P_in between Stack 3 and 4
                                P_distributed = P_in - (P_stack*3)
                                df.loc[df.index[i], 'stack 1'] = (P_stack/60) / operation_function(P_stack,P_stack * 0.99)
                                df.loc[df.index[i], 'eta 1'] = operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'stack 2'] = (P_stack/60) / operation_function(P_stack,P_stack * 0.99)
                                df.loc[df.index[i], 'eta 2'] = operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'stack 3'] = (P_stack/ 60) / operation_function(P_stack,P_stack * 0.99)
                                df.loc[df.index[i], 'eta 3'] = operation_function(P_stack, P_stack * 0.99)
                                if P_distributed < P_stack * 0.25:
                                    df.loc[df.index[i], 'stack 4'] = (P_distributed/ 60) / 5.6
                                    df.loc[df.index[i], 'eta 4'] = 5.6
                                else:
                                    df.loc[df.index[i], 'stack 4'] = (P_distributed/ 60) / operation_function(P_stack,P_distributed * 0.99)
                                    df.loc[df.index[i], 'eta 4'] = operation_function(P_stack, P_distributed* 0.99)
                        else: #P_in between 3 and 4
                            P_distributed = P_in- (P_stack*2)
                            df.loc[df.index[i], 'stack 1'] = (P_stack / 60) / operation_function(P_stack,
                                                                                                       P_stack * 0.99)
                            df.loc[df.index[i], 'eta 1'] = operation_function(P_stack, P_stack * 0.99)
                            df.loc[df.index[i], 'stack 2'] = (P_stack / 60) / operation_function(P_stack,
                                                                                                       P_stack * 0.99)
                            df.loc[df.index[i], 'eta 2'] = operation_function(P_stack, P_stack * 0.99)
                            if P_distributed < P_stack * 0.25:
                                df.loc[df.index[i], 'stack 3'] = (P_distributed / 60) / 5.6
                                df.loc[df.index[i], 'eta 3'] = 5.6
                            else:
                                df.loc[df.index[i], 'stack 3'] = (P_distributed / 60) / operation_function(P_stack,
                                                                                                       P_distributed * 0.99)
                                df.loc[df.index[i], 'eta 3'] = operation_function(P_stack, P_distributed * 0.99)
                            df.loc[df.index[i], 'stack 4'] = 0.0
                    else: #P_in between 2 and 3
                        P_distributed = P_in - (P_stack)
                        df.loc[df.index[i], 'stack 1'] = (P_stack / 60) / operation_function(P_stack, P_stack* 0.99)
                        df.loc[df.index[i], 'eta 1'] = operation_function(P_stack, P_stack* 0.99)
                        if P_distributed < P_stack*0.25:
                            df.loc[df.index[i], 'stack 2'] = (P_distributed/60) / 5.6
                            df.loc[df.index[i], 'eta 2'] = 5.6
                        else:
                            df.loc[df.index[i], 'stack 2'] = (P_stack / 60) / operation_function(P_stack,
                                                                                                P_distributed * 0.99)
                            df.loc[df.index[i], 'eta 2'] = operation_function(P_stack, P_distributed * 0.99)

                        df.loc[df.index[i], 'stack 3'] = 0.0
                        df.loc[df.index[i], 'stack 4'] = 0.0
                else: #P_in between 1 and 2
                    df.loc[df.index[i], 'stack 1'] = (P_in / 60) / operation_function(P_stack, P_in * 0.99)
                    df.loc[df.index[i], 'eta 1'] = operation_function(P_stack, P_in * 0.99)
                    df.loc[df.index[i], 'stack 2'] = 0.0
                    df.loc[df.index[i], 'stack 3'] = 0.0
                    df.loc[df.index[i], 'stack 4'] = 0.0
            else:
                df.loc[df.index[i], 'Surplus electricity [kW]'] = P_in
                df.loc[df.index[i], 'stack 1'] = 0.0
                df.loc[df.index[i], 'stack 2'] = 0.0
                df.loc[df.index[i], 'stack 3'] = 0.0
                df.loc[df.index[i], 'stack 4'] = 0.0


        return df

    def modulation_eta(self, df):
        '''
        modulate simulation with optimize eta
        '''
        P_min = self.P_stack * 0.2
        long_gap_threshold = 60
        short_gap_threshold = 5
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
        for i in range(1, 6):
            booting_mask |= (df['status'].eq('production') & df['status'].shift(i).eq('cold standby'))

        # Identify rows where production is True and status is hot standby for up to 30 rows before
        for i in range(1, 31):
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
        # Load power curve data
        power_curve = pd.read_csv('../plots/my_power_curve.csv', sep=',', decimal='.', header=0)

        # Define function to calculate specific energy consumption
        def operation_function(P_nominal, P_in):
            '''
            :param P_nominal: nominal power of the electrolyzer
            :param P_in: actual power generation of the electrolyzer
            :return: specific energy consumption in kWh/Nm3 for P_in
            '''

            x = power_curve['relative power [%]'].to_numpy()
            x = (x * P_nominal) / 100
            y = power_curve['energy consumption [kWh/m3]'].to_numpy()

            f = interp1d(x, y, kind='linear')

            return f(P_in)
        def heat_funcion(P_nominal, P_in):
            '''
            calculate ind interpolate eta heat for each P_in
            '''
            x = [0.08,0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95,1.01]
            for i in range(len(x)):
                x[i] = x[i]*P_nominal
            y = [0.01,0.017,0.035,0.046,0.059,0.068,0.078,0.086,0.093,0.10,0.109,0.116,0.123,0.129,0.136,0.144,0.148,0.153,0.159,0.163]
            f = interp1d(x, y, kind='linear')
            return f(P_in)

        # Initialize new columns for hydrogen production, heat energy, and surplus electricity
        df['hydrogen [Nm3]'] = 0.0
        df['heat energy [kW/h]'] = 0.0
        df['Surplus electricity [kW]'] = 0.0
        df['heat [kW/h]'] = 0.0

        n_stacks = self.n_stacks
        P_stack = self.P_stack  # Assuming all stacks have the same P_nominal
        P_nominal = n_stacks*P_stack


        for i in range(len(df.index)):
            # Check if the status is 'production'
            P_in = df.loc[df.index[i], 'power total [kW]']
            if df.loc[df.index[i], 'status'] == 'production':
                if P_in > P_stack*1:
                    if P_in > P_stack*2:
                        if P_in > P_stack*3:
                            if P_in >= P_stack*4: #P_in bigger than electrolyzer
                                df.loc[df.index[i], 'stack 1'] = ((P_stack)) /operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'eta 1'] =  operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'stack 2'] = ((P_stack)) /operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'eta 2'] = operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'stack 3'] = ((P_stack)) /operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'eta 3'] = operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'stack 4'] = ((P_stack)) /operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'eta 4'] = operation_function(P_stack, P_stack * 0.99)
                                df.loc[df.index[i], 'Surplus electricity [kW]'] = P_in-P_stack*4
                            else: #P_in between Stack 3 and 4
                                P_distributed = P_in/4
                                df.loc[df.index[i], 'stack 1'] = (P_distributed) / operation_function(P_stack,P_distributed * 0.99)
                                df.loc[df.index[i], 'eta 1'] = operation_function(P_stack, P_distributed * 0.99)
                                df.loc[df.index[i], 'stack 2'] = (P_distributed) / operation_function(P_stack,P_distributed * 0.99)
                                df.loc[df.index[i], 'eta 2'] = operation_function(P_stack, P_distributed * 0.99)
                                df.loc[df.index[i], 'stack 3'] = (P_distributed / 1) / operation_function(P_stack,P_distributed * 0.99)
                                df.loc[df.index[i], 'eta 3'] = operation_function(P_stack, P_distributed * 0.99)
                                df.loc[df.index[i], 'stack 4'] = (P_distributed/ 1) / operation_function(P_stack,P_distributed * 0.99)
                                df.loc[df.index[i], 'eta 4'] = operation_function(P_stack, P_distributed* 0.99)
                        else: #P_in between 3 and 4
                            P_distributed = P_in / 3
                            df.loc[df.index[i], 'stack 1'] = (P_distributed / 1) / operation_function(P_stack,
                                                                                                       P_distributed * 0.99)
                            df.loc[df.index[i], 'eta 1'] = operation_function(P_stack, P_distributed * 0.99)
                            df.loc[df.index[i], 'stack 2'] = (P_distributed / 1) / operation_function(P_stack,
                                                                                                       P_distributed * 0.99)
                            df.loc[df.index[i], 'eta 2'] = operation_function(P_stack, P_distributed * 0.99)
                            df.loc[df.index[i], 'stack 3'] = (P_distributed / 1) / operation_function(P_stack,
                                                                                                       P_distributed * 0.99)
                            df.loc[df.index[i], 'eta 3'] = operation_function(P_stack, P_distributed * 0.99)
                            df.loc[df.index[i], 'stack 4'] = 0.0
                    else: #P_in between 2 and 3
                        P_distributed = P_in/2
                        df.loc[df.index[i], 'stack 1'] = (P_distributed / 1) / operation_function(P_stack,
                                                                                                   P_distributed * 0.99)
                        df.loc[df.index[i], 'eta 1'] = operation_function(P_stack, P_distributed* 0.99)
                        df.loc[df.index[i], 'stack 2'] = (P_distributed / 1) / operation_function(P_stack,
                                                                                                   P_distributed * 0.99)
                        df.loc[df.index[i], 'eta 2'] = operation_function(P_stack, P_distributed * 0.99)
                        df.loc[df.index[i], 'stack 3'] = 0.0
                        df.loc[df.index[i], 'stack 4'] = 0.0
                else: #P_in between 1 and 2
                    df.loc[df.index[i], 'stack 1'] = (P_in / 1) / operation_function(P_stack, P_in * 0.99)
                    df.loc[df.index[i], 'eta 1'] = operation_function(P_stack, P_in * 0.99)
                    df.loc[df.index[i], 'stack 2'] = 0.0
                    df.loc[df.index[i], 'stack 3'] = 0.0
                    df.loc[df.index[i], 'stack 4'] = 0.0
            else:
                df.loc[df.index[i], 'Surplus electricity [kW]'] = P_in
                df.loc[df.index[i], 'stack 1'] = 0.0
                df.loc[df.index[i], 'stack 2'] = 0.0
                df.loc[df.index[i], 'stack 3'] = 0.0
                df.loc[df.index[i], 'stack 4'] = 0.0

        return df



    def ratio(self, df):
        '''
        calculate the optimized ratio
        '''
        P_nominal = self.P_nominal
        P_min =  P_nominal * 0.12
        # Load power curve data
        power_curve = pd.read_csv('../plots/my_power_curve.csv', sep=',', decimal='.', header=0)

        # Define function to calculate specific energy consumption
        def operation_funcion(P_nominal, P_in):
            '''
            :param P_nominal: nominal power of the electrolyzer
            :param P_in: actual power generation of the electrolyzer
            :return: specific energy consumption in kWh/Nm3 for P_in
            '''

            x = power_curve['relative power [%]'].to_numpy()
            x = (x * P_nominal) / 100
            y = power_curve['energy consumption [kWh/m3]'].to_numpy()

            f = interp1d(x, y, kind='linear')

            return f(P_in)

        # Initialize new columns for hydrogen production, heat energy, and surplus electricity
        df['hydrogen [Nm3]'] = 0.0
        df['heat energy [kW/h]'] = 0.0
        df['Surplus electricity [kW]'] = 0.0
        df['heat [kW/h]'] = 0.0

        # Calculate hydrogen production, heat energy, and surplus electricity for each time step
        for i in range(len(df.index)):
            # Check if the status is 'production'
            if df.loc[df.index[i], 'power total [kW]'] >= P_min:
                # Check if the power generation is less than or equal to the nominal power
                if df.loc[df.index[i], 'power total [kW]'] <= P_nominal:
                    # Calculate specific energy consumption and hydrogen production
                    P_in = df.loc[df.index[i], 'power total [kW]']
                    specific_energy_consumption = operation_funcion(P_nominal, P_in * 0.99)
                    hydrogen_production = (P_in) / specific_energy_consumption
                    df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption
                    df.loc[df.index[i], 'energy consumption'] = P_in
                else:
                    # Calculate hydrogen production using nominal power and specific energy consumption
                    specific_energy_consumption = operation_funcion(P_nominal, P_nominal * 0.99)
                    hydrogen_production = (P_nominal) / specific_energy_consumption
                    df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption
                    df.loc[df.index[i], 'energy consumption'] = P_nominal

                # Update the hydrogen production column for the current time step
                df.loc[df.index[i], 'hydrogen [Nm3]'] = hydrogen_production

                # Check if the power generation is greater than the nominal power
                if df.loc[df.index[i], 'power total [kW]'] > P_nominal:
                    # Calculate surplus electricity
                    surplus_electricity = df.loc[df.index[i], 'power total [kW]'] - P_nominal
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = surplus_electricity
                elif df.loc[df.index[i], 'power total [kW]'] < P_nominal:
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[i], 'power total [kW]']
                else:
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = 0


            # Check if the status is 'booting'
            #if df.loc[df.index[i], 'status'] == 'booting':
            #    # Set heat energy to 8.5 kW
            #    df.loc[df.index[i], 'heat energy [kW/h]'] = 8.5
            #if df.loc[df.index[i], 'status'] == 'production':
            #   df.loc[df.index[i], 'heat [kW/h]'] = P_nominal * 0.167

        return df

    def operate_middle(self, df):
        '''
        dt=1min
        '''
        P_min = self.P_min
        quantile15 = df['power total [kW]'].quantile(0.15)
        quantile40 = df['power total [kW]'].quantile(0.40)
        long_gap_threshold = 60
        short_gap_threshold = 5
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
        for i in range(1, 6):
            booting_mask |= (df['status'].eq('production') & df['status'].shift(i).eq('cold standby'))

        # Identify rows where production is True and status is hot standby for up to 30 rows before
        for i in range(1, 31):
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
        P_nominal = self.P_nominal
        # Load power curve data
        power_curve = pd.read_csv('../plots/my_power_curve.csv', sep=',', decimal='.', header=0)

        # Define function to calculate specific energy consumption
        def operation_funcion(P_nominal, P_in):
            '''
            :param P_nominal: nominal power of the electrolyzer
            :param P_in: actual power generation of the electrolyzer
            :return: specific energy consumption in kWh/Nm3 for P_in
            '''

            x = power_curve['relative power [%]'].to_numpy()
            x = (x * P_nominal) / 100
            y = power_curve['energy consumption [kWh/m3]'].to_numpy()

            f = interp1d(x, y, kind='linear')

            return f(P_in)

        def heat_funcion(P_nominal, P_in):
            '''
            calculate ind interpolate eta heat for each P_in
            '''
            x = [0.08,0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95,1.01]
            for i in range(len(x)):
                x[i] = x[i]*P_nominal
            y = [0.01,0.017,0.035,0.046,0.059,0.068,0.078,0.086,0.093,0.10,0.109,0.116,0.123,0.129,0.136,0.144,0.148,0.153,0.159,0.163]
            f = interp1d(x, y, kind='linear')
            return f(P_in)

        # Initialize new columns for hydrogen production, heat energy, and surplus electricity
        df['hydrogen [Nm3]'] = 0.0
        df['heat energy [kW/h]'] = 0.0
        df['Surplus electricity [kW]'] = 0.0
        df['heat [kW/h]'] = 0.0

        # Calculate hydrogen production, heat energy, and surplus electricity for each time step
        for i in range(len(df.index)):
            if df.loc[df.index[i], 'power total [kW]'] < quantile40 and df.loc[df.index[i], 'power total [kW]'] > quantile15:
                # Check if the status is 'production'
                if df.loc[df.index[i], 'status'] == 'production':
                    # Check if the power generation is less than or equal to the nominal power
                    if df.loc[df.index[i], 'power total [kW]'] <= P_nominal:
                        # Calculate specific energy consumption and hydrogen production
                        P_in = df.loc[df.index[i], 'power total [kW]']
                        specific_energy_consumption = operation_funcion(P_nominal, P_in * 0.99)
                        hydrogen_production = (P_in / 60) / specific_energy_consumption
                        df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption
                    else:
                        # Calculate hydrogen production using nominal power and specific energy consumption
                        specific_energy_consumption = operation_funcion(P_nominal, P_nominal * 0.99)
                        hydrogen_production = (P_nominal / 60) / specific_energy_consumption
                        df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption

                # Update the hydrogen production column for the current time step
                df.loc[df.index[i], 'hydrogen [Nm3]'] = hydrogen_production

                # Check if the power generation is greater than the nominal power
                if df.loc[df.index[i], 'power total [kW]'] > P_nominal:
                    # Calculate surplus electricity
                    surplus_electricity = df.loc[df.index[i], 'power total [kW]'] - P_nominal
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = surplus_electricity
                elif df.loc[df.index[i], 'power total [kW]'] < P_nominal:
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[i], 'power total [kW]']
                else:
                    df.loc[df.index[i], 'Surplus electricity [kW]'] = 0

            # Check if the status is 'booting'
            if df.loc[df.index[i], 'status'] == 'booting':
                # Set heat energy to 8.5 kW
                df.loc[df.index[i], 'heat energy [kW/h]'] = 8.5
            if df.loc[df.index[i], 'status'] == 'production':
                df.loc[df.index[i], 'heat [kW/h]'] = P_nominal * heat_funcion(P_nominal, P_in)

        return df


    def production_costs_optimization(self, df):
        '''
        dt=1min

        '''
        price = pd.read_csv('../prices/day_ahead_prices_2015_ger.csv', sep=';', header=0, index_col=0, decimal=',',
                            date_parser=lambda idx: pd.to_datetime(idx, utc=True))
        price = price.resample('1min').interpolate(method='linear')
        price = price.loc['2015-01-01 00:00:00+00:00':'2015-12-31 23:45:00+00:00']
        df['Day-ahead Price [EUR/kWh]'] = price[' Day-ahead Price [EUR/kWh] ']
        P_min = self.P_min
        long_gap_threshold = 60
        short_gap_threshold = 5

        #quantile = df['Day-ahead Price [EUR/kWh]'].quantile(0.60)
        quantile = 0.04
        print(quantile)
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
        for i in range(1, 31):
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
        P_nominal = self.P_nominal
        P_middle = P_nominal * 0.5
        # Load power curve data
        power_curve = pd.read_csv('../plots/my_power_curve.csv', sep=',', decimal='.', header=0)

        # Define function to calculate specific energy consumption
        def operation_funcion(P_nominal, P_in):
            '''
            :param P_nominal: nominal power of the electrolyzer
            :param P_in: actual power generation of the electrolyzer
            :return: specific energy consumption in kWh/Nm3 for P_in
            '''

            x = power_curve['relative power [%]'].to_numpy()
            x = (x * P_nominal) / 100
            y = power_curve['energy consumption [kWh/m3]'].to_numpy()

            f = interp1d(x, y, kind='linear')

            return f(P_in)

        def heat_funcion(P_nominal, P_in):
            '''
            calculate ind interpolate eta heat for each P_in
            '''
            x = [0.08,0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95,1.01]
            for i in range(len(x)):
                x[i] = x[i]*P_nominal
            y = [0.01,0.017,0.035,0.046,0.059,0.068,0.078,0.086,0.093,0.10,0.109,0.116,0.123,0.129,0.136,0.144,0.148,0.153,0.159,0.163]
            f = interp1d(x, y, kind='linear')
            return f(P_in)

        # Initialize new columns for hydrogen production, heat energy, and surplus electricity
        df['hydrogen [Nm3]'] = 0.0
        df['heat energy [kW/h]'] = 0.0
        df['Surplus electricity [kW]'] = 0.0
        df['heat [kW/h]'] = 0.0

        # Calculate hydrogen production, heat energy, and surplus electricity for each time step
        for i in range(len(df.index)):
            # Check if the status is 'production'
            P_in = df.loc[df.index[i], 'power total [kW]']
            if df.loc[df.index[i], 'status'] == 'production':
                # Check if the power generation is less than or equal to the quantile
                if df.loc[df.index[i], 'Day-ahead Price [EUR/kWh]'] <= quantile:
                    if df.loc[df.index[i], 'power total [kW]'] > P_middle: #and df.loc[df.index[i], 'power total [kW]'] <= P_nominal:
                        specific_energy_consumption = operation_funcion(P_nominal, P_middle * 0.99)
                        hydrogen_production = (P_middle / 60) / specific_energy_consumption
                        df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption
                        df.loc[df.index[i], 'heat [kW/h]'] = P_middle * heat_funcion(P_nominal, P_middle)
                        df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[
                            i], 'power total [kW]'] - P_middle
                    else: #P_in < P_middle
                        specific_energy_consumption = operation_funcion(P_nominal, P_in * 0.99)
                        hydrogen_production = (P_in / 60) / specific_energy_consumption
                        df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption
                        df.loc[df.index[i], 'heat [kW/h]'] = P_in * heat_funcion(P_nominal, P_in)
                        df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[
                            i], 'power total [kW]'] - P_in
                else:
                    if df.loc[df.index[i], 'power total [kW]'] <= P_nominal:
                        # Calculate hydrogen production using nominal power and specific energy consumption
                        specific_energy_consumption = operation_funcion(P_nominal, P_in * 0.99)
                        hydrogen_production = (P_in / 60) / specific_energy_consumption
                        df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption
                        df.loc[df.index[i], 'heat [kW/h]'] = P_in * heat_funcion(P_nominal, P_in)
                        df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[i], 'power total [kW]'] - P_in
                        # Update the hydrogen production column for the current time step
                    else:
                        # Calculate hydrogen production using nominal power and specific energy consumption
                        specific_energy_consumption = operation_funcion(P_nominal, P_nominal * 0.99)
                        hydrogen_production = (P_nominal / 60) / specific_energy_consumption
                        df.loc[df.index[i], 'specific consumption'] = specific_energy_consumption
                        df.loc[df.index[i], 'heat [kW/h]'] = P_nominal * heat_funcion(P_nominal, P_nominal)
                        df.loc[df.index[i], 'Surplus electricity [kW]'] = df.loc[df.index[i], 'power total [kW]'] - P_nominal
                        # Update the hydrogen production column for the current time step
                df.loc[df.index[i], 'hydrogen [Nm3]'] = hydrogen_production
            elif df.loc[df.index[i], 'status'] == 'booting':
                df.loc[df.index[i], 'heat energy loss [kW]'] = 0.0085 * P_nominal  # 0.85% of P_nominal energy losses for heat
                df.loc[df.index[i], 'Surplus electricity [kW]'] = P_in - (0.0085 * quantile)
            else:
                df.loc[df.index[i], 'Surplus electricity [kW]'] = P_in

        return df