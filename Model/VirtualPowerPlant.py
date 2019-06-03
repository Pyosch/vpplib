
class VirtualPowerPlant(object):

    def __init__(self, name):

        # Configure attributes
        self.name = name
    
        self.components = []





    # Component handling

    # This function takes a component of type VPPComponent and appends it to the
    # components of the virtual power plant.
    def addComponent(self, component):

        # Append component
        self.components.append(component)






    # This function removes a component from the components of the virtual power
    # plant.
    def removeComponent(self, component):

        # Remove component
        self.components.remove(component)





    # Simulation handling
    
    # This function calculates the balance of all generation and consumption at a
    # given timestamp and returns the result.
    def balanceAtTimestamp(self, timestamp):

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
