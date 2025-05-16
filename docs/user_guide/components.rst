Components
==========

vpplib provides a variety of components that can be used to build a virtual power plant. Each component has its own characteristics and behavior.

Generation Components
-------------------

Photovoltaic
^^^^^^^^^^^

The Photovoltaic class represents a photovoltaic system. It uses the pvlib library to calculate the power output based on weather data.

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

Wind Power
^^^^^^^^^

The WindPower class represents a wind turbine. It calculates the power output based on wind speed data.

.. code-block:: python

   import vpplib
   
   env = vpplib.Environment(timebase=15, timezone="Europe/Berlin")
   
   wind = vpplib.WindPower(
       unit="kW",
       identifier="Wind_1",
       environment=env,
       nominal_power=100,
       hub_height=100,
       rotor_diameter=80,
       cut_in_wind_speed=3,
       cut_out_wind_speed=25,
       nominal_wind_speed=12
   )

Combined Heat and Power
^^^^^^^^^^^^^^^^^^^^^

The CombinedHeatAndPower class represents a combined heat and power plant. It can produce both electricity and heat.

.. code-block:: python

   import vpplib
   
   env = vpplib.Environment(timebase=15, timezone="Europe/Berlin")
   
   chp = vpplib.CombinedHeatAndPower(
       unit="kW",
       identifier="CHP_1",
       environment=env,
       nominal_electrical_power=50,
       nominal_thermal_power=100,
       electrical_efficiency=0.3,
       thermal_efficiency=0.6,
       overall_efficiency=0.9
   )

Storage Components
----------------

Electrical Energy Storage
^^^^^^^^^^^^^^^^^^^^^^^

The ElectricalEnergyStorage class represents an electrical energy storage system, such as a battery.

.. code-block:: python

   import vpplib
   
   env = vpplib.Environment(timebase=15, timezone="Europe/Berlin")
   
   battery = vpplib.ElectricalEnergyStorage(
       unit="kW",
       identifier="Battery_1",
       environment=env,
       capacity=100,
       max_power=50,
       efficiency=0.95,
       self_discharge=0.001
   )

Thermal Energy Storage
^^^^^^^^^^^^^^^^^^^^

The ThermalEnergyStorage class represents a thermal energy storage system, such as a hot water tank.

.. code-block:: python

   import vpplib
   
   env = vpplib.Environment(timebase=15, timezone="Europe/Berlin")
   
   tes = vpplib.ThermalEnergyStorage(
       unit="kW",
       identifier="TES_1",
       environment=env,
       capacity=100,
       max_power=50,
       efficiency=0.9,
       self_discharge=0.002
   )

Battery Electric Vehicle
^^^^^^^^^^^^^^^^^^^^^^

The BatteryElectricVehicle class represents an electric vehicle with a battery that can be charged and discharged.

.. code-block:: python

   import vpplib
   
   env = vpplib.Environment(timebase=15, timezone="Europe/Berlin")
   user = vpplib.UserProfile(timebase=15)
   
   bev = vpplib.BatteryElectricVehicle(
       unit="kW",
       identifier="BEV_1",
       environment=env,
       user_profile=user,
       capacity=60,
       max_power=11,
       efficiency=0.95
   )

Consumption Components
--------------------

Heat Pump
^^^^^^^^

The HeatPump class represents a heat pump that converts electrical energy to thermal energy.

.. code-block:: python

   import vpplib
   
   env = vpplib.Environment(timebase=15, timezone="Europe/Berlin")
   user = vpplib.UserProfile(timebase=15)
   
   hp = vpplib.HeatPump(
       unit="kW",
       identifier="HP_1",
       environment=env,
       user_profile=user,
       nominal_power=10,
       cop=3.5
   )

Heating Rod
^^^^^^^^^^

The HeatingRod class represents a simple electrical heating element.

.. code-block:: python

   import vpplib
   
   env = vpplib.Environment(timebase=15, timezone="Europe/Berlin")
   user = vpplib.UserProfile(timebase=15)
   
   hr = vpplib.HeatingRod(
       unit="kW",
       identifier="HR_1",
       environment=env,
       user_profile=user,
       nominal_power=5,
       efficiency=0.98
   )

Hydrogen Components
-----------------

Electrolyzer
^^^^^^^^^^^

The Electrolyzer class represents a device that uses electricity to split water into hydrogen and oxygen.

.. code-block:: python

   import vpplib
   
   env = vpplib.Environment(timebase=15, timezone="Europe/Berlin")
   
   electrolyzer = vpplib.Electrolyzer(
       unit="kW",
       identifier="Electrolyzer_1",
       environment=env,
       nominal_power=100,
       efficiency=0.7
   )

Fuel Cell
^^^^^^^^

The FuelCell class represents a device that converts hydrogen to electricity.

.. code-block:: python

   import vpplib
   
   env = vpplib.Environment(timebase=15, timezone="Europe/Berlin")
   
   fuel_cell = vpplib.FuelCell(
       unit="kW",
       identifier="FuelCell_1",
       environment=env,
       nominal_power=50,
       efficiency=0.6
   )

Hydrogen Storage
^^^^^^^^^^^^^^

The HydrogenStorage class represents a storage system for hydrogen.

.. code-block:: python

   import vpplib
   
   env = vpplib.Environment(timebase=15, timezone="Europe/Berlin")
   
   h2_storage = vpplib.HydrogenStorage(
       unit="kg",
       identifier="H2Storage_1",
       environment=env,
       capacity=100,
       max_power=10,
       efficiency=0.95,
       self_discharge=0.0001
   )