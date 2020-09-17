# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 06:54:43 2020

@author: andre
create csv containing temperatures for the solar thermal (instead of calculating
each time when running a test_solar_thermal). calculating of temperatures
according to dwd_pv_data_2015.
"""

import pandas as pd
from vpplib.user_profile import UserProfile

# create user_profile to get its index (to set index of temps_ST_df equal to)
# Values for user_profile
yearly_thermal_energy_demand = 15000  # kWh
building_type = "DE_HEF33"
t_0 = 40  # °C

user_profile = UserProfile(
    identifier=None,
    latitude=None,
    longitude=None,
    thermal_energy_demand_yearly=yearly_thermal_energy_demand,
    building_type=building_type,
    comfort_factor=None,
    t_0=t_0,
    )

user_profile.get_thermal_energy_demand()

# maximum difference between ambient temperature and heat carrier temperature
max_diff_T = 10

# for visualizing
start = "2015-01-01 00:00:00"
end = "2015-12-31 23:45:00"

pv_data_df = pd.read_csv("./input/pv/dwd_pv_data_2015.csv",
                         index_col="time"
                         )

temps_env_df = pd.read_csv("./input/thermal/dwd_temp_15min_2015.csv",
                         index_col="time"
                         )

temps_ST_df = pd.DataFrame(
        columns = ["temperatures_fluid"],
        index = user_profile.thermal_energy_demand.index
        )
        
max_irr = pv_data_df["dni"].max()

for i, data in pv_data_df.iterrows():
    # temperature of solar fluid equals environment temperature plus a part from
    # the solar radiation
    temps_ST_df["temperatures_fluid"][i] = temps_env_df["temperature"][i] + (
            pv_data_df["dni"][i] / max_irr * max_diff_T)

print(temps_ST_df)
print(temps_env_df)
print(user_profile.thermal_energy_demand)
        
# =============================================================================
# print(pv_data_df)
# print(temps_env_df)
# print(temps_ST_df)
# =============================================================================
temps_df = pd.concat([temps_env_df, temps_ST_df], axis = 1)
print(temps_df)
temps_df[start:end].plot()

temps_ST_df.to_csv("./input/pv/calculated_ST_temps_2015.csv")
