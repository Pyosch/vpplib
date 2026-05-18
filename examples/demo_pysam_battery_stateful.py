from vpplib.environment import Environment
from vpplib.electrical_energy_storage import PySAMBatteryStateful
from vpplib.photovoltaic import Photovoltaic

import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Reference period: yesterday going back one year
yesterday = datetime.date.today() - datetime.timedelta(days=1)
ref_start = yesterday.replace(year=yesterday.year - 1)

# Simulation window: a summer week within the reference year for PV generation
start = f"{ref_start.year}-06-15 00:00:00"
end = f"{ref_start.year}-06-21 23:45:00"
timebase = 15

# user_profile
latitude = 50.941357
longitude = 6.958307

# PV
unit = "kW"
name = "bus"
module_lib = "SandiaMod"
module = "Canadian_Solar_CS5P_220M___2009_"
inverter_lib = "cecinverter"
inverter = "Connect_Renewable_Energy__CE_4000__240V_"
surface_tilt = 20
surface_azimuth = 200
modules_per_string = 4
strings_per_inverter = 2
temp_lib = 'sapm'
temp_model = 'open_rack_glass_glass'

# storage
nominal_energy=20

# test
timestamp_int = 48
timestamp_str = f"{ref_start.year}-06-15 12:00:00"


environment = Environment(timebase=timebase, start=start, end=end, surpress_output_globally=False)
environment.get_dwd_pv_data(lat=latitude, lon=longitude)

# create pv object and timeseries
pv = Photovoltaic(
    unit=unit,
    latitude=latitude,
    longitude=longitude,
    identifier=(name + "_pv"),
    environment=environment,
    module_lib=module_lib,
    module=module,
    inverter_lib=inverter_lib,
    inverter=inverter,
    surface_tilt=surface_tilt,
    surface_azimuth=surface_azimuth,
    modules_per_string=modules_per_string,
    strings_per_inverter=strings_per_inverter,
    temp_lib=temp_lib,
    temp_model=temp_model
)

pv.prepare_time_series()

baseload = pd.read_csv("./input/baseload/df_S_15min.csv")
baseload.drop(columns=["Time"], inplace=True)
# Re-index baseload to pv timeseries index so alignment is guaranteed
baseload = baseload.iloc[:len(pv.timeseries)].copy()
baseload.index = pv.timeseries.index

# combine baseload and pv timeseries to get residual load
house_loadshape = pd.DataFrame(baseload["0"] / 1000)
house_loadshape["pv_gen"] = pv.timeseries
house_loadshape["residual_load"] = (
    baseload["0"] / 1000 - pv.timeseries[name + "_pv"]
)

# create storage object and timeseries
storage = PySAMBatteryStateful(
    identifier=(name + "_storage"),
    environment=environment,
    unit=None
)

storage.init_battery_stateful(nominal_energy=nominal_energy,
                              nominal_voltage=500,
                              Vnom_default=3.600, resistance=0.0001,
                              Vfull=4.100, Vexp=4.050, Vnom=3.400,
                              Qfull=2.250, Qexp=0.040, Qnom=2.000,
                              C_rate=0.200, Vcut=2,
                              initial_SOC=50.0, maximum_SOC=95.0, minimum_SOC=5.0)

# assign residual load to storage
storage.residual_load = house_loadshape.residual_load

def test_operate_storage(storage, timestamp):

    print("operate_storage:")
    state_of_charge, ac_power = storage.operate_storage(
        storage.residual_load.loc[timestamp]
    )
    print("state_of_charge: ", state_of_charge)
    print("ac_power: ", ac_power)


def test_prepare_time_series(storage):

    storage.prepare_time_series()
    print("prepare_time_series:")
    print(storage.timeseries.head())
    storage.timeseries.plot(figsize=(16, 9))
    plt.show()


def test_value_for_timestamp(storage, timestamp):

    timestepvalue = storage.value_for_timestamp(timestamp)
    print("\nvalue_for_timestamp:\n", timestepvalue)


def test_observations_for_timestamp(storage, timestamp):

    print("observations_for_timestamp:")
    observation = storage.observations_for_timestamp(timestamp)
    print(observation, "\n")


test_operate_storage(storage, timestamp_str)

test_prepare_time_series(storage)

test_value_for_timestamp(storage, timestamp_int)
test_value_for_timestamp(storage, timestamp_str)

test_observations_for_timestamp(storage, timestamp_int)
test_observations_for_timestamp(storage, timestamp_str)
