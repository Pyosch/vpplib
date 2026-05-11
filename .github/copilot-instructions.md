# Project Guidelines — vpplib

## Repository Overview
- **Name**: vpplib
- **Owner**: Pyosch
- **URL**: https://github.com/Pyosch/vpplib
- **Description**: A Python library for simulating distributed energy appliances in a virtual power plant.
- **License**: GNU General Public License v3 (GPLv3)

## Architecture

vpplib simulates distributed energy resources in a virtual power plant. Five core abstractions compose the system:

- **`Component`** ([vpplib/component.py](vpplib/component.py)) — Abstract base class. All energy components (PV, wind, heat pump, storage, etc.) inherit from it and override `prepare_time_series()`, `value_for_timestamp()`, and `observations_for_timestamp()`.
- **`Environment`** ([vpplib/environment.py](vpplib/environment.py)) — Weather, time settings, and regulatory context. Passed to every component's constructor. Sources data from CSV files or the DWD API.
- **`UserProfile`** ([vpplib/user_profile.py](vpplib/user_profile.py)) — Thermal demand modeling (SigLinDe method), building types, comfort factors.
- **`VirtualPowerPlant`** ([vpplib/virtual_power_plant.py](vpplib/virtual_power_plant.py)) — Aggregates components in a `dict` keyed by `identifier`. Methods: `add_component()`, `remove_component()`, `export_component_values()`.
- **`Operator`** ([vpplib/operator.py](vpplib/operator.py)) — Runs simulation strategies over a pandapower network. Key entry points: `run_base_scenario(baseload)`, `run_simbench_scenario(profiles)`.

Data flow: `Environment` + `UserProfile` → `Component.prepare_time_series()` → `VirtualPowerPlant` → `Operator` → pandapower `runpp()` → results.

## Code Style

- **No type hints** in function signatures; types documented in docstrings only.
- Classes inherit explicitly from `object` (e.g., `class Component(object):`).
- **Sign convention**: positive = consumption/load, negative = generation.
- Timestamps are accepted as `int` (iloc index), `str` (parsed via `pd.Timestamp()`), `datetime.datetime`, or `pd.Timestamp`. Use `isinstance()` dispatch.
- Use relative imports within `vpplib/` (e.g., `from .component import Component`).
- Do not add `# -*- coding: utf-8 -*-` file headers.
- Docstrings: **NumPy-style** (Parameters / Returns / Attributes sections).
- `snake_case` for variables/methods/modules, `PascalCase` for classes.
- Use `isinstance()` instead of `type()` comparisons.

## Component Pattern

When adding a new component, follow the existing pattern (see [vpplib/photovoltaic.py](vpplib/photovoltaic.py) as reference):

1. Inherit from `Component`, call `super().__init__(unit, environment)`.
2. Set `self.identifier` and component-specific attributes.
3. Override `prepare_time_series()` — compute timeseries using `self.environment` data, store in `self.timeseries` (pandas DataFrame).
4. Override `value_for_timestamp(timestamp)` — accept `int`, `str`, `datetime.datetime`, or `pd.Timestamp`; return power in kW.
5. Override `observations_for_timestamp(timestamp)` — return `dict` of status info (e.g., SoC).
6. Export the class in [vpplib/\_\_init\_\_.py](vpplib/__init__.py).

## Build and Test

```bash
# Install from source (editable)
pip install -e .

# Run the pytest test suite (requires internet for DWD API)
pytest -m integration
pytest -v

# Build docs
cd docs && make html
```

Tests live in `tests/` and use pytest with `@pytest.mark.integration` markers. They fetch live DWD weather data, instantiate components, and assert on timeseries outputs. Old ad-hoc test scripts are preserved as examples in `examples/`. Input data for examples lives in `input/` (CSV files for baseload, pv, thermal, wind).

## Key Dependencies

| Library | Purpose |
|---------|---------|
| `pvlib` | Photovoltaic modeling |
| `windpowerlib` | Wind turbine power curves |
| `pandapower` / `simbench` | Power grid modeling & simulation |
| `simses` | Battery simulation (hydrogen scenario) |
| `NREL-PySAM` | Battery stateful models |
| `pandas` / `numpy` / `polars` | Data manipulation |
| `requests` / `lxml` / `pytz` | DWD Open Data API client |
| `tqdm` | Progress bars |

## Project Environment
Use the provided virtualenv (`vppenv`) with all dependencies installed. Activate with `.\vppenv\Scripts\activate` (Windows) before running code or tests.

## Project Conventions

- VPP components dict uses identifier strings; component type is inferred by substring matching (e.g., `'_pv' in identifier`). Choose identifiers accordingly.
- `Environment` CSV paths default to `./input/` subdirectories — example scripts rely on these files existing.
- Comments and TODOs should be in English.
