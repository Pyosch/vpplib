# Documentation of the VPP Model structure
For the simulation of the virtual power plant a basic data structure is developed. This structure is designed in such a way that there are three superordinate elements.

## VPPComponent
The VPPComponent class represents a component within the virtual power plant. This can be, for example, a photovoltaik system or a combined heat and power plant. In addition to the generators, consumers and electrical storage devices can also be stored in this way.
The different generators, consumers and storages are derived from the VPPComponent superclass. The superclass is used to provide general functionality for the accounting of the power flows within the virtual power plant. Therefore, it does not matter whether an electricity storage device or a photovoltaik system is to be balanced afterwards. However, you can create derivations from this object so that you can still represent the special features of the individual components.
### Observation functions
The VPPComponent class requires the implementation of the following function.
Def observationsForTimestamp(self, timestamp)
This function takes a timestamp and returns a key-value-paired dictionary which contains the possible observations of that particular component. A energy storage device can, for example, return a dictionary with the key state of charge and a value for that key.
The operator of the virtual power plant can use this information to derive actions from this.
### Controlling functions
The controlling functions are individual for each derived VPPComponent. A energy storage device, for example, can provide functions to charge and discharge energy. A combined heat and power plant on the other side can offer functions for ramping up or ramping down.
### Balancing functions
The third unification based on VPPComponent are the balancing functions. By having a unified function for balancing power flows there is no need to distinguish between different components.
Def valueForTimestamp(self, timestamp)
This function returns the value at a given timestamp. The return value is a floating point. A positive float represents a consumption, a negative float a generation.
This function gets called in each iteration of the simulation to sum up the generation and consumption. This result gets compared to the target sum of the virtual power plant at this timestamp.
## Virtual power plant
The second superordinate element is the VirtualPowerPlant object. This represents a combination of different components. Individual components can be added and removed for the simulation. By this encapsulation of the individual components, different topologies of the virtual power plant can be simulated.
## VPPOperator
The last element to be named is the VPPOperator object. This object receives a reference to a VirtualPowerPlant object and controls this according to the stored logic. This element can also be used as a basis to achieve different goals. By deriving this class one VPPOperator can, for example, aim to maximize the share of renewable energies. Another VPPOperator could maximize the monetary profit.
## VPPEnvironment
The VPPEnvironment class is an encapsulation of every environmental impact on the system. In addition to basic weather data, it is also possible to store regulatory framework conditions for the operation of a virtual power plant.
The VPPEnvironment can be passed to any VPPComponent in the constructor. Depending on the component, individual data is accessed.
## VPPUserProfile
The VPPUserProfile class is similar to the VPPEnvironment class. However, this contains information on the respective usage of different types of users. For example, it can be stored how many kilometers per day an electric vehicle covers. This information is used, for example, in the model of the electric vehicle to calculate the state of charge at arrival in the evening.
Further parameters which describe the user behavior can also be stored.