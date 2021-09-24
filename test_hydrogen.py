# -*- coding: utf-8 -*-
"""
Created on Mon May 10 14:07:58 2021

@author: sbirk
"""
from vpplib.hydrogen import ElectrolysisSimses
from vpplib.environment import Environment
from vpplib.user_profile import UserProfile
from vpplib.photovoltaic import Photovoltaic

import pandas as pd
import matplotlib.pyplot as plt

# environment
start = "2015-06-01 00:00:00"
end = "2015-06-07 23:45:00"
year = "2015"

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
timebase = 15
charge_efficiency = 0.98
discharge_efficiency = 0.98
electrolyzer_power = 4  # kW
fuelcell_power = None
tank_size = 700  # standard config
capacity = 4  # kWh
max_c = 1  # factor between 0.5 and 1.2

# test
timestamp_int = 48
timestamp_str = "2015-06-01 12:00:00"


environment = Environment(timebase=timebase, start=start, end=end, year=year)
environment.get_pv_data(file="./input/pv/dwd_pv_data_2015.csv")

user_profile = UserProfile(
    identifier=name, latitude=latitude, longitude=longitude
)

# create pv object and timeseries
pv = Photovoltaic(
    unit=unit,
    identifier=(name + "_pv"),
    environment=environment,
    user_profile=user_profile,
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

# %%
hydrogen = ElectrolysisSimses(electrolyzer_power=electrolyzer_power,
                              fuelcell_power=fuelcell_power,
                              tank_size=tank_size,
                              capacity=capacity,
                              soc_start=0.1,
                              soc_min=0.1,
                              soc_max=0.9,
                              identifier="SimSES",
                              result_path="./Results/SimSES/hydrogen",
                              environment=environment,
                              user_profile=user_profile,
                              unit=unit,
                              cost=None
                              )

# %%

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
hydrogen.residual_load = house_loadshape.residual_load


# %%


def test_operate_storage(hydrogen, timestamp):

    print("operate_storage:")
    state_of_charge, ac_power = hydrogen.operate_storage(
        timestamp,
        hydrogen.residual_load.loc[timestamp]
    )
    print("state_of_charge: ", state_of_charge)
    print("ac_power: ", ac_power)


def test_prepare_time_series(hydrogen):

    hydrogen.prepare_time_series()
    print("\nprepare_time_series:")
    print(hydrogen.timeseries.head())
    hydrogen.timeseries.plot(figsize=(16, 9))
    plt.show()


def test_value_for_timestamp(hydrogen, timestamp):

    timestepvalue = hydrogen.value_for_timestamp(timestamp)
    print("\nvalue_for_timestamp:\n", timestepvalue)


def test_observations_for_timestamp(hydrogen, timestamp):

    print("\nobservations_for_timestamp:")
    observation = hydrogen.observations_for_timestamp(timestamp)
    print(observation)


try:
    test_prepare_time_series(hydrogen)

    test_operate_storage(hydrogen, timestamp_str)

    test_value_for_timestamp(hydrogen, timestamp_int)
    test_value_for_timestamp(hydrogen, timestamp_str)

    test_observations_for_timestamp(hydrogen, timestamp_int)
    test_observations_for_timestamp(hydrogen, timestamp_str)

finally:
    hydrogen.simses.close()
