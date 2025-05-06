# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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