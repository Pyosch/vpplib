Core Concepts
============

vpplib is built around several core concepts that work together to simulate a virtual power plant. Understanding these concepts is essential for effectively using the library.

Component
--------

The Component class is the base class for all energy components in vpplib. It provides common functionality for accounting power flows within the virtual power plant. Different types of components (generators, consumers, and storage devices) are derived from this base class.

Key features of components:

* Unique identifier
* Power unit (kW, MW, etc.)
* Connection to environment for weather and time data
* Connection to user profile for demand data
* Methods for calculating power output/input
* Methods for balancing power flows

Virtual Power Plant
-----------------

The VirtualPowerPlant class represents a combination of different components. It allows you to:

* Add and remove components
* Simulate the operation of all components together
* Balance power flows between components
* Calculate overall power output/input
* Implement operation strategies

Environment
----------

The Environment class encapsulates all environmental impacts on the system, including:

* Weather data (temperature, irradiance, wind speed, etc.)
* Time-related data (timestamps, timebase, etc.)
* Regulatory framework conditions

User Profile
-----------

The UserProfile class contains information about user behavior, such as:

* Electricity demand
* Heat demand
* Electric vehicle usage patterns
* User preferences

Operator
-------

The Operator class controls the virtual power plant according to implemented logic. Different operation strategies can be implemented by deriving from this class, such as:

* Maximizing renewable energy share
* Maximizing monetary profit
* Minimizing grid impact
* Providing grid services

Data Flow
--------

The typical data flow in vpplib is as follows:

1. Create an Environment and UserProfile
2. Create Components with references to the Environment and UserProfile
3. Add Components to a VirtualPowerPlant
4. Create an Operator with a reference to the VirtualPowerPlant
5. Simulate the operation of the VirtualPowerPlant
6. Analyze the results