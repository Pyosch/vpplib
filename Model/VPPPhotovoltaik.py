
from .VPPComponent import VPPComponent

import pandas as pd

# pvlib imports
import pvlib

from pvlib.pvsystem import PVSystem
from pvlib.location import Location
from pvlib.modelchain import ModelChain

class VPPPhotovoltaik(VPPComponent):

    # The constructor takes an identifier (String) for referencing the current
    # photovoltaik power plant. The parameter peak power (Float) determines the maximum
    # power that the photovoltaik power plant can generate.
    def __init__(self, timebase, identifier, latitude, longitude, environment = None, userProfile = None,
                 module_lib = 'SandiaMod', module = 'Canadian_Solar_CS5P_220M___2009_', 
                 inverter_lib = 'cecinverter', inverter = 'ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_',
                 surface_tilt = 20, surface_azimuth = 200,
                 modules_per_string = 1, strings_per_inverter = 1):

        # Call to super class
        super(VPPPhotovoltaik, self).__init__(timebase, environment, userProfile)
    
    
        # Configure attributes
        self.identifier = identifier
        #self.peakPower = peakPower #results from module
    
        self.limit = 1.0
        
        # load some module and inverter specifications
        sandia_modules = pvlib.pvsystem.retrieve_sam(module_lib)
        cec_inverters = pvlib.pvsystem.retrieve_sam(inverter_lib)
        
        self.module = sandia_modules[module]
        self.inverter = cec_inverters[inverter]

        self.location = Location(latitude=latitude, longitude=longitude)
        
        self.system = PVSystem(surface_tilt=surface_tilt, surface_azimuth=surface_azimuth,
                          module_parameters=self.module,
                          inverter_parameters=self.inverter,
                          modules_per_string=modules_per_string,
                          strings_per_inverter=strings_per_inverter)
        
        self.modelchain = ModelChain(self.system, self.location, name=identifier)
    
    
    
    
    
    def prepareTimeSeries(self, weather_data):
    
        # -> Functions stub <-
        self.modelchain.run_model(times = weather_data.index, weather = weather_data)
        
        timeseries = pd.DataFrame(self.modelchain.ac/1000) #convert to kW
        timeseries.rename(columns = {0:self.identifier}, inplace=True)
        timeseries.set_index(timeseries.index, inplace=True)
        
        self.timeseries = timeseries
        
        return timeseries





    # ===================================================================================
    # Controlling functions
    # ===================================================================================

    # This function limits the power of the photovoltaik to the given percentage.
    # It cuts the current power production down to the peak power multiplied by
    # the limit (Float [0;1]).
    def limitPowerTo(self, limit):

        # Validate input parameter
        if limit >= 0 and limit <= 1:

            # Parameter is valid
            self.limit = limit

        else:
        
            # Paramter is invalid
            return
        
    def print_value(self, time):
        
        print(time+200)

    # ===================================================================================
    # Balancing Functions
    # ===================================================================================

    # Override balancing function from super class.
    def valueForTimestamp(self, timestamp):
        
        return self.timeseries[self.identifier][self.timeseries.index[timestamp]] * self.limit
