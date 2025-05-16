# VPPlib Repository Information

## Repository Overview
- **Name**: vpplib
- **Owner**: Pyosch
- **URL**: https://github.com/Pyosch/vpplib
- **Description**: A Python library for simulating distributed energy appliances in a virtual power plant.
- **License**: GNU General Public License v3 (GPLv3)

## Project Structure
The repository is organized as follows:
- `vpplib/`: Main package directory containing all the core modules
- `docs/`: Documentation files
- `input/`: Input data for simulations
- `test_*.py`: Test files for various components

## Core Components
VPPlib consists of several key classes:

1. **Component**: Base class for all energy components (generators, consumers, storage)
   - `component.py`

2. **Energy Generation Components**:
   - `photovoltaic.py`: Solar PV systems
   - `wind_power.py`: Wind power systems
   - `combined_heat_and_power.py`: CHP systems
   - `heat_pump.py`: Heat pump systems
   - `heating_rod.py`: Heating rod systems
   - `hydrogen.py`: Hydrogen systems

3. **Energy Storage Components**:
   - `electrical_energy_storage.py`: Battery storage systems
   - `thermal_energy_storage.py`: Thermal storage systems
   - `battery_electric_vehicle.py`: Electric vehicle batteries

4. **System Components**:
   - `virtual_power_plant.py`: Aggregates multiple components into a VPP
   - `operator.py`: Controls the VPP according to implemented logic
   - `environment.py`: Encapsulates environmental impacts (weather, time, regulations)
   - `user_profile.py`: Contains information on user behavior patterns

## Dependencies
Main dependencies include:
- windpowerlib
- pvlib
- pandas
- numpy
- pandapower
- simbench
- simses
- polars
- NREL-PySAM
- wetterdienst (version 0.89.0)
- marshmallow (version 3.20.1)

## Installation
The package can be installed via pip:
```bash
pip install vpplib
```

Or directly from the repository:
```bash
git clone https://github.com/Pyosch/vpplib.git
cd vpplib
pip install -e .
```

## Python Compatibility
- Requires Python 3.9 or higher
- Compatible with Python 3.9, 3.10, 3.11, 3.12, and 3.13

## Development Status
- Development Status: 4 - Beta

## Contact
- Author: Pyosch
- Email: pyosch@posteo.de