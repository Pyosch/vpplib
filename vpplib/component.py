""".

Info
----
This file contains the basic functionalities of the Component class.
This is the mother class of all VPPx classes

"""


class Component(object):

    def __init__(self,
                 unit=None,
                 environment=None,
                 identifier=None):
        """

        Info.
        ----
        ...

        Parameters
        ----------
        The parameter timebase determines the resolution of the given data.
        Furthermore the parameter environment (Environment) is given,
        to provide weather data and further external influences.
        To account for different people using a component,
        a use case (VPPUseCase) can be passed in to improve the simulation.

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
        self.unit = unit  # e.g. "kW"
        self.identifier = identifier
        self.environment = environment

    def value_for_timestamp(self, timestamp):
        """
        Info.
        ----
        This function takes a timestamp as the parameter and returns the
        corresponding value for that timestamp.
        A positiv result represents a load.
        A negative result represents a generation.

        This abstract function needs to be implemented by child classes.

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
        return self.timeseries.loc[timestamp].item()

    def observations_for_timestamp(self, timestamp):
        """
        Info
        ----
        This function takes a timestamp as the parameter and returns a
        dictionary with key (String) value (Any) pairs.
        Depending on the type of component, different status parameters of the
        respective component can be queried.

        For example, a power store can report its "State of Charge".
        Returns an empty dictionary since this function needs to be
        implemented by child classes.

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

        return {}

    def prepare_time_series(self):
        """
        Info
        ----
        This function is called to prepare the time series for generations and
        consumptions that are based on a non controllable data series.
        An empty array is stored for generation units that are independent of
        external influences.

        Setting an empty array.
        Override this function if generation or consumption is based on data series.

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

        self.timeseries = []

    def reset_time_series(self):

        self.timeseries = None

        return self.timeseries
