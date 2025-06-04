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
- wetterdienst (version 0.109.0)
- marshmallow (version 3.20.1)

### Wetterdienst Compatibility
The repository has been updated to work with wetterdienst v0.109.0 (previously v0.89.0). The following changes were made:

1. **API Changes**:
   - `DwdMosmixType.LARGE` was replaced with `DwdForecastDate.LATEST`
   - Parameter format for `DwdMosmixRequest` changed to tuples: `('hourly', 'large', parameter_name)`
   - Parameter format for `DwdObservationRequest` changed to tuples: `('hourly', parameter_name)` or `('10_minutes', parameter_name)`

2. **Station IDs**:
   - MOSMIX data: Use station ID "10410" (ESSEN) instead of "01303"
   - Observation data: Station IDs may need larger search radius (use `distance=100` parameter)

3. **Error Handling**:
   - Added checks for empty DataFrames before accessing index
   - Added try-except blocks for "cannot concat empty list" errors
   - Added proper error messages for missing data

4. **Parameter Changes**:
   - Created a dedicated MOSMIX parameter dictionary for cleaner code organization
   - Added `use_mosmix` parameter to `get_dwd_pv_data` and `get_dwd_wind_data` methods to explicitly control data source
   - Solar radiation data is available in 10_minutes resolution

5. **PV Object Initialization**:
   - When creating Photovoltaic objects, include temperature model parameters:
     ```python
     pv = Photovoltaic(
         # other parameters...
         temp_lib="sapm",
         temp_model="open_rack_glass_glass",
     )
     ```
   - Inverter names have changed in newer pvlib versions (e.g., "ABB__MICRO_0_25_I_OUTD_US_208__208V_" instead of "ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_")

6. **Wind Data Compatibility**:
   - Wind data for windpowerlib requires a specific MultiIndex DataFrame format
   - The MultiIndex must have two levels with names 'variable' and 'height'
   - The first level contains parameter names ('wind_speed', 'temperature', 'pressure', 'roughness_length')
   - The second level contains heights (10, 2, 0, 0)
   - Example of creating a compatible wind data DataFrame:
     ```python
     # Create tuples for MultiIndex
     tuples = [
         ('wind_speed', 10),
         ('temperature', 2),
         ('pressure', 0),
         ('roughness_length', 0)
     ]
     
     # Create MultiIndex
     columns = pd.MultiIndex.from_tuples(tuples, names=['variable', 'height'])
     
     # Create the DataFrame with MultiIndex columns
     wind_data = pd.DataFrame(columns=columns, index=index)
     wind_data[('wind_speed', 10)] = weather['wind_speed']
     wind_data[('temperature', 2)] = weather['temperature']
     wind_data[('pressure', 0)] = weather['pressure']
     wind_data[('roughness_length', 0)] = weather['roughness_length']
     ```
   - Added automatic MultiIndex conversion in wind_power.py for compatibility with windpowerlib
   - When using ModelChain, ensure obstacle_height is set to 0 (not None) to prevent TypeError
   - For testing, use CSV data with proper MultiIndex format instead of MOSMIX data

7. **Timestamp Handling**:
   - Enhanced value_for_timestamp and observations_for_timestamp methods to handle datetime objects
   - Added automatic closest timestamp finding when exact timestamp is not found
   - Added proper error handling for missing data and invalid timestamp formats
   - Example usage:
     ```python
     # Using string timestamp
     value = wind.value_for_timestamp("2015-01-01 00:00:00")
     
     # Using datetime object
     import datetime
     timestamp = datetime.datetime(2015, 1, 1, 0, 0, 0)
     value = wind.value_for_timestamp(timestamp)
     
     # Using pandas Timestamp
     import pandas as pd
     timestamp = pd.Timestamp("2015-01-01 00:00:00")
     value = wind.value_for_timestamp(timestamp)
     ```

The main files affected by these changes are:
- `vpplib/environment.py`: Weather data retrieval and processing
- `vpplib/wind_power.py`: Wind power calculation and data handling
- `test_pv.py`: Test file for Photovoltaic class
- `test_wind.py`: Test file for WindPower class

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