import schedule
import time
import datetime
import pandas as pd
from vpplib.environment import Environment
import os
dir_path = os.path.dirname(os.path.realpath(__file__))

"""
Change your settings here 
"""
path_output_main = dir_path + "/dwd_results/"    
"hourly or daily"
frequency = 'daily'
resolution = '60 min'
distance = 100
surpress_output_globally = False
force_end_time = True
min_quality_per_parameter = 10
run_time_hours = 0 #should be max 238 hours. If run_time_hours = 0 the script will run in infinite loop
dict_locations = {
    'Bedburg':      {'latitude': 51.01, 'longitude': 6.31},
    'Köln':         {'latitude': 50.97, 'longitude': 6.97},
    'Essen':        {'latitude': 51.40, 'longitude': 6.97},  
}

if not os.path.exists(path_output_main):
    os.mkdir(path_output_main)
for key in dict_locations:
    dir_path_key = path_output_main +'/'+ str(key)
    if not os.path.exists(dir_path_key):
        os.mkdir(dir_path_key)
         
#Get actual time from dwd server (UTC)
time_start = Environment().get_time_from_dwd().replace(tzinfo=None)
forecast_end_time = time_start + datetime.timedelta(hours = run_time_hours + 2)
plot_next_run_flag = False

if frequency == 'daily':
    #Set shedule time for daily run. First run triggered by run_get_dwd_data() so the first shedule run is time_now+23h58min
    shedule_time = datetime.datetime.now() + datetime.timedelta(hours=23, minutes = 58)
    str_shedule_time = str(shedule_time.hour).zfill(2) + ':00'
elif frequency == 'hourly':
    shedule_time = datetime.datetime.now() + datetime.timedelta(minutes = 2)
    str_shedule_time =':' + str(shedule_time.minute).zfill(2)
else:
    raise Exception("unknown frequency")


print("Shedule time: " + str_shedule_time)
print("----------------------------------")

def create_csv(meta_1,data_1,meta_2,data_2,out_path):
    """
    create csv file with meta header and data
    """
    
    meta_1_sorted = pd.DataFrame(index = meta_1.to_dict(orient='dict').keys(), data = meta_1.to_dict(orient='dict').values())
    concat_df_1 = pd.concat([meta_1_sorted, data_1], axis=1)
    
    meta_2_sorted = pd.DataFrame(index = meta_2.to_dict(orient='dict').keys(), data = meta_2.to_dict(orient='dict').values())
    concat_df_2 = pd.concat([meta_2_sorted, data_2], axis=1)
    
    out_df = pd.concat([concat_df_1,concat_df_2], axis = 1)
    
    out_df.to_csv(out_path, sep = ';')

def run_get_dwd_data(test_run = False):
    global forecast_end_time
    global plot_next_run_flag
    if test_run:
        print("Start test run")
    time_now_dwd = Environment().get_time_from_dwd().replace(tzinfo=None)
    print(time_now_dwd)
    if run_time_hours == 0:
        forecast_end_time = time_now_dwd.replace(minute=0,second=0) + datetime.timedelta(hours = 240)
    for location in dict_locations:
        #print("Query weather data for " + str(location))
        latitude  = dict_locations[location]['latitude']
        longitude = dict_locations[location]['longitude']

        """OBSERVATION: """
        if test_run or time_start + datetime.timedelta(hours=1) <= time_now_dwd:
                obs_environment = Environment(
                    start=str(time_start - datetime.timedelta(hours=2)) if test_run else str(time_start), 
                    end=str(time_now_dwd),
                    time_freq=resolution,
                    surpress_output_globally=surpress_output_globally, 
                    force_end_time= force_end_time)
                print("Query Observation data for " + str(location) + " lat: " + str(latitude) + " lon: " + str(longitude))
                print("Start: " + str(obs_environment.start) +  " End: " + str(obs_environment.end))
                pv_obs_meta     = obs_environment.get_dwd_pv_data  (lat=latitude, lon=longitude, distance=distance, min_quality_per_parameter=min_quality_per_parameter)
                wind_obs_meta   = obs_environment.get_dwd_wind_data(lat=latitude, lon=longitude, distance=distance, min_quality_per_parameter=min_quality_per_parameter)
                if not test_run:
                    obs_out = path_output_main + location + '/obs_'+ str(time_now_dwd.year) + str(time_now_dwd.month).zfill(2) + str(time_now_dwd.day).zfill(2) + str(time_now_dwd.hour).zfill(2) +  str(time_now_dwd.minute).zfill(2) + '.csv'
                    create_csv(
                        pv_obs_meta,
                        obs_environment.pv_data,
                        wind_obs_meta,
                        obs_environment.wind_data,
                        obs_out)
        else:
            print("Skipping observation query. Difftime: " + str(time_now_dwd - time_start) + " < 1 hour")
                
        if time_now_dwd + datetime.timedelta(hours=1) < forecast_end_time:
            """MOSMIX: """
            mos_environment = Environment(start=str(time_now_dwd), end=str(forecast_end_time),time_freq=resolution,surpress_output_globally=surpress_output_globally, force_end_time= force_end_time)
            print("Query Mosmix data for " + str(location)+ " lat: " + str(latitude) + " lon: " + str(longitude))
            print("Start: " + str(mos_environment.start) +  " End: " + str(mos_environment.end))
            pv_mos_meta     = mos_environment.get_dwd_pv_data  (lat=latitude, lon=longitude, distance=distance, min_quality_per_parameter=min_quality_per_parameter, estimation_methode_lst=['disc','erbs','dirint','boland'])
            wind_mos_meta   = mos_environment.get_dwd_wind_data(lat=latitude, lon=longitude, distance=distance, min_quality_per_parameter=min_quality_per_parameter)
            if not test_run:
                mos_out = path_output_main + location  +'/mos_'+ str(time_now_dwd.year) + str(time_now_dwd.month).zfill(2) + str(time_now_dwd.day).zfill(2) + str(time_now_dwd.hour).zfill(2) +  str(time_now_dwd.minute).zfill(2) + '.csv'
                create_csv(
                    pv_mos_meta,
                    mos_environment.pv_data,
                    wind_mos_meta,
                    mos_environment.wind_data,
                    mos_out)
    
    if test_run:
        print("Test run successful")
        print("----------------------------------")
    else:
       plot_next_run_flag = True  
       
run_get_dwd_data(test_run=True)

if frequency == 'daily':
    # Schedule the job to run once a day at a specific time
    schedule.every().day.at(str_shedule_time).do(run_get_dwd_data)
    #First run
    run_get_dwd_data()
elif frequency == 'hourly':
    print("First run in 2 minutes")
    schedule.every().hour.at(str_shedule_time).do(run_get_dwd_data)

# Keep the script running
while True:
    if plot_next_run_flag:
        print("Next run:" ,schedule.next_run())
        plot_next_run_flag = False
    
    n = schedule.idle_seconds()
    if n is None or run_time_hours != 0 and schedule.next_run() >= time_start + datetime.timedelta(hours = run_time_hours):
        print("End period reached")
        raise SystemExit(0)
    elif n > 0:
        time.sleep(int(n/2))
    schedule.run_pending()