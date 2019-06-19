"""
Info
----
The class "VPPUserProfile" reflects different patterns of use and behaviour. 
This makes it possible, for example, to simulate different usage profiles of 
electric vehicles.

TODO: Collect information about parameters that must be represented in a use case.
"""

class VPPUserProfile(object):

    def __init__(self):
        """
        Info
        ----
        This attributes can be used to derive profiles for different components. 
        The BEV for example will probably care more about the daily vehicle usage, than the comfort factor. 
        The heat pump will probably not care about the daily vehicle usage at all (and so on).
        
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

        # Examples
        self.dailyVehicleUsage = 120    # km
        self.comfortFactor = 1.3        # For people that likes to have their homes quite warm 
