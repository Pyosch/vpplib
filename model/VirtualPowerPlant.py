"""
Info
----
This file contains the basic functionalities of the VirtualPowerPlant class.
This is the overall aggregator of the technologies used.

"""

import random
import traceback

class VirtualPowerPlant(object):

    def __init__(self, name):
        
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

        # Configure attributes
        self.name = name
    
        self.components = {}
        
        self.buses_with_pv = []
        self.buses_with_hp = []
        self.buses_with_bev = []
        self.buses_with_wind = []
        self.buses_with_storage = []


    def addComponent(self, component):
        
        """
        Info
        ----
        Component handling
        
        This function takes a component of type VPPComponent and appends it to the
        components of the virtual power plant.
        
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

        # Append component
        #self.components.append(component)
        self.components[component.identifier] = component


    def removeComponent(self, component):
        
        """
        Info
        ----
        This function removes a component from the components of the virtual power
        plant.
        
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

        # Remove component
        self.components.remove(component)
        
    def get_buses_with_components(self, net, method='random', pv_percentage=0, 
                                  hp_percentage=0, bev_percentage=0,
                                  wind_percentage = 0, storage_percentage=0):
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
        
        if method == 'random':
            
            pv_amount = int(round((len(net.bus.name[net.bus.type == 'b']) * (pv_percentage/100)), 0))
            self.buses_with_pv = random.sample(list(net.bus.name[net.bus.type == 'b']), pv_amount)

            hp_amount = int(round((len(net.bus.name[net.bus.type == 'b']) * (hp_percentage/100)), 0))
            self.buses_with_hp = random.sample(list(net.bus.name[net.bus.type == 'b']), hp_amount)

            bev_amount = int(round((len(net.bus.name[net.bus.type == 'b']) * (bev_percentage/100)), 0))
            self.buses_with_bev = random.sample(list(net.bus.name[net.bus.type == 'b']), bev_amount)
            
            wind_amount = int(round((len(net.bus.name[net.bus.type == 'b']) * (wind_percentage/100)), 0))
            self.buses_with_wind = random.sample(list(net.bus.name[net.bus.type == 'b']), wind_amount)

            #Distribution of el storage is only done for houses with pv
            storage_amount = int(round((len(self.buses_with_pv) * (storage_percentage/100)), 0))
            self.buses_with_storage = random.sample(self.buses_with_pv, storage_amount)
            
            return self.buses_with_pv, self.buses_with_hp, self.buses_with_bev, self.buses_with_wind, self.buses_with_storage
        
        elif method == 'random_loadbus':
            
   
            bus_lst = []
            for bus in net.bus.index:
                if bus in list(net.load.bus):
                    bus_lst.append(net.bus.name[bus])
                    
            pv_amount = int(round((len(bus_lst) * (pv_percentage/100)), 0))
            self.buses_with_pv = random.sample(bus_lst, pv_amount)
            
            hp_amount = int(round((len(bus_lst) * (hp_percentage/100)), 0))
            self.buses_with_hp = random.sample(bus_lst, hp_amount)
            
            bev_amount = int(round((len(bus_lst) * (bev_percentage/100)), 0))
            self.buses_with_bev = random.sample(bus_lst, bev_amount)
            
            wind_amount = int(round((len(bus_lst) * (wind_percentage/100)), 0))
            self.buses_with_wind = random.sample(bus_lst, wind_amount)
            
            #Distribution of el storage is only done for houses with pv
            storage_amount = int(round((len(self.buses_with_pv) * (storage_percentage/100)), 0))
            self.buses_with_storage = random.sample(self.buses_with_pv, storage_amount)
            
            return self.buses_with_pv, self.buses_with_hp, self.buses_with_bev, self.buses_with_wind, self.buses_with_storage
        
        else:
            traceback.print_exc("method ", method, " is invalid")


    def balanceAtTimestamp(self, timestamp):
        
        """
        Info
        ----
        Simulation handling
    
        This function calculates the balance of all generation and consumption at a
        given timestamp and returns the result.
        
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

        # Create result variable
        result = 0


        # Iterate through all components
        for i in range(0, len(self.components)):

            # Get balance for component at timestamp
            balance = self.components[i].valueForTimestamp(timestamp)

            # Add balance to result
            result += balance


        # Return result
        return result
