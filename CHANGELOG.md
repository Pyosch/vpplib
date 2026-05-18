# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `UserProfile.get_location_calibrated_consumerfactor()` classmethod: fetches a full reference year of DWD daily observation data for a given lat/lon and computes the SigLinDe consumerfactor from station-specific temperatures, replacing the generic 2015 CSV calibration. Result is cached for 24 h by `DWDClient`.
- `consumerfactor` parameter on `UserProfile.__init__` to inject a pre-computed value and skip the automatic per-instance recalculation.

### Fixed
- `TypeError: Cannot compare tz-naive and tz-aware timestamps` when running `CombinedHeatAndPower`, `HeatPump`, or `HeatingRod` with a MOSMIX environment (`use_timezone_aware_time_index=True`): `last_ramp_up` / `last_ramp_down` sentinels now initialize from `timeseries.index[0]` (always tz-naive) instead of `thermal_energy_demand.index[0]` (tz-aware in the MOSMIX path).
- `KeyError` in `ThermalEnergyStorage.operate_storage` when indexing `thermal_energy_demand.loc[timestamp]` with tz-aware MOSMIX data: all three thermal generator components now strip timezone info from the demand index at construction time.
- `UserProfile.get_consumerfactor()` inflating demand ~100× for short MOSMIX forecast windows (10 days): `get_consumerfactor()` now skips recalculation when `self.consumerfactor` is already set.
- MOSMIX simulation loop in `demo_combined_heat_and_power.py` raising `KeyError` at the last few timesteps by iterating past the available demand horizon; loop now iterates over `thermal_energy_demand.index`.

### Changed
- `demo_combined_heat_and_power.py` MOSMIX section uses `UserProfile.get_location_calibrated_consumerfactor()` for station-specific demand scaling instead of the generic 2015-CSV-derived value.

## [0.0.6] - 2025-07-22

### Added
- `DWDClient` for fetching weather data directly from the DWD Open Data API, replacing the `wetterdienst` dependency.
- `HeatingRod` component for electrical resistance heating simulation.
- Proper pytest test suite under `tests/` with integration tests that fetch live DWD data (`@pytest.mark.integration`).
- `DWDClient` exported from `vpplib.__init__`.
- Old ad-hoc test scripts preserved as usage examples in `examples/`.

### Changed
- Switched `tqdm` imports to `tqdm.auto` for correct rendering in both terminals and notebooks; added descriptive `desc=` labels to all progress bars.
- Unified timestamp handling across all components: `value_for_timestamp()` and `observations_for_timestamp()` now accept `int`, `str`, `datetime.datetime`, and `pd.Timestamp` via `isinstance()` dispatch. Removed reliance on the private `pd._libs.tslibs.timestamps.Timestamp` type.
- Replaced all `type(x) == Y` comparisons with `isinstance()` throughout the codebase.
- Converted informal `Info / ----` docstring headers to NumPy-style across all component modules.
- Removed legacy `# -*- coding: utf-8 -*-` file headers from all modules.
- Translated remaining German comments and TODOs to English.
- Alphabetically sorted imports in `__init__.py`.

### Removed
- `wetterdienst` and `marshmallow` dependencies (replaced by `DWDClient` using `requests`, `lxml`, and `pytz`).

### Fixed
- `tqdm` progress bars no longer produce multi-line output in Jupyter notebooks.
- `operator.py` no longer casts timestamps to `str` before passing to `value_for_timestamp()`.

## [0.0.5] - 2025-05-16

### Changed
- Lost in progress ;)

## [0.0.4] - 2025-03-17

### Changed
- Optimized requirements.txt and setup.py dependencies
- Removed unnecessary dependencies that were causing installation issues
- Added specific version requirements for wetterdienst (0.89.0) and marshmallow (3.20.1) to ensure compatibility
- Added missing dependencies: pandas, numpy, and polars

### Fixed
- Installation failures on non-Windows platforms by removing platform-specific dependencies
- Compatibility issues with newer versions of wetterdienst

## [0.0.3] - Previous release

Initial public release.