# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 13:25:23 2019

@author: Sascha Birk
"""
import pandas as pd
import matplotlib.pyplot as plt

from vpplib import Environment, ElectricalEnergyStorage, Photovoltaic

# environment
start = "2015-06-01 00:00:00"
end = "2015-06-07 23:45:00"
year = "2015"

# PV
unit = "kW"
latitude = 50.941357
longitude = 6.958307
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
timebase = 15
charge_efficiency = 0.98
discharge_efficiency = 0.98
max_power = 4  # kW
capacity = 4  # kWh
max_c = 1  # factor between 0.5 and 1.2

# test
timestamp_int = 48
timestamp_str = "2015-06-01 12:00:00"


environment = Environment(timebase=timebase, start=start, end=end, year=year)
environment.get_pv_data(file="./input/pv/dwd_pv_data_2015.csv")

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

# create storage object
storage = ElectricalEnergyStorage(
    unit=unit,
    identifier=(name + "_storage"),
    environment=environment,
    capacity=capacity,
    charge_efficiency=charge_efficiency,
    discharge_efficiency=discharge_efficiency,
    max_power=max_power,
    max_c=max_c,
)

baseload = pd.read_csv("./input/baseload/df_S_15min.csv")
baseload.drop(columns=["Time"], inplace=True)
baseload.set_index(environment.pv_data.index, inplace=True)

# combine baseload and pv timeseries to get residual load
house_loadshape = pd.DataFrame(baseload["0"].loc[start:end] / 1000)
house_loadshape["pv_gen"] = pv.timeseries.loc[start:end]
house_loadshape["residual_load"] = (
    baseload["0"].loc[start:end] / 1000 - pv.timeseries.bus_pv
)

# assign residual load to storage
storage.residual_load = house_loadshape.residual_load


def test_prepare_time_series(storage):

    storage.prepare_time_series()
    print("prepare_time_series:")
    print(storage.timeseries.head())
    storage.timeseries.plot(figsize=(16, 9))
    plt.show()


def test_value_for_timestamp(storage, timestamp):

    timestepvalue = storage.value_for_timestamp(timestamp)
    print("\nvalue_for_timestamp:\n", timestepvalue)


def test_observationsForTimestamp(storage, timestamp):

    print("observations_for_timestamp:")
    observation = storage.observations_for_timestamp(timestamp)
    print(observation, "\n")


def test_operate_storage(storage, timestamp):

    print("operate_storage:")
    state_of_charge, res_load = storage.operate_storage(
        storage.residual_load.loc[timestamp]
    )
    print("state_of_charge: ", state_of_charge)
    print("res_load: ", res_load)


test_prepare_time_series(storage)
test_value_for_timestamp(storage, timestamp_int)
test_value_for_timestamp(storage, timestamp_str)

test_observationsForTimestamp(storage, timestamp_int)
test_observationsForTimestamp(storage, timestamp_str)

test_operate_storage(storage, timestamp_str)
