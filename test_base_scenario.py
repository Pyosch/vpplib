# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 10:38:17 2019

@author: Sascha Birk
"""

import pandas as pd
import pandapower as pp
import pandapower.networks as pn
from model.VPPPhotovoltaic import VPPPhotovoltaic
from model.VPPBEV import VPPBEV
from model.VPPHeatPump import VPPHeatPump
from model.VPPEnergyStorage import VPPEnergyStorage
from model.VPPWind import VPPWind
from model.VirtualPowerPlant import VirtualPowerPlant
from model.VPPOperator import VPPOperator

import logging
logging.getLogger().setLevel(logging.DEBUG)

latitude = 50.941357
longitude = 6.958307

start = '2017-03-01 00:00:00'
end = '2017-03-01 23:45:00'
timezone = 'Europe/Berlin'
year = '2017'
time_freq = "15 min"
timebase=15/60
index=pd.date_range(start=start, end=end, freq=time_freq)

weather_data = pd.read_csv("./Input_House/PV/2017_irradiation_15min.csv")
weather_data.set_index("index", inplace = True)

baseload = pd.read_csv("./Input_House/Base_Szenario/df_S_15min.csv")
baseload.set_index("Time", inplace=True)
baseload.index = pd.to_datetime(baseload.index)

wind_filename = "./Input_House/Wind/weather.csv"

#WindTurbine data
turbine_type = 'E-126/4200'
hub_height = 135
rotor_diameter = 127
fetch_curve = 'power_curve'
data_source = 'oedb'

#ModelChain data
wind_speed_model = 'logarithmic'
density_model = 'ideal_gas'
temperature_model = 'linear_gradient'
power_output_model = 'power_curve'
density_correction = True
obstacle_height = 0
hellman_exp = None

#storage
timebase = 15/60
chargeEfficiency = 0.98
dischargeEfficiency = 0.98
maxPower = 4 #kW
capacity = 4 #kWh
maxC = 1 #factor between 0.5 and 1.2

#%% define the amount of components in the grid
# NOT VALIDE for all component distribution methods (see line 131-143)

pv_percentage = 50
storage_percentage = 50
bev_percentage = 0
hp_percentage = 0
wind_percentage = 0

#%% create instance of VirtualPowerPlant and the designated grid
vpp = VirtualPowerPlant("Master")

net = pn.panda_four_load_branch()

#%% assign names and types to baseloads for later p and q assignment
for bus in net.bus.index:
    
    net.load.name[net.load.bus == bus] = net.bus.name[bus]+'_baseload'
    net.load.type[net.load.bus == bus] = 'baseload'

#%% assign components to random bus names

def test_get_buses_with_components(vpp):
    vpp.get_buses_with_components(net, method='random', 
                                          pv_percentage=pv_percentage,
                                          hp_percentage=hp_percentage,
                                          bev_percentage=bev_percentage,
                                          wind_percentage=wind_percentage,
                                          storage_percentage=storage_percentage)


#%% assign components to the bus names for testing purposes
    
def test_get_assigned_buses_with_components(vpp, 
                                            buses_with_pv,
                                            buses_with_hp,
                                            buses_with_bev,
                                            buses_with_storage,
                                            buses_with_wind):
    
    vpp.buses_with_pv = buses_with_pv
    
    vpp.buses_with_hp = buses_with_hp
    
    vpp.buses_with_bev = buses_with_bev
    
    vpp.buses_with_wind = buses_with_wind
    
    # storages should only be assigned to buses with pv
    vpp.buses_with_storage = buses_with_storage


    
#%% assign components to the loadbuses

def test_get_loadbuses_with_components(vpp):
    
    vpp.get_buses_with_components(net, method='random_loadbus',
                                       pv_percentage=pv_percentage,
                                       hp_percentage=hp_percentage,
                                       bev_percentage=bev_percentage,
                                       wind_percentage=wind_percentage,
                                       storage_percentage=storage_percentage)


#%% Choose assignment methode for component distribution
    
#test_get_buses_with_components(vpp)
    
test_get_assigned_buses_with_components(vpp, 
                                        buses_with_pv = ['bus3', 'bus4', 'bus5', 'bus6'],
                                        buses_with_hp = ['bus4'],
                                        buses_with_bev = ['bus5'],
                                        buses_with_storage = ['bus5'],
                                        buses_with_wind = ['bus1'])
    
#test_get_loadbuses_with_components(vpp)

#%% create components and assign components to the Virtual Powerplant

for bus in vpp.buses_with_pv:
    
    vpp.addComponent(VPPPhotovoltaic(timebase=timebase, identifier=(bus+'_PV'), 
                                     latitude=latitude, longitude=longitude, 
                                     environment = None, userProfile = None,
                                     start = start, end = end,
                                     module_lib = 'SandiaMod', module = 'Canadian_Solar_CS5P_220M___2009_', 
                                     inverter_lib = 'cecinverter', inverter = 'ABB__PVI_4_2_OUTD_S_US_Z_M_A__208_V__208V__CEC_2014_',
                                     surface_tilt = 20, surface_azimuth = 200,
                                     modules_per_string = 4, strings_per_inverter = 2))
    
    vpp.components[list(vpp.components.keys())[-1]].prepareTimeSeries(weather_data)
    
    
for bus in vpp.buses_with_storage:
    
    vpp.addComponent(VPPEnergyStorage(timebase = timebase, 
                                      identifier=(bus+'_storage'), capacity=capacity, 
                                      chargeEfficiency=chargeEfficiency, 
                                      dischargeEfficiency=dischargeEfficiency, 
                                      maxPower=maxPower, maxC=maxC, 
                                      environment = None, userProfile = None))
    
    vpp.components[list(vpp.components.keys())[-1]].timeseries = pd.DataFrame(columns=['state_of_charge','residual_load'], index=pd.date_range(start=start, end=end, freq=time_freq))
    
    
for bus in vpp.buses_with_bev:
    
    vpp.addComponent(VPPBEV(timebase=timebase, identifier=(bus+'_BEV'),
                            start = start, end = end, time_freq = time_freq, 
                            battery_max = 16, battery_min = 0, battery_usage = 1, 
                            charging_power = 11, chargeEfficiency = 0.98, 
                            environment=None, userProfile=None))
    
    vpp.components[list(vpp.components.keys())[-1]].prepareTimeSeries()
    
    
for bus in vpp.buses_with_hp:
    
    vpp.addComponent(VPPHeatPump(identifier=(bus+'_HP'), timebase=timebase, heatpump_type="Air", 
                                 heat_sys_temp=60, environment=None, userProfile=None, 
                                 heatpump_power=5, full_load_hours=2100, 
                                 building_type = 'DE_HEF33', start=start,
                                 end=end, year = year))
    
    vpp.components[list(vpp.components.keys())[-1]].prepareTimeSeries()
    
for bus in vpp.buses_with_wind:
    
    vpp.addComponent(VPPWind(timebase = 1, identifier = (bus+'_Wind'), 
                 environment = None, userProfile = None,
                 start = None, end = None, timezone = timezone,
                 weather_filename = wind_filename,
                 turbine_type = turbine_type, hub_height = hub_height,
                 rotor_diameter = rotor_diameter, fetch_curve = fetch_curve,
                 data_source = data_source,
                 wind_speed_model = wind_speed_model, density_model = density_model,
                 temperature_model = temperature_model, 
                 power_output_model = power_output_model, 
                 density_correction = density_correction,
                 obstacle_height = obstacle_height, hellman_exp = hellman_exp))
    
    vpp.components[list(vpp.components.keys())[-1]].prepareTimeSeries(wind_filename)
    #TODO: fix with weather data from 2017
    vpp.components[list(vpp.components.keys())[-1]].timeseries.index = pd.date_range(start='2017-01-01 00:00:00', end='2017-12-31 23:45:00', freq='H')
    tmp = pd.DataFrame(index = pd.date_range(start='2017-01-01 00:00:00', end='2017-12-31 23:45:00', freq='15 min'))
    tmp['Wind'] = vpp.components[list(vpp.components.keys())[-1]].timeseries
    tmp.interpolate(inplace=True)
    vpp.components[list(vpp.components.keys())[-1]].timeseries = tmp.loc[start:end] #TODO: Adjust start:end in __init__ data when using other weather data

#%% create elements in the pandapower.net

for bus in vpp.buses_with_pv:
    
    pp.create_sgen(net, bus=net.bus[net.bus.name == bus].index[0], 
                  p_mw=(vpp.components[bus+'_PV'].module.Impo*vpp.components[bus+'_PV'].module.Vmpo/1000000),
                  name=(bus+'_PV'), type = 'PV')    

for bus in vpp.buses_with_storage:
    
    pp.create_storage(net, bus=net.bus[net.bus.name == bus].index[0],
                      p_mw=0, max_e_mwh=capacity, name=(bus+'_storage'), type='LiIon')
  
for bus in vpp.buses_with_bev:
    
    pp.create_load(net, bus=net.bus[net.bus.name == bus].index[0], 
                   p_mw=(vpp.components[bus+'_BEV'].charging_power/1000), name=(bus+'_BEV'), type='BEV')
    
for bus in vpp.buses_with_hp:
    
    pp.create_load(net, bus=net.bus[net.bus.name == bus].index[0], 
                   p_mw=(vpp.components[bus+'_HP'].heatpump_power/1000), name=(bus+'_HP'), type='HP')
    
for bus in vpp.buses_with_wind:
    
    pp.create_sgen(net, bus=net.bus[net.bus.name == bus].index[0], 
                  p_mw=(vpp.components[bus+'_Wind'].wind_turbine.nominal_power/1000000),
                  name=(bus+'_Wind'), type = 'Wind')
    
#%% initialize operator

operator = VPPOperator(virtualPowerPlant=vpp, net=net, targetData=None)

#%% run base_scenario without operation strategies

net_dict = operator.run_base_scenario(baseload)    

#%% extract results from powerflow

results = operator.extract_results(net_dict)
single_result = operator.extract_single_result(net_dict, res='ext_grid', value='p_mw')

#%% plot results of powerflow and storage values

single_result.plot(figsize=(16,9), title='ext_grid from single_result function')
operator.plot_results(results)
operator.plot_storages()
