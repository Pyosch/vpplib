Environment
===========

The Environment class encapsulates all environmental impacts on the system, including weather data and time-related data.

Creating an Environment
---------------------

To create an environment, you need to instantiate the Environment class:

.. code-block:: python

   import vpplib
   
   env = vpplib.Environment(timebase=15, timezone="Europe/Berlin")

Timebase
-------

The timebase parameter specifies the time resolution of the simulation in minutes. For example, a timebase of 15 means that the simulation will be performed in 15-minute intervals.

Timezone
-------

The timezone parameter specifies the timezone of the simulation. It should be a string that can be recognized by the pytz library.

Weather Data
----------

The Environment class can load weather data from different sources:

From CSV File
^^^^^^^^^^^

.. code-block:: python

   env.load_weather_from_csv(
       filepath="weather_data.csv",
       datetime_column="datetime",
       temperature_column="temperature",
       irradiance_column="irradiance",
       wind_speed_column="wind_speed"
   )

From Pandas DataFrame
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import pandas as pd
   
   weather_data = pd.DataFrame({
       "datetime": pd.date_range(start="2020-01-01", end="2020-01-02", freq="15min"),
       "temperature": [10.0] * 97,
       "irradiance": [800.0] * 97,
       "wind_speed": [5.0] * 97
   })
   
   env.load_weather_from_dataframe(
       dataframe=weather_data,
       datetime_column="datetime",
       temperature_column="temperature",
       irradiance_column="irradiance",
       wind_speed_column="wind_speed"
   )

From API
^^^^^^^

.. code-block:: python

   env.load_weather_from_api(
       latitude=52.52,
       longitude=13.405,
       start="2020-01-01 00:00:00",
       end="2020-01-02 00:00:00",
       api_key="your_api_key"
   )

Accessing Weather Data
-------------------

You can access the weather data using the get_weather method:

.. code-block:: python

   # Get the temperature at a specific time
   temperature = env.get_weather("temperature", "2020-01-01 12:00:00")
   
   # Get the irradiance at a specific time
   irradiance = env.get_weather("irradiance", "2020-01-01 12:00:00")
   
   # Get the wind speed at a specific time
   wind_speed = env.get_weather("wind_speed", "2020-01-01 12:00:00")

Time-Related Data
---------------

You can access time-related data using the get_time method:

.. code-block:: python

   # Get the timestamp at a specific time
   timestamp = env.get_time("timestamp", "2020-01-01 12:00:00")
   
   # Get the hour of the day at a specific time
   hour = env.get_time("hour", "2020-01-01 12:00:00")
   
   # Get the day of the week at a specific time
   day_of_week = env.get_time("day_of_week", "2020-01-01 12:00:00")
   
   # Get the month at a specific time
   month = env.get_time("month", "2020-01-01 12:00:00")
   
   # Get the year at a specific time
   year = env.get_time("year", "2020-01-01 12:00:00")