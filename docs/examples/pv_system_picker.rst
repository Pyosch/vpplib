PV System Picker Example
========================

This example shows how to select a PV system configuration and generate a time series.

Input CSVs:
- PV weather CSV: input/pv/dwd_pv_data_2015.csv
  https://github.com/Pyosch/vpplib/tree/main/input

.. code-block:: python

   from vpplib.environment import Environment
   from vpplib.photovoltaic import Photovoltaic

   environment = Environment(
       timebase=15,
       timezone="Europe/Berlin",
       start="2015-07-01 00:00:00",
       end="2015-07-31 23:45:00",
       year="2015",
       time_freq="15 min",
   )
   environment.get_pv_data(file="./input/pv/dwd_pv_data_2015.csv")

   pv = Photovoltaic(
       module_lib="SandiaMod",
       inverter_lib="SandiaInverter",
       surface_tilt=20,
       surface_azimuth=200,
       unit="kW",
       latitude=50.941357,
       longitude=6.958307,
       identifier="PV-System",
       environment=environment,
       temp_lib='sapm',
       temp_model='open_rack_glass_glass'
   )

   modules_per_string, strings_per_inverter, module, inverter = pv.pick_pvsystem(
       min_module_power=220,
       max_module_power=240,
       pv_power=8000,
       inverter_power_range=100
   )
   pv.prepare_time_series()
   print("PV module:", pv.module)
   print("PV inverter:", pv.inverter)
   print("PV peak power:", pv.peak_power)
   print("Area of PV modules:", pv.modules_area)
