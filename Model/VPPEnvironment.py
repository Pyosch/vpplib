"""
Info
----
This file contains the basic functionalities of the VPPEnvironment class.
The object "VPPEnvironment" defines external influences on the system to be simulated. 
In addition to weather and location, this also includes regulatory influences.

TODO: Add regulatory influences e. g. photovoltaik maximum power at the grid connection point

"""

class VPPEnvironment(object):

    def __init__(self, weatherData, longitude, latitude):
        
        """
        Info
        ----
        ...
        
        Parameters
        ----------
        
        ...
        	
        Attributes
        ----------
        
        ...
        
        Notes
        -----
        
        ...
        
        References
        ----------
        
        ...
        
        Returns
        -------
        
        ...
        
        """

        # Configure attribues
        self.weatherData = weatherData
        self.longitude = longitude
        self.latitude
