# -*- coding: utf-8 -*-
"""
Created on Mon May 10 14:07:58 2021

@author: sbirk
"""
from vpplib.hydrogen import ElectrolysisSimses
# from simses.technology.hydrogen.factory import HydrogenFactory
# from configparser import ConfigParser
# from simses.commons.data.data_handler import DataHandler
# from simses.commons.config.data.electrolyzer import ElectrolyzerDataConfig
# from simses.commons.constants import Hydrogen as HydrogenConstants
# from simses.commons.state.technology.electrolyzer import ElectrolyzerState
# from simses.technology.hydrogen.electrolyzer.stack.pem import PemElectrolyzer
# from simses.technology.hydrogen.system import Hydrogen

# # %%
# electrolyzer_data_config = ElectrolyzerDataConfig()
# electrolyzer_maximal_power = 5

# pem = PemElectrolyzer(electrolyzer_maximal_power,
#                       electrolyzer_data_config)

# # %%
# configparser = ConfigParser()
# # datahandler = DataHandler

# hydrogen = Hydrogen(data_export=DataHandler,  # "./Results/SimSES/hydrogen/",
#                     fuel_cell="NoFuelCell",  # "PemFuelCell",
#                     fuel_cell_maximal_power=50_000,  # W,
#                     electrolyzer="PemElectrolyzer",
#                     electrolyzer_maximal_power=50_000,  # W,
#                     storage="PressureTank",
#                     capacity=50_000,  # Wh ?
#                     max_pressure=20,  # bar
#                     temperature=25,  # °C
#                     system_id=0,
#                     storage_id=0,
#                     config=configparser)

# %%
from vpplib.environment import Environment
from vpplib.user_profile import UserProfile
from vpplib.electrical_energy_storage import ElectricalEnergyStorageSimses
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
)

pv.prepare_time_series()

# %%
hydrogen = ElectrolysisSimses(max_power=max_power,
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

hydrogen.prepare_time_series()


hydrogen.timeseries.plot()

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
    print("prepare_time_series:")
    print(hydrogen.timeseries.head())
    hydrogen.timeseries.plot(figsize=(16, 9))
    plt.show()


def test_value_for_timestamp(hydrogen, timestamp):

    timestepvalue = hydrogen.value_for_timestamp(timestamp)
    print("\nvalue_for_timestamp:\n", timestepvalue)


def test_observations_for_timestamp(hydrogen, timestamp):

    print("observations_for_timestamp:")
    observation = hydrogen.observations_for_timestamp(timestamp)
    print(observation, "\n")


try:
    test_operate_storage(hydrogen, timestamp_str)

    test_prepare_time_series(hydrogen)

    test_value_for_timestamp(hydrogen, timestamp_int)
    test_value_for_timestamp(hydrogen, timestamp_str)

    test_observations_for_timestamp(hydrogen, timestamp_int)
    test_observations_for_timestamp(hydrogen, timestamp_str)

finally:
    hydrogen.simses.close()
