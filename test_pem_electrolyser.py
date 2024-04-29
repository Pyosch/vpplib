import os
import pandas as pd
from vpplib.hydrogen import ElectrolysisPEM 

dir_path = os.path.dirname(os.path.realpath(__file__))
#Read generation data
ts = pd.read_csv(f'{dir_path}/input/hydrogen/Electrolyzer_wind_energy_cologne.csv',sep=',', decimal='.',nrows=20)

#Power adjustment
ts['P_ac'] = round(ts['P_ac']/100,2)

electrolyzer = ElectrolysisPEM(
                P_elektrolyseur_="1.5",
                unit_P="mw",
                dt_1="15",
                unit_dt="m",
                p2="750",
                production_H2_="0",
                unit_production_H2="kg")

#Execute electrolyzer
electrolyzer.prepare_timeseries(ts)
print(ts)

timestamp_int=10
timestamp_str="2015-01-01 02:30:00+00:00"

def test_value_for_timestamp(electrolyzer, timestamp):
    
    timestepvalue = electrolyzer.value_for_timestamp(timestamp)
    print("\nvalue_for_timestamp:\n", timestepvalue)

def test_observations_for_timestamp(electrolyzer, timestamp):

    print("observations_for_timestamp:")
    
    observation = electrolyzer.observations_for_timestamp(timestamp)
    print(observation, "\n")

test_value_for_timestamp(electrolyzer, timestamp_int)
test_value_for_timestamp(electrolyzer, timestamp_str)

test_observations_for_timestamp(electrolyzer, timestamp_int)
test_observations_for_timestamp(electrolyzer,timestamp_str)
