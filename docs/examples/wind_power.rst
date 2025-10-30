Wind Power Example
==================

This example shows how to use the WindPower component with CSV wind data.

Note on input data:
- Example CSVs are available at https://github.com/Pyosch/vpplib/tree/main/input
  (Wind data: input/wind/dwd_wind_data_2015.csv)

.. code-block:: python

   import matplotlib.pyplot as plt
   from vpplib.environment import Environment
   from vpplib.wind_power import WindPower
   from windpowerlib import data as wt

   # Optional: list turbine types
   _ = wt.get_turbine_types(print_out=False)

   latitude = 51.200001
   longitude = 6.433333
   timestamp_int = 12
   timestamp_str = "2015-11-09 12:00:00"

   # Use CSV-based wind data to avoid DWD API issues
   environment = Environment(start="2015-01-01 00:00:00", end="2015-12-31 23:45:00")
   environment.get_wind_data(file="./input/wind/dwd_wind_data_2015.csv", utc=False)

   wind = WindPower(
       unit="kW",
       identifier=None,
       environment=environment,
       turbine_type="E-126/4200",
       hub_height=135,
       rotor_diameter=127,
       fetch_curve="power_curve",
       data_source="oedb",
       wind_speed_model="logarithmic",
       density_model="ideal_gas",
       temperature_model="linear_gradient",
       power_output_model="power_coefficient_curve",
       density_correction=True,
       obstacle_height=0,
       hellman_exp=None,
   )

   wind.prepare_time_series()
   wind.timeseries.plot(figsize=(16, 9))
   plt.show()
   print(wind.value_for_timestamp(timestamp_int))
   print(wind.value_for_timestamp(timestamp_str))
   print(wind.observations_for_timestamp(timestamp_int))
   print(wind.observations_for_timestamp(timestamp_str))
