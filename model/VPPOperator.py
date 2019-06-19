"""
Info
----
The VPPOperator class should be subclassed to implement different
operation stategies. One subclass for example could implement
machine learning to operate the virtual power plant.
Additional functions that help operating the virtual power plant,
like forecasting, should be implemented here.
        
TODO: Setup data type for target data and alter the referencing accordingly!

"""

class VPPOperator(object):

    def __init__(self, virtualPowerPlant, targetData):
        
        """
        Info
        ----
        This function takes two parameters. The first one is the virtual
        power plant, that should be operated by the operator. It must not
        be changed during simulation. The second parameter represents
        the target generation/consumption data. The operator tries
        to operate the virtual power plant in a way, that this target
        output is achieved.
        The VPPOperator class should be subclassed to implement different
        operation stategies. One subclass for example could implement
        machine learning to operate the virtual power plant.
        Additional functions that help operating the virtual power plant,
        like forecasting, should be implemented here.
        
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
        self.virtualPowerPlant = virtualPowerPlant
        self.targetData = targetData


    def operateVirtualPowerPlant(self):
        
        """
        Info
        ----
        Operation handling
    
        This function is the key function for the operation of the virtual
        power plant. It simulates every timestamp given in the target data.
        It returns how good the operation of the virtual power plant matches
        the target data (0: no match, 1: perfect match).
        
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
    
        # Create result variables
        sum = 0
        count = 0
    
    
        # Iterate through timestamps
        for i in range(0, len(self.targetData)):
    
            # Operate at timestamp
            self.operateAtTimestamp(self.targetData[i][0])

    
            # Get balance of virtual power plant
            balance = self.virtualPowerPlant.balanceAtTimestamp(self.targetData[i][0])
            
            # Get target balance
            target = self.targetData[i][1]

    
            # Calculate match
            match = 1 - (abs(target) - abs(balance)) / abs(target)

    
            # Add to sum and count
            sum += match
            count += 1
            
            
        # Calculate average of match
        average = sum / count
        
        
        # Return average
        return average


    def operateAtTimestamp(self, timestamp):
        
        """
        Info
        ----
        Raises an error since this function needs to be implemented by child classes.
        
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

        raise NotImplementedError("operateAtTimestamp needs to be implemented by child classes!")
