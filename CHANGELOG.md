# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Updated wetterdienst compatibility from v0.89.0 to v0.109.0
- Changed DwdMosmixType.LARGE to DwdForecastDate.LATEST for MOSMIX requests
- Updated parameter format for DwdMosmixRequest to use proper (resolution, dataset, parameter) tuples
- Updated parameter format for DwdObservationRequest to use simpler format
- Added use_mosmix parameter to get_dwd_pv_data and get_dwd_wind_data methods to allow explicit MOSMIX data retrieval
- Created a dedicated MOSMIX parameter dictionary for cleaner code organization
- Modified wind_power.py to handle different MultiIndex formats for wind data

### Fixed
- Fixed MOSMIX station ID issue by using "10410" instead of "01303"
- Added empty dataframe check before accessing index to prevent IndexError
- Added error handling for empty data results from API calls
- Updated test_pv.py to properly test both MOSMIX and observation data
- Fixed inverter name in test_pv.py to match available inverters in current pvlib version
- Added proper temperature model parameters to Photovoltaic initialization
- Modified test_wind.py to use CSV data with proper MultiIndex format for windpowerlib compatibility
- Added automatic MultiIndex conversion in wind_power.py for compatibility with windpowerlib

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