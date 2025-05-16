Architecture Overview
===================

vpplib is designed with a modular architecture that allows for flexible composition of virtual power plants. This document provides an overview of the architecture and the relationships between the different components.

Core Components
-------------

.. code-block:: text

   +----------------+     +----------------+     +----------------+
   |                |     |                |     |                |
   |  Environment   |     |  UserProfile   |     |    Operator    |
   |                |     |                |     |                |
   +-------+--------+     +-------+--------+     +-------+--------+
           |                      |                      |
           |                      |                      |
           v                      v                      |
   +-------+------------------------+                    |
   |                                |                    |
   |           Component            |                    |
   |                                |                    |
   +-------+------------------------+                    |
           |                                             |
           |                                             |
           v                                             |
   +-------+------------------------+                    |
   |                                |<-------------------+
   |      VirtualPowerPlant         |
   |                                |
   +--------------------------------+

The architecture consists of the following core components:

Environment
^^^^^^^^^^

The Environment class encapsulates all environmental impacts on the system, including:

* Weather data (temperature, irradiance, wind speed, etc.)
* Time-related data (timestamps, timebase, etc.)
* Regulatory framework conditions

UserProfile
^^^^^^^^^^

The UserProfile class contains information about user behavior, such as:

* Electricity demand
* Heat demand
* Electric vehicle usage patterns
* User preferences

Component
^^^^^^^^

The Component class is the base class for all energy components in vpplib. It provides common functionality for accounting power flows within the virtual power plant. Different types of components (generators, consumers, and storage devices) are derived from this base class.

VirtualPowerPlant
^^^^^^^^^^^^^^^

The VirtualPowerPlant class represents a combination of different components. It allows you to:

* Add and remove components
* Simulate the operation of all components together
* Balance power flows between components
* Calculate overall power output/input
* Implement operation strategies

Operator
^^^^^^^

The Operator class controls the virtual power plant according to implemented logic. Different operation strategies can be implemented by deriving from this class.

Component Hierarchy
-----------------

.. code-block:: text

                           +----------------+
                           |                |
                           |   Component    |
                           |                |
                           +-------+--------+
                                   |
                 +----------------+|+----------------+
                 |                 |                 |
    +------------v------+ +--------v-------+ +------v-----------+
    |                   | |                | |                  |
    |     Generator     | |    Consumer    | |     Storage      |
    |                   | |                | |                  |
    +-----+-----+-------+ +--------+-------+ +------+-----------+
          |     |                  |                |
          |     |                  |                |
    +-----v-+  +v------+    +-----v------+  +------v-----------+
    |       |  |       |    |            |  |                  |
    |  PV   |  | Wind  |    | Heat Pump  |  | ElectricalStorage|
    |       |  |       |    |            |  |                  |
    +-------+  +-------+    +------------+  +------------------+

The Component class is the base class for all energy components in vpplib. It is subclassed by three main categories:

Generator
^^^^^^^^

Generator components produce energy. Examples include:

* Photovoltaic
* WindPower
* CombinedHeatAndPower

Consumer
^^^^^^^

Consumer components consume energy. Examples include:

* HeatPump
* HeatingRod
* BatteryElectricVehicle (in charging mode)

Storage
^^^^^^

Storage components can both consume and produce energy. Examples include:

* ElectricalEnergyStorage
* ThermalEnergyStorage
* HydrogenStorage
* BatteryElectricVehicle (in vehicle-to-grid mode)

Data Flow
--------

.. code-block:: text

   +----------------+     +----------------+
   |                |     |                |
   |  Environment   |     |  UserProfile   |
   |                |     |                |
   +-------+--------+     +-------+--------+
           |                      |
           |                      |
           v                      v
   +-------+------------------------+
   |                                |
   |           Component            |
   |                                |
   +-------+------------------------+
           |
           |
           v
   +-------+------------------------+     +----------------+
   |                                |     |                |
   |      VirtualPowerPlant         |<--->|    Operator    |
   |                                |     |                |
   +-------+------------------------+     +----------------+
           |
           |
           v
   +-------+------------------------+
   |                                |
   |           Results              |
   |                                |
   +--------------------------------+

The typical data flow in vpplib is as follows:

1. The Environment provides weather and time data to Components
2. The UserProfile provides demand data to Components
3. Components calculate their power output/input
4. The VirtualPowerPlant aggregates the power flows of all Components
5. The Operator controls the VirtualPowerPlant according to implemented logic
6. The VirtualPowerPlant produces Results that can be analyzed

Simulation Process
----------------

.. code-block:: text

   +--------------------------------+
   |                                |
   |  Create Environment and User   |
   |                                |
   +---------------+----------------+
                   |
                   v
   +---------------+----------------+
   |                                |
   |      Create Components         |
   |                                |
   +---------------+----------------+
                   |
                   v
   +---------------+----------------+
   |                                |
   |  Create Virtual Power Plant    |
   |                                |
   +---------------+----------------+
                   |
                   v
   +---------------+----------------+
   |                                |
   |       Create Operator          |
   |                                |
   +---------------+----------------+
                   |
                   v
   +---------------+----------------+
   |                                |
   |    Prepare Simulation          |
   |                                |
   +---------------+----------------+
                   |
                   v
   +---------------+----------------+
   |                                |
   |        Run Simulation          |
   |                                |
   +---------------+----------------+
                   |
                   v
   +---------------+----------------+
   |                                |
   |       Analyze Results          |
   |                                |
   +--------------------------------+

The simulation process in vpplib consists of the following steps:

1. Create an Environment and UserProfile
2. Create Components with references to the Environment and UserProfile
3. Create a VirtualPowerPlant and add Components to it
4. Create an Operator with a reference to the VirtualPowerPlant
5. Prepare the simulation
6. Run the simulation
7. Analyze the results