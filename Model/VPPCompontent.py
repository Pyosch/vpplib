
class VPPComponent(object):
    
    # The parameter timebase determines the resolution of the given data.
    def __init__(self, timebase):
    
        # Configure attributes
        self.unit = "kW"
        self.dataResolution = timebase
    
    
    
    
    
    
    
    # This function takes a timestamp as the parameter and returns the
    # corresponding value for that timestamp. A positiv result represents
    # a load. A negative result represents a generation.
    # This abstract function needs to be implemented by child classes.
    def valueForTimestamp(self, timestamp):
    
        # Raise error since this function needs to be implemented by child classes.
        raise NotImplementedError("valueForTimestamp needs to be implemented by child classes!")
    
    
    
    
    
    # This function is called to prepare the time series for generations and consumptions
    # that are based on a non controllable data series. An empty array is stored for generation
    # units that are independent of external influences.
    def prepareTimeSeries(self):
    
        # Set empty array. Override this function if generation or consumption is based on data series.
        self.timeseries = []

    



    # This function converts the given timebase to a target timebase. This is achieved by calculating
    # the average. The return value is either None, if an error occured, or an array of averaged values.
    def averageDataToTimebase(self, targetTimebase):

        # Validate input parameters
        if targetTimebase > self.timebase:

            # Calculate compression factor
            compressionFactor = targetTimebase / self.timebase
            
            # Calculate number of iterations
            numberOfIterations = int(len(self.timeseries) / compressionFactor)
            
            
            # Create results array
            result = []
            
            # Iterate through timeseries
            for i in range(0, numberOfIterations):
                
                sum = 0
                count = 0
                
                for j in range(0, targetTimebase):
                    
                    # Add to sum
                    sum += self.timeseries[i * compressionFactor + j]
                    
                    # Increase count
                    count += 1
                    

                # Validate count
                if count > 0:

                    # Calculate average
                    average = sum / count
                    
                    # Append to result
                    result.append(average)


            return result

        else:

            # Parameter is invalid
            return None
