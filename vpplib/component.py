"""Component Module.

This module contains the basic functionalities of the Component class.
This is the parent class of all VPP component classes.

The Component class provides the foundation for all components in the virtual power plant,
including common attributes and methods that are inherited by specific component types
like photovoltaic systems, energy storage, heat pumps, etc.
"""


class Component(object):
    """Base class for all components in a virtual power plant.
    
    This class serves as the foundation for all component types in the virtual power plant.
    It provides common attributes and methods that are inherited by specific component types
    like photovoltaic systems, energy storage, heat pumps, etc.
    
    Attributes
    ----------
    unit : str, optional
        The unit of measurement for the component's output (e.g., "kW", "kWh").
    environment : Environment, optional
        The environment object providing weather data and external influences.
    identifier : str, optional
        A unique identifier for the component.
    timeseries : list or pandas.DataFrame
        Time series data for the component.
    """

    def __init__(self,
                 unit=None,
                 environment=None,
                 identifier=None):
        """Initialize a Component object.

        Parameters
        ----------
        unit : str, optional
            The unit of measurement for the component's output (e.g., "kW", "kWh").
        environment : Environment, optional
            The environment object providing weather data and external influences.
            Used to provide weather data and further external influences.
        identifier : str, optional
            A unique identifier for the component.
        """
        # Configure attributes
        self.unit = unit  # e.g. "kW"
        self.identifier = identifier
        self.environment = environment

    def value_for_timestamp(self, timestamp):
        """Get the component's value for a specific timestamp.
        
        This method returns the value of the component at the given timestamp.
        A positive result represents a load (consumption).
        A negative result represents a generation.
        
        Parameters
        ----------
        timestamp : datetime.datetime
            The timestamp for which to retrieve the value.
            
        Returns
        -------
        float
            The value of the component at the given timestamp.
            Positive for consumption, negative for generation.
            
        Notes
        -----
        This method is implemented in the base class to return the value from
        the timeseries attribute. Child classes may override this method to
        implement custom behavior.
        """
        return self.timeseries.loc[timestamp].item()

    def observations_for_timestamp(self, timestamp):
        """Get component observations for a specific timestamp.
        
        This method returns a dictionary of observations for the component at the given timestamp.
        Depending on the type of component, different status parameters can be queried.
        For example, an energy storage component might report its "State of Charge".
        
        Parameters
        ----------
        timestamp : datetime.datetime
            The timestamp for which to retrieve observations.
            
        Returns
        -------
        dict
            A dictionary with key-value pairs representing component observations.
            Returns an empty dictionary in the base class.
            
        Notes
        -----
        This method returns an empty dictionary in the base class.
        Child classes should override this method to provide component-specific observations.
        """

        return {}

    def prepare_time_series(self):
        """Prepare the time series data for the component.
        
        This method is called to prepare the time series for generations and
        consumptions that are based on non-controllable data series.
        In the base class, it sets an empty list for the timeseries attribute.
        
        Returns
        -------
        list
            An empty list in the base class.
            
        Notes
        -----
        Child classes should override this method if generation or consumption
        is based on data series or external influences.
        """

        self.timeseries = []

    def reset_time_series(self):
        """Reset the time series data for the component.
        
        This method resets the timeseries attribute to None.
        
        Returns
        -------
        None
            The reset timeseries value (None).
        """
        self.timeseries = None

        return self.timeseries
