Photovoltaic Example
====================

This example shows how to use the Photovoltaic component with CSV weather data.

Note on input data:
- Example CSVs are available under https://github.com/Pyosch/vpplib/tree/main/input
  (PV weather data: input/pv/dwd_pv_data_2015.csv)

.. code-block:: python

   import matplotlib.pyplot as plt
   from vpplib.environment import Environment
   from vpplib.photovoltaic import Photovoltaic

   latitude = 50.933954264541924
   longitude = 6.988538343769104
   identifier = "Cologne"
   timestamp_int = 48
   timestamp_str = "2015-11-09 12:00:00"

   # Use CSV-based weather data to avoid DWD API issues
   environment = Environment(start="2015-01-01 00:00:00", end="2015-12-31 23:45:00")
   environment.get_pv_data(file="./input/pv/dwd_pv_data_2015.csv")

   pv = Photovoltaic(
       unit="kW",
       latitude=latitude,
       longitude=longitude,
       identifier=identifier,
       environment=environment,
       module_lib="SandiaMod",
       module="Canadian_Solar_CS5P_220M___2009_",
       inverter_lib="cecinverter",
       inverter="ABB__MICRO_0_25_I_OUTD_US_208__208V_",
       surface_tilt=20,
       surface_azimuth=200,
       modules_per_string=2,
       strings_per_inverter=2,
       temp_lib='sapm',
       temp_model='open_rack_glass_glass'
   )

   pv.prepare_time_series()
   pv.timeseries.plot(figsize=(16, 9))
   plt.show()
   print(pv.value_for_timestamp(timestamp_int))
   print(pv.observations_for_timestamp(timestamp_str))
