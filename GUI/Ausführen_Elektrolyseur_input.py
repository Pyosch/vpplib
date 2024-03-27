# -*- coding: utf-8 -*-

import pandas as pd
from hydrogen_electrolyseur import ElectrolysisMoritz 

#-------------------------------------------------------------------------------------------------
#test mit input
def simulate_electrolyzer(store_hydrogen, store_environment, store_basic_settings):
    """
    Simulates the operation of an electrolyzer based on the provided input parameters.
    The results are stored in a CSV file.

    Args:
        store_hydrogen (dict): A dictionary containing hydrogen storage parameters.
        store_environment (dict): A dictionary containing environmental parameters.
        store_basic_settings (dict): A dictionary containing basic settings.

    Returns:
        None
    """
    aa = str(store_hydrogen['Power_Electrolyzer'])+'kW'
    a = ''.join([c for c in aa if c.isnumeric() or c == '.'])
    b = ''.join([c for c in aa if c.isalpha()])

    # ---------------------------------------------------------------------------

    cc = store_environment['Time Step']
    c = ''.join([c for c in cc if c.isnumeric() or c == '.'])
    d = ''.join([c for c in cc if c.isalpha()])

    # ---------------------------------------------------------------------------
    x = int((pd.to_datetime(store_environment['End Date'])-pd.to_datetime(store_environment['Start Date'])).days)
    # print(x)
    # print(type(x))
    try:
        if store_environment['Time Step'] == '1 day':
            Zeitschritte = int(x)
        else:
            Zeitschritte = int(x*24*60/int(c))
    except ValueError:
        print("Ungültige Eingabe. Bitte geben Sie eine ganze Zahl ein.")
    #-------------------------------------------------------------------------------

    e = store_hydrogen['Pressure_Hydrogen']

    # ---------------------------------------------------------------------------

   
    ff = str('0' +'kg')
    if not ff.strip():
        f=""
        g=""
    else:
        f = ''.join([c for c in ff if c.isnumeric() or c == '.'])
        g = ''.join([c for c in ff if c.isalpha()])

    electrolyzer = ElectrolysisMoritz(a,b,c,d,e,f,g)
    #--------------------------------------------------------------------------------------------------------------------------

    #Import der Eingangsleistung

    ts=pd.read_csv(r'GUI/csv-files/df_timeseries.csv', sep=',', decimal='.',nrows=Zeitschritte)
    ts['P_ac']=ts.iloc[:, 1:].sum(axis=1)
    ts.set_index('time')
    electrolyzer.prepare_timeseries(ts)

    #CSV-Datei
    ts.to_csv(r'GUI/csv-files/hydrogen_time_series.csv', index=False)
  
