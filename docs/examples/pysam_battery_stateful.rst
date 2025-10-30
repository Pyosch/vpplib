PySAM Battery Stateful Example
==============================

This example uses the PySAM BatteryStateful model. It requires PySAM installed.
PV and baseload CSVs are under input/pv and input/baseload.

Input CSVs:
- https://github.com/Pyosch/vpplib/tree/main/input

.. code-block:: python

   import pandas as pd
   import matplotlib.pyplot as plt
   from vpplib.environment import Environment
   from vpplib.electrical_energy_storage import PySAMBatteryStateful
   from vpplib.photovoltaic import Photovoltaic

   start = "2015-06-01 00:00:00"
   end = "2015-06-07 23:45:00"
   environment = Environment(timebase=15, start=start, end=end, year="2015")
   environment.get_pv_data(file="./input/pv/dwd_pv_data_2015.csv")

   pv = Photovoltaic(
       unit="kW",
       latitude=50.941357,
       longitude=6.958307,
       identifier="bus_pv",
       environment=environment,
       module_lib="SandiaMod",
       module="Canadian_Solar_CS5P_220M___2009_",
       inverter_lib="cecinverter",
       inverter="Connect_Renewable_Energy__CE_4000__240V_",
       surface_tilt=20,
       surface_azimuth=200,
       modules_per_string=4,
       strings_per_inverter=2,
       temp_lib='sapm',
       temp_model='open_rack_glass_glass'
   )
   pv.prepare_time_series()

   baseload = pd.read_csv("./input/baseload/df_S_15min.csv")
   baseload.drop(columns=["Time"], inplace=True)
   baseload.set_index(environment.pv_data.index, inplace=True)

   house_loadshape = pd.DataFrame(baseload["0"].loc[start:end] / 1000)
   house_loadshape["pv_gen"] = pv.timeseries.loc[start:end]
   house_loadshape["residual_load"] = baseload["0"].loc[start:end] / 1000 - pv.timeseries.bus_pv

   storage = PySAMBatteryStateful(identifier="bus_storage", environment=environment, unit=None)
   storage.init_battery_stateful(
       nominal_energy=20, nominal_voltage=500, Vnom_default=3.600, resistance=0.0001,
       Vfull=4.100, Vexp=4.050, Vnom=3.400,
       Qfull=2.250, Qexp=0.040, Qnom=2.000,
       C_rate=0.200, Vcut=2,
       initial_SOC=50.0, maximum_SOC=95.0, minimum_SOC=5.0
   )
   storage.residual_load = house_loadshape.residual_load

   storage.prepare_time_series()
   storage.timeseries.plot(figsize=(16, 9))
   plt.show()
   print(storage.value_for_timestamp("2015-06-01 12:00:00"))
