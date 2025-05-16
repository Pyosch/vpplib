Getting Started
===============

Installation
-----------

You can install vpplib using pip:

.. code-block:: bash

   pip install vpplib

Or install directly from the repository:

.. code-block:: bash

   git clone https://github.com/Pyosch/vpplib.git
   cd vpplib
   pip install -e .

Basic Usage
----------

Here's a simple example of how to use vpplib to create a virtual power plant with a photovoltaic system:

.. code-block:: python

   import vpplib
   
   # Create an environment
   env = vpplib.Environment(timebase=15, timezone="Europe/Berlin")
   
   # Create a photovoltaic system
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
   
   # Create a virtual power plant
   vpp = vpplib.VirtualPowerPlant(identifier="VPP_1")
   
   # Add the photovoltaic system to the virtual power plant
   vpp.add_component(pv)
   
   # Simulate the virtual power plant
   vpp.prepare_simulation()
   vpp.simulate(start="2020-01-01 00:00:00", end="2020-01-02 00:00:00")
   
   # Get the results
   results = vpp.get_results()
   print(results)

Next Steps
----------

Check out the following sections to learn more about vpplib:

* :doc:`concepts` - Learn about the core concepts of vpplib
* :doc:`components` - Explore the different components available in vpplib
* :doc:`virtual_power_plant` - Learn how to create and manage virtual power plants
* :doc:`environment` - Understand how to configure the environment
* :doc:`operator` - Learn about operation strategies