# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [0.0.5] - 2025-05-20

### Added
- `DWDClient` module (`vpplib/dwd_client.py`) for direct DWD Open Data access.
- `HeatingRod` component.
- `Environment` integration with `DWDClient` for observation and MOSMIX forecast data.

### Changed
- Replaced `wetterdienst` / `marshmallow` dependency chain with lightweight `requests` + `lxml` + `pytz`.
- Updated `requirements.txt` accordingly.

## [0.0.4] - 2025-05-06

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