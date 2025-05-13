Welcome to vpplib's documentation!
===================================

**vpplib** is a Python library for simulating distributed energy appliances in a virtual power plant.

.. image:: https://readthedocs.org/projects/vpplib/badge/?version=latest
   :target: https://vpplib.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

Overview
--------

For the simulation of the virtual power plant, vpplib provides a basic data structure consisting of multiple classes to design a virtual power plant, build models of the components, and operate it in a distribution grid.

Key Features
-----------

* Simulation of various energy components (PV, wind, CHP, etc.)
* Modeling of electrical and thermal storage systems
* Integration of battery electric vehicles
* Environment and user profile modeling
* Virtual power plant aggregation
* Grid operation strategies

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

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/getting_started
   user_guide/concepts
   user_guide/components
   user_guide/virtual_power_plant
   user_guide/environment
   user_guide/operator

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/simple_vpp
   examples/advanced_vpp

.. toctree::
   :maxdepth: 2
   :caption: Architecture

   architecture/overview
   architecture/component_model
   architecture/data_flow

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/component
   api/virtual_power_plant
   api/environment
   api/user_profile
   api/operator
   api/photovoltaic
   api/wind_power
   api/combined_heat_and_power
   api/electrical_energy_storage
   api/thermal_energy_storage
   api/battery_electric_vehicle
   api/heat_pump
   api/heating_rod
   api/hydrogen

.. toctree::
   :maxdepth: 1
   :caption: Development

   development/contributing
   development/changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`