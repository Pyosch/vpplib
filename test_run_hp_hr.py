# -*- coding: utf-8 -*-
"""
Info
----
In this testfile a heating rod and a heat pump are being run.
Run each time you make changes on an existing function.
Adjust if a new function is added or 
parameters in an existing function are changed.

"""

from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.heat_pump import HeatPump
from vpplib.heating_rod import HeatingRod
from fct_optimize_bivalent import optimize_bivalent
import matplotlib.pyplot as plt
import pandas as pd

#Values for environment
start = '2015-01-01 00:00:00'
end = '2015-01-14 23:45:00'
year = '2015'
time_freq = "15 min"
timestamp_int1 = 48
timestamp_int2 = 500
timestamp_str1 = '2015-01-01 12:00:00'
timestamp_str2 = '2015-01-10 06:00:00'
timebase = 15

#Values for user_profile
thermal_energy_demand_yearly = 12500
building_type = 'DE_HEF33'
t_0 = 40

#Values for Heatpump
#el_power = 5 #kW electric
ramp_up_time = 1 / 15 #timesteps
ramp_down_time = 1 / 15 #timesteps
min_runtime = 1 #timesteps
min_stop_time = 2 #timesteps
heat_pump_type = "Ground" #nur "Ground" oder "Air"!


environment = Environment(timebase=timebase, start=start, end=end, year=year,
                          time_freq=time_freq)

user_profile = UserProfile(identifier=None,
                           latitude=None,
                           longitude=None,
                           thermal_energy_demand_yearly=thermal_energy_demand_yearly,
                           building_type=building_type,
                           comfort_factor=None,
                           t_0=t_0)


def test_get_thermal_energy_demand(user_profile):
    
    user_profile.get_thermal_energy_demand()
    user_profile.thermal_energy_demand.plot()
    plt.show()


test_get_thermal_energy_demand(user_profile)


hp = HeatPump(identifier='hp',
              environment=environment, user_profile=user_profile,
              #el_power=el_power,
              ramp_up_time=ramp_up_time,
              ramp_down_time=ramp_down_time, heat_pump_type = heat_pump_type,
              min_runtime=min_runtime,
              min_stop_time=min_stop_time)

hr = HeatingRod(identifier='hr1', 
                 environment=environment, user_profile = user_profile,
                 #el_power = el_power,
                 rampUpTime = ramp_up_time, 
                 rampDownTime = ramp_down_time, 
                 min_runtime = min_runtime, 
                 min_stop_time = min_stop_time)

# parameters for running hp and hr
t_biv = -5.0
mode = "parallel"

# layout hr and hp
optimize_bivalent(hp, hr, mode, t_biv, user_profile)

# show results of layout
print("thermal power hp: " + str(hp.th_power) + "[kW]")
print("electrical power hr: " + str(hr.el_power) + "[kW]")

# temperature and heat demand over time
heat_demand = user_profile.thermal_energy_demand
temperature = pd.read_csv("./input/thermal/dwd_temp_15min_2015.csv", index_col="time")
dataframe = pd.concat([heat_demand, temperature], axis = 1)

# times where hp is running
filter_hp = dataframe['temperature'] >= t_biv
bools_hp = filter_hp.values
filter_hp = pd.DataFrame(data = bools_hp, columns = ['hp_running'], index =
                         dataframe.index)

# times where hr is running (and maybe hp too, if bivalent parallel)
filter_hr = dataframe['temperature'] < t_biv
bools_hr = filter_hr.values
filter_hr = pd.DataFrame(data = bools_hr, columns = ['hr_running'], index =
                         dataframe.index)

dataframe = pd.concat([dataframe, filter_hp, filter_hr], axis = 1)
print(str(dataframe))

power_hp = []
power_hr = []

# to iterate over
th_energy_demand = dataframe['thermal_energy_demand'].values

# determine heat output of heat pump
if mode == "alternative":
    for i in range(len(dataframe)):
        if bools_hp[i] == True:
            if th_energy_demand[i] <= hp.th_power:
                power_hp.append(th_energy_demand[i])
            else:
                power_hp.append(hp.th_power)
        else:
            power_hp.append(0)
            
if mode == "parallel":
    for i in range(len(dataframe)):
        if bools_hp[i] == True:
            if th_energy_demand[i] <= hp.th_power:
                power_hp.append(th_energy_demand[i])
            else:
                power_hp.append(hp.th_power)
        else:
            if th_energy_demand[i] <= hp.th_power:
                power_hp.append(th_energy_demand[i])
            else:
                power_hp.append(hp.th_power)
        
th_output_hp = pd.DataFrame(data = power_hp, columns = ['th_output_hp'], index =
                            dataframe.index)

dataframe = pd.concat([dataframe, th_output_hp], axis = 1)
print(str(dataframe))

# determine heat output of heating rod
if mode == "parallel":
    for i in range(len(dataframe)):
        if th_energy_demand[i] > power_hp[i]:
            power = th_energy_demand[i] - power_hp[i]
            power_hr.append(power)
        else:
            power_hr.append(0)
# =============================================================================
#     for i in range(len(dataframe)):
#         if bools_hr[i] == True:
#             difference = th_energy_demand[i] - power_hp[i]
#             power_hr.append(difference)
#         else:
#             power_hr.append(0)
# =============================================================================
            
if mode == "alternative":
    for i in range(len(dataframe)):
        if bools_hr[i] == True:
            power_hr.append(th_energy_demand[i])
        else:
            power_hr.append(0)
        
th_output_hr = pd.DataFrame(data = power_hr, columns = ['th_output_hr'], index =
                            dataframe.index)

el_demand_hp = []

for i in range(len(dataframe)):
    el_demand = power_hp[i] / hp.get_current_cop(dataframe['temperature'][i])
    el_demand_hp.append(el_demand)

el_demand_hp = pd.DataFrame(data = el_demand_hp, columns = ['el_demand_hp'],
                            index = dataframe.index)

dataframe = pd.concat([dataframe, el_demand_hp], axis = 1)
    
dataframe = pd.concat([dataframe, th_output_hr], axis = 1)
print(str(dataframe))
dataframe[:(24*4*7)].plot(figsize = (16, 9))
plt.show()




