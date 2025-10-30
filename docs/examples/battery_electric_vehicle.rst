Battery Electric Vehicle Example
================================

This example shows how to use the BatteryElectricVehicle component.

.. note::
   Example CSVs for other examples are located at:
   https://github.com/Pyosch/vpplib/tree/main/input

.. code-block:: python

   from vpplib.environment import Environment
   from vpplib.battery_electric_vehicle import BatteryElectricVehicle
   import matplotlib.pyplot as plt

   environment = Environment(start="2015-06-01 00:00:00", end="2015-06-01 23:45:00", timebase=15)

   bev = BatteryElectricVehicle(
       unit="kW",
       identifier="bev_1",
       environment=environment,
       battery_max=16,
       battery_min=0,
       battery_usage=1,
       charging_power=11,
       load_degradation_begin=0.8,
       charge_efficiency=0.98,
   )

   bev.prepare_time_series()
   bev.timeseries.plot(figsize=(16, 9))
   plt.show()
   print(bev.value_for_timestamp(48))
   print(bev.observations_for_timestamp("2015-06-01 12:00:00"))
