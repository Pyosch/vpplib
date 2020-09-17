# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 17:40:34 2020

@author: andre
test creating different user_profiles
"""
from vpplib.user_profile import UserProfile
import matplotlib.pyplot as plt
import pandas as pd

#Values for user_profile
thermal_energy_demand_yearly = 15000
building_type_1 = 'DE_HEF33'
building_type_2 = 'DE_HEF34'
building_type_3 = 'DE_HMF34'
building_type_4 = 'DE_HEF33'
building_type_5 = 'DE_GKO34'


t_0 = 40

def test_get_thermal_energy_demand(user_profile):
    user_profile.get_thermal_energy_demand()
    user_profile.thermal_energy_demand.plot()
    plt.show()


user_profile_1 = UserProfile(identifier=None,
                           latitude=None,
                           longitude=None,
                           thermal_energy_demand_yearly=thermal_energy_demand_yearly,
                           building_type=building_type_1,
                           comfort_factor=None,
                           t_0=t_0)

user_profile_2 = UserProfile(identifier=None,
                           latitude=None,
                           longitude=None,
                           thermal_energy_demand_yearly=thermal_energy_demand_yearly,
                           building_type=building_type_2,
                           comfort_factor=None,
                           t_0=t_0)

user_profile_3 = UserProfile(identifier=None,
                           latitude=None,
                           longitude=None,
                           thermal_energy_demand_yearly=thermal_energy_demand_yearly,
                           building_type=building_type_3,
                           comfort_factor=None,
                           t_0=t_0)

user_profile_4 = UserProfile(identifier=None,
                           latitude=None,
                           longitude=None,
                           thermal_energy_demand_yearly=thermal_energy_demand_yearly,
                           building_type=building_type_4,
                           comfort_factor=None,
                           t_0=t_0)

user_profile_5 = UserProfile(identifier=None,
                           latitude=None,
                           longitude=None,
                           thermal_energy_demand_yearly=thermal_energy_demand_yearly,
                           building_type=building_type_5,
                           comfort_factor=None,
                           t_0=t_0)


test_get_thermal_energy_demand(user_profile_1)
test_get_thermal_energy_demand(user_profile_2)
test_get_thermal_energy_demand(user_profile_3)
test_get_thermal_energy_demand(user_profile_4)
test_get_thermal_energy_demand(user_profile_5)

test_df_div = user_profile_1.thermal_energy_demand / user_profile_2.thermal_energy_demand
test_df_div.plot()
plt.show()

test_df_sub = user_profile_1.thermal_energy_demand - user_profile_2.thermal_energy_demand
test_df_sub.plot()
plt.show()
