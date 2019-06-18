"""
Info
----
This file contains the basic functionalities of the VirtualPowerPlant class.
This is the overall aggregator of the technologies used.

"""

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
    
        self.components = []


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
        self.components.append(component)


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
