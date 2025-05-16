Operator
========

The Operator class controls the virtual power plant according to implemented logic. Different operation strategies can be implemented by deriving from this class.

Creating an Operator
------------------

To create an operator, you need to instantiate the Operator class:

.. code-block:: python

   import vpplib
   
   vpp = vpplib.VirtualPowerPlant(identifier="VPP_1")
   operator = vpplib.Operator(vpp=vpp)

Operation Strategies
------------------

The Operator class provides a default operation strategy that does nothing. To implement a custom operation strategy, you need to subclass the Operator class and override the operate method:

.. code-block:: python

   import vpplib
   
   class MaximizeSelfConsumption(vpplib.Operator):
       def operate(self, time):
           # Get the current power balance
           power_balance = self.vpp.get_power_balance(time)
           
           # Get the battery
           battery = self.vpp.get_component("Battery_1")
           
           # If there is excess power, charge the battery
           if power_balance > 0:
               battery.charge(power_balance, time)
           # If there is a power deficit, discharge the battery
           elif power_balance < 0:
               battery.discharge(abs(power_balance), time)

Example: Maximize Self-Consumption
--------------------------------

Here's a complete example of how to implement a strategy to maximize self-consumption:

.. code-block:: python

   import vpplib
   
   class MaximizeSelfConsumption(vpplib.Operator):
       def operate(self, time):
           # Get the current power balance
           power_balance = self.vpp.get_power_balance(time)
           
           # Get the battery
           battery = self.vpp.get_component("Battery_1")
           
           # If there is excess power, charge the battery
           if power_balance > 0:
               battery.charge(power_balance, time)
           # If there is a power deficit, discharge the battery
           elif power_balance < 0:
               battery.discharge(abs(power_balance), time)
   
   env = vpplib.Environment(timebase=15, timezone="Europe/Berlin")
   
   pv = vpplib.Photovoltaic(
       unit="kW",
       identifier="PV_1",
       environment=env,
       module_lib="SandiaMod",
       module="Canadian_Solar_CS5P_220M___2009_",
       inverter_lib="SandiaInverter",
       inverter="ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_",
       surface_tilt=30,
       surface_azimuth=180,
       modules_per_string=10,
       strings_per_inverter=2
   )
   
   battery = vpplib.ElectricalEnergyStorage(
       unit="kW",
       identifier="Battery_1",
       environment=env,
       capacity=100,
       max_power=50,
       efficiency=0.95,
       self_discharge=0.001
   )
   
   vpp = vpplib.VirtualPowerPlant(identifier="VPP_1")
   vpp.add_component(pv)
   vpp.add_component(battery)
   
   operator = MaximizeSelfConsumption(vpp=vpp)
   
   # Prepare the simulation
   vpp.prepare_simulation()
   
   # Run the simulation
   vpp.simulate(start="2020-01-01 00:00:00", end="2020-01-02 00:00:00")
   
   # Get the results
   results = vpp.get_results()
   print(results)

Example: Maximize Profit
----------------------

Here's an example of how to implement a strategy to maximize profit:

.. code-block:: python

   import vpplib
   
   class MaximizeProfit(vpplib.Operator):
       def __init__(self, vpp, price_data):
           super().__init__(vpp)
           self.price_data = price_data
       
       def operate(self, time):
           # Get the current power balance
           power_balance = self.vpp.get_power_balance(time)
           
           # Get the battery
           battery = self.vpp.get_component("Battery_1")
           
           # Get the current price
           current_price = self.price_data.loc[time, "price"]
           
           # If the price is high, discharge the battery
           if current_price > 0.15:  # EUR/kWh
               battery.discharge(battery.max_power, time)
           # If the price is low, charge the battery
           elif current_price < 0.05:  # EUR/kWh
               battery.charge(battery.max_power, time)
           # Otherwise, use the battery to balance the power
           else:
               # If there is excess power, charge the battery
               if power_balance > 0:
                   battery.charge(power_balance, time)
               # If there is a power deficit, discharge the battery
               elif power_balance < 0:
                   battery.discharge(abs(power_balance), time)
   
   import pandas as pd
   
   # Create price data
   price_data = pd.DataFrame({
       "datetime": pd.date_range(start="2020-01-01", end="2020-01-02", freq="15min"),
       "price": [0.1] * 97
   })
   price_data.set_index("datetime", inplace=True)
   
   env = vpplib.Environment(timebase=15, timezone="Europe/Berlin")
   
   pv = vpplib.Photovoltaic(
       unit="kW",
       identifier="PV_1",
       environment=env,
       module_lib="SandiaMod",
       module="Canadian_Solar_CS5P_220M___2009_",
       inverter_lib="SandiaInverter",
       inverter="ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_",
       surface_tilt=30,
       surface_azimuth=180,
       modules_per_string=10,
       strings_per_inverter=2
   )
   
   battery = vpplib.ElectricalEnergyStorage(
       unit="kW",
       identifier="Battery_1",
       environment=env,
       capacity=100,
       max_power=50,
       efficiency=0.95,
       self_discharge=0.001
   )
   
   vpp = vpplib.VirtualPowerPlant(identifier="VPP_1")
   vpp.add_component(pv)
   vpp.add_component(battery)
   
   operator = MaximizeProfit(vpp=vpp, price_data=price_data)
   
   # Prepare the simulation
   vpp.prepare_simulation()
   
   # Run the simulation
   vpp.simulate(start="2020-01-01 00:00:00", end="2020-01-02 00:00:00")
   
   # Get the results
   results = vpp.get_results()
   print(results)