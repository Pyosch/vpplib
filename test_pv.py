# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 11:31:31 2019

@author: Sascha Birk
"""

import pandas as pd
#import numpy as np
#import matplotlib.pyplot as plt

# pvlib imports
#import pvlib
#
#from pvlib.pvsystem import PVSystem
#from pvlib.location import Location
#from pvlib.modelchain import ModelChain

from Model import VPPPhotovoltaik


latitude = 50.941357
longitude = 6.958307
name = 'Cologne'
#altitude = 46
weather_data = pd.read_csv("./Input_House/PV/2017_irradiation_15min.csv")
weather_data.set_index("index", inplace = True)

pv = VPPPhotovoltaik.VPPPhotovoltaik(timebase=1, identifier=name, latitude=latitude, longitude=longitude, modules_per_string=1, strings_per_inverter=1)

#asx = pv.prepareTimeSeries()
"""
TypeError: prepareTimeSeries() takes 1 positional argument but 2 were given
"""
pv.modelchain.run_model(times = weather_data.index, weather = weather_data)
print(pv.modelchain.ac)

timeseries = pd.DataFrame(pv.modelchain.ac/1000) #convert to kW
timeseries.rename(columns = {0:pv.identifier}, inplace=True)
timeseries.set_index(timeseries.index, inplace=True)
print(timeseries.head())

#pv.timeseries.plot()

#
#weather_data = pd.read_csv("./Input_House/PV/2017_irradiation_15min.csv")
#weather_data.set_index("index", inplace = True)
#temp_air =25
#wind_speed = 5
#
#print(weather_data.ghi[48])
#print(weather_data.dhi[48])
#print(weather_data.dni[48])
#print(weather_data.index[48])
## load some module and inverter specifications
#sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
#cec_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
#
#sandia_module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']
#cec_inverter = cec_inverters['ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_']
#
#location = Location(latitude=latitude, longitude=longitude)
#system = PVSystem(surface_tilt=20, surface_azimuth=200,
#                  module_parameters=sandia_module,
#                  inverter_parameters=cec_inverter)
#mc = ModelChain(system, location)
#    
#print(mc)
#count = 48
#def valueForTimestamp(mc, weather_data, count):
#    
#    weather = pd.DataFrame([[weather_data.ghi[count], weather_data.dni[count], weather_data.dhi[count], temp_air, wind_speed]],
#                               columns=['ghi', 'dni', 'dhi', 'temp_air', 'wind_speed'],
#                               index=[pd.Timestamp(weather_data.index[count], tz='Europe/Amsterdam')])
#    
#    mc.run_model(times=weather.index, weather=weather)
#    
#    return mc
#
#mc = valueForTimestamp(mc, weather_data, count)
#
#print("---")
#print("mc.ac: ", mc.ac)
#print("mc.dc: ", pd.DataFrame(mc.dc))
#print("mc.aoi: ", mc.aoi)