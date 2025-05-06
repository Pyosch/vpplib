# Introduction to the VPPlib structure

## Installation

You can install vpplib using pip:

```bash
pip install vpplib
```

Or install directly from the repository:

```bash
git clone https://github.com/Pyosch/vpplib.git
cd vpplib
pip install -e .
```

### Dependencies

VPPlib requires the following main dependencies:
- windpowerlib
- pvlib
- pandas
- numpy
- pandapower
- simbench
- simses
- polars
- wetterdienst (version 0.89.0)
- marshmallow (version 3.20.1)
- NREL-PySAM

Note: Some dependencies like wetterdienst and marshmallow require specific versions for compatibility.
## Overview

For the simulation of the virtual power plant a basic data structure is developed. It consists of multiple classes to design a virtual power plant, build models of the components and operate it in a distribution grid.

The "Environment" class describes the overall environment, in which the vpp is being operated. It contains all time- and weather-related information and data. The class "UserProfile" contains information, which is specific for a certain house or housing unit, like heat demand or usage times of an electric vehicle. 

The "Component" classes can then compose the Environment and UserProfile, to access their information for simulating the single components. To aggregate the components, the "VirtualPowerPlant" class composes the components. 

To be able to mirror the behavior of the components to the distribution grid, a pandapower net object is created, containing loads, storages and generation units, which correspond to the components in the VirtualPowerPlant. The net object along with the VirtualPowerPlant are then passed on to the "Operator" class. In this class, operation strategies as well as optimizations can be implemented, considering restrictions which arise from the components as well as the grid. 

Besides the technical issues, time series from markets can also be included to analyze the financial aspects of the virtual power plant at hand.

### Component
The Component class represents a component within the virtual power plant. This can be, for example, a photovoltaik system or a combined heat and power plant. In addition to the generators, consumers and electrical storage devices can also be stored in this way.
The different generators, consumers and storages are derived from the Component superclass. The superclass is used to provide general functionality for the accounting of the power flows within the virtual power plant. Therefore, it does not matter whether an electricity storage device or a photovoltaik system is to be balanced afterwards. However, you can create derivations from this object so that you can still represent the special features of the individual components.

### Virtual power plant
The second superordinate element is the VirtualPowerPlant object. This represents a combination of different components. Individual components can be added and removed for the simulation. By this encapsulation of the individual components, different topologies of the virtual power plant can be simulated.

### Operator
The Operator object receives a reference to a VirtualPowerPlant object and controls this according to the implemented logic. This element can also be used as a basis to achieve different goals. By deriving this class one Operator can, for example, aim to maximize the share of renewable energies. Another Operator could maximize the monetary profit.

### Environment
The Environment class is an encapsulation of every environmental impact on the system. In addition to basic weather and time related data, it is also possible to store regulatory framework conditions for the operation of a virtual power plant.
The Environment can be passed to any Component in the constructor. Depending on the component, individual data is accessed.

### UserProfile
The UserProfile class is similar to the Environment class. However, this contains information on the respective usage behaviour of different types of users.