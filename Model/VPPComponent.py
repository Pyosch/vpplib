
class VPPComponent(object):
    
    # The parameter timebase determines the resolution of the given data. Furthermore the parameter environment (VPPEnvironment) is given to provide weather data and further external influences. To account for different people using a component, a use case (VPPUseCase) can be passed in to improve the simulation.
    def __init__(self, timebase, environment, userProfile):
    
        # Configure attributes
        self.unit = "kW"
        self.dataResolution = timebase
        self.environment = environment
        self.userProfile = userProfile
    
    
    
    
    
    # This function takes a timestamp as the parameter and returns the corresponding value for that timestamp. A positiv result represents a load. A negative result represents a generation. This abstract function needs to be implemented by child classes.
    def valueForTimestamp(self, timestamp):
    
        # Raise error since this function needs to be implemented by child classes.
        raise NotImplementedError("valueForTimestamp needs to be implemented by child classes!")
    
    
    
    
    
    # This function takes a timestamp as the parameter and returns a dictionary with key (String) value (Any) pairs. Depending on the type of component, different status parameters of the respective component can be queried. For example, a power store can report its "State of Charge".
    def observationsForTimestamp(self, timestamp):
    
        # Raise error since this function needs to be implemented by child classes.
        raise NotImplementedError("observationsForTimestamp needs to be implemented by child classes!")

    
    
    
    
    # This function is called to prepare the time series for generations and consumptions that are based on a non controllable data series. An empty array is stored for generation units that are independent of external influences.
    def prepareTimeSeries(self):
    
        # Set empty array. Override this function if generation or consumption is based on data series.
        self.timeseries = []
