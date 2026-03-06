# Project Guidelines — vpplib

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
- Timestamps are strings (`'YYYY-MM-DD hh:mm:ss'`) or integer indices.
- Use relative imports within `vpplib/` (e.g., `from .component import Component`).
- Some file headers start with `# -*- coding: utf-8 -*-`. Remove when editing, but don't add to files that don't have it.
- Docstrings: prefer **NumPy-style** (Parameters / Returns / Attributes sections). Some older files use an informal `Info` header — match to **NumPy-style** when editing.
- `snake_case` for variables/methods/modules, `PascalCase` for classes.

## Component Pattern

When adding a new component, follow the existing pattern (see [vpplib/photovoltaic.py](vpplib/photovoltaic.py) as reference):

1. Inherit from `Component`, call `super().__init__(unit, environment)`.
2. Set `self.identifier` and component-specific attributes.
3. Override `prepare_time_series()` — compute timeseries using `self.environment` data, store in `self.timeseries` (pandas DataFrame).
4. Override `value_for_timestamp(timestamp)` — accept `int` index or `str` datetime; return power in kW.
5. Override `observations_for_timestamp(timestamp)` — return `dict` of status info (e.g., SoC).
6. Export the class in [vpplib/\_\_init\_\_.py](vpplib/__init__.py).

## Build and Test

```bash
# Install from source (editable)
pip install -e .

# Run individual test scripts (no pytest — standalone scripts)
python test_pv.py
python test_base_scenario.py        # integration test: full VPP + pandapower
python test_imports.py              # smoke test: verifies all imports

# Build docs
cd docs && make html
```

Tests are ad-hoc scripts in the repo root (`test_*.py`). They instantiate components, call `prepare_time_series()` and `value_for_timestamp()`, then print or plot results — no assertions or test framework. Input data lives in `input/` (CSV files for baseload, pv, thermal, wind).

## Key Dependencies

| Library | Purpose |
|---------|---------|
| `pvlib` | Photovoltaic modeling |
| `windpowerlib` | Wind turbine power curves |
| `pandapower` / `simbench` | Power grid modeling & simulation |
| `simses` | Battery simulation (hydrogen scenario) |
| `NREL-PySAM` | Battery stateful models |
| `pandas` / `numpy` / `polars` | Data manipulation |

## Project Conventions

- VPP components dict uses identifier strings; component type is inferred by substring matching (e.g., `'_pv' in identifier`). Choose identifiers accordingly.
- `Environment` CSV paths default to `./input/` subdirectories — tests rely on these files existing.
- German-language comments and TODOs appear occasionally; translate to English when editing nearby code.
- `type()` comparisons are used instead of `isinstance()` — follow existing style in the file you're editing.
