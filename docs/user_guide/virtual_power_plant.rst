Virtual Power Plant
=================

The VirtualPowerPlant class is the central element of vpplib. It represents a combination of different components and allows you to simulate their operation together.

Creating a Virtual Power Plant
----------------------------

To create a virtual power plant, you need to instantiate the VirtualPowerPlant class:

.. code-block:: python

   import vpplib
   
   vpp = vpplib.VirtualPowerPlant(identifier="VPP_1")

Adding Components
---------------

You can add components to the virtual power plant using the add_component method:

.. code-block:: python

   import vpplib
   
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

Removing Components
-----------------

You can remove components from the virtual power plant using the remove_component method:

.. code-block:: python

   vpp.remove_component(pv)

Simulation
---------

To simulate the operation of the virtual power plant, you need to:

1. Prepare the simulation
2. Run the simulation
3. Get the results

.. code-block:: python

   # Prepare the simulation
   vpp.prepare_simulation()
   
   # Run the simulation
   vpp.simulate(start="2020-01-01 00:00:00", end="2020-01-02 00:00:00")
   
   # Get the results
   results = vpp.get_results()
   print(results)

Operation Strategies
------------------

You can implement different operation strategies by creating an Operator class and connecting it to the virtual power plant:

.. code-block:: python

   import vpplib
   
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
   
   operator = vpplib.Operator(vpp=vpp)
   
   # Prepare the simulation
   vpp.prepare_simulation()
   
   # Run the simulation
   vpp.simulate(start="2020-01-01 00:00:00", end="2020-01-02 00:00:00")
   
   # Get the results
   results = vpp.get_results()
   print(results)

Custom Operation Strategies
-------------------------

You can create custom operation strategies by subclassing the Operator class:

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