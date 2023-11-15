import matplotlib.pyplot as plt

from vpplib.environment import Environment

def check_obs_mos_result():
    
    latitude = 51.4041
    longitude = 6.9677
    
    Uhrzeit = "2023-11-15 17:00:00+01:00"
    
    start_obs = "2023-11-15 00:00:00"
    
    start_mos = "2023-11-15 18:00:00"
    end_mos   = "2024-11-19 23:00:00"
    end_obs   = end_mos #Nicht vorhandene observation daten werden abgeschnitten
    
    """
    PV
    
    #OBSERVATION Abfrage
    environment_obs = Environment(start=start_obs, end=end_obs,surpress_output_globally=True)
    environment_obs.get_dwd_pv_data(lat=latitude, lon=longitude)
    #Plotte den letzten Tag
    obs_start_plt = environment_obs.pv_data.index[len(environment_obs.pv_data.index)-4*24]
    obs_end_plt   = environment_obs.pv_data.index[-1]
    environment_obs.pv_data[obs_start_plt:obs_end_plt].plot()
    plt.title('OBS Start Date: ' + str(obs_start_plt))
    plt.show()
    
    #Mosmix Abfrage
    environment_mos = Environment(start=start_mos, end=end_mos,surpress_output_globally=True)
    environment_mos.get_dwd_pv_data(lat=latitude, lon=longitude)
    #Plotte den 1. Tag
    environment_mos.pv_data[environment_mos.pv_data.index[0]:environment_mos.pv_data.index[25*4]].plot()
    plt.title('MOS Start Date: ' + str(environment_mos.pv_data.index[0]))
    plt.show()
    
    #Vergleiche 2 Uhrzeiten
    date = environment_obs.pv_data.index[-1]
    date_1 = environment_mos.pv_data.index[-1]
    
    print(environment_obs.pv_data.loc[date])
    print(environment_mos.pv_data.loc[date_1])
    """
    
    """
    Temp
    
    #OBSERVATION Abfrage
    environment_obs = Environment(start=start_obs, end=end_obs,time_freq = '60 min',surpress_output_globally=True)
    environment_obs.get_dwd_mean_temp_hours(lat=latitude, lon=longitude)
    #Plotte den letzten Tag
    obs_start_plt = environment_obs.mean_temp_hours.index[len(environment_obs.mean_temp_hours.index)-12]
    obs_end_plt   = environment_obs.mean_temp_hours.index[-1]
    environment_obs.mean_temp_hours[obs_start_plt:obs_end_plt].plot()
    plt.title('OBS Start Date: ' + str(obs_start_plt))
    plt.show()
    
    #Mosmix Abfrage
    environment_mos = Environment(start=start_mos, end=end_mos, time_freq = '60 min',surpress_output_globally=True)
    environment_mos.get_dwd_mean_temp_hours(lat=latitude, lon=longitude)
    #Plotte den 1. Tag
    environment_mos.mean_temp_hours[environment_mos.mean_temp_hours.index[0]:environment_mos.mean_temp_hours.index[12]].plot()
    plt.title('MOS Start Date: ' + str(environment_mos.mean_temp_hours.index[0]))
    plt.show()
    
    #Vergleiche 2 Uhrzeiten
    #Vergleiche 2 Uhrzeiten
    date = environment_obs.mean_temp_hours.index[-1]
    date_1 = environment_mos.mean_temp_hours.index[-1]

    print(environment_obs.mean_temp_hours.loc[date])
    print(environment_mos.mean_temp_hours.loc[date_1])
    """
    
    """
    Wind
    
    environment_obs = Environment(start=start_obs, end=end_obs,surpress_output_globally=True)
    environment_obs.get_dwd_wind_data(lat=latitude, lon=longitude)
    #Plotte den letzten Tag
    obs_start_plt = environment_obs.wind_data.index[len(environment_obs.wind_data.index)-4*24]
    obs_end_plt   = environment_obs.wind_data.index[-1]
    environment_obs.wind_data[obs_start_plt:obs_end_plt].plot()
    plt.title('OBS Start Date: ' + str(obs_start_plt))
    plt.show()
    
    #Mosmix Abfrage
    environment_mos = Environment(start=start_mos, end=end_mos,surpress_output_globally=True)
    environment_mos.get_dwd_wind_data(lat=latitude, lon=longitude)
    #Plotte den 1. Tag
    environment_mos.wind_data[environment_mos.wind_data.index[0]:environment_mos.wind_data.index[25*4]].plot()
    plt.title('MOS Start Date: ' + str(environment_mos.wind_data.index[0]))
    plt.show()
    
    date = environment_obs.wind_data.index[-1]
    date_1 = environment_mos.wind_data.index[-1]
    
    #Vergleiche 2 Uhrzeiten
    print(environment_obs.wind_data.loc[date])
    print(environment_mos.wind_data.loc[date_1])
    """


def check_dwd_csv_result():

    """
    Prüfe csv und dwd ergebnis
    """
    
    latitude = 50.941357
    longitude = 6.958307
    identifier = "Cologne"
    start = "2015-01-01 00:00:00"
    end = "2015-12-31 23:45:00"
    timestamp_int = 48
    timestamp_str = "2015-06-05 12:00:00"
    environment = Environment(start=start, end=end)
    
    """
    #PV
    environment.get_pv_data(file="./input/pv/dwd_pv_data_2015.csv")
    pv_sascha_csv = environment.pv_data[start:end]
    
    environment.get_dwd_pv_data(lat=latitude, lon=longitude)
    pv_sascha_dwd = environment.pv_data
    
    pv_sascha_csv.reset_index(inplace = True)
    pv_sascha_csv = pv_sascha_csv.drop('time', axis = 1)
    pv_sascha_csv = pv_sascha_csv.reindex(sorted(pv_sascha_csv.columns), axis=1)
    pv_sascha_csv = round(pv_sascha_csv,2)
    
    pv_sascha_dwd.reset_index(inplace = True)
    pv_sascha_dwd = pv_sascha_dwd.drop('time', axis = 1)
    pv_sascha_dwd = pv_sascha_dwd.shift(-8).fillna(0)
    
    if not pv_sascha_csv.equals(pv_sascha_dwd):
        print("non equal PV dfs")
        return 0
    print("PV dataframes are equal")
    #Zeitverschiebung in csv df nicht beachtet
    #Reigenfolge der columns ungleich
    #df unterscheiden sich nach frühestens der 3. Nachkommastelle
    #csv output datei ist nicht innerhalb start:end sonder über das ganze Jahr
    
    """
    #Wind
    environment.get_wind_data(file="./input/wind/dwd_wind_data_2015.csv", utc=False)
    wind_sascha_csv = environment.wind_data
    
    wind_sascha_csv.reset_index(inplace = True)
    wind_sascha_csv = wind_sascha_csv.drop('Time', axis = 1)
    wind_sascha_csv = wind_sascha_csv.reindex(sorted(wind_sascha_csv.columns), axis=1)
    wind_sascha_csv = round(wind_sascha_csv,2)
    
    environment.get_dwd_wind_data(lat=latitude, lon=longitude)
    wind_sascha_dwd = environment.wind_data
    wind_sascha_dwd.reset_index(inplace = True)
    wind_sascha_dwd = wind_sascha_dwd.drop('time', axis = 1)
    wind_sascha_dwd = wind_sascha_dwd.shift(-4).fillna(0)
    
    if not  wind_sascha_dwd.equals(wind_sascha_csv):
        print("non equal wind dfs")
        return 0
    
    print("Wind dataframes are equal")
    #Wie bei pv +:
    # time/Time
    
    """
    #Temp
    
    environment = Environment(start=start, end=end,time_freq= '60 min')
    environment.get_mean_temp_hours()
    temp_sascha_csv = environment.mean_temp_hours#[start:end]
    
    temp_sascha_csv.reset_index(inplace = True)
    temp_sascha_csv = temp_sascha_csv.drop('time', axis = 1)
    #temp_sascha_csv = temp_sascha_csv.reindex(sorted(temp_sascha_csv.columns), axis=1)
    temp_sascha_csv = round(temp_sascha_csv,0)
    temp_sascha_csv.temperature[temp_sascha_csv.index[-1]] = 0
    temp_sascha_csv.temperature[temp_sascha_csv.index[-1]-1] = 0
    
    
    environment.get_dwd_temp_data(lat=latitude, lon=longitude)
    temp_sascha_dwd = environment.mean_temp_hours
    temp_sascha_dwd.reset_index(inplace = True)
    temp_sascha_dwd = temp_sascha_dwd.drop(['time'], axis = 1)
    temp_sascha_dwd = round(temp_sascha_dwd,0)
    temp_sascha_dwd = temp_sascha_dwd.shift(-2).fillna(0)
    
    for index in temp_sascha_csv.index:
        if not temp_sascha_csv[index] == temp_sascha_dwd[index]:
            1
    
    if not  temp_sascha_csv.equals(temp_sascha_dwd):
        print("non equal temp dfs")
        return 0
    
    print("twmp dataframes are equal")
    """
    return 1
    
if check_dwd_csv_result():
    print("csv/dwd dfs ok")
    #check_obs_mos_result()
else:
    print("invalid data")







