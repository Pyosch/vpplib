# VPPlib Requirements Analysis

## Summary

The original `requirements.txt` file contains 136 packages, many of which are not necessary for the core functionality of VPPlib. This can cause installation failures for some users, particularly due to platform-specific dependencies like `pywin32`.

We've created a minimal requirements file (`requirements_minimal.txt`) with only 14 essential dependencies, which is sufficient for the core functionality of VPPlib.

## Key Findings

1. **Unnecessary Dependencies**: The original requirements file includes many packages that are not directly needed for VPPlib's core functionality:
   - Platform-specific packages (e.g., `pywin32`)
   - Visualization libraries beyond matplotlib
   - Development and testing tools
   - Web frameworks and related packages

2. **Version Conflicts**: Some specific versions in the original requirements can cause compatibility issues.

3. **Critical Dependencies**: The following packages are essential for VPPlib:
   - `windpowerlib`: For wind power modeling
   - `pvlib`: For photovoltaic modeling
   - `pandas` and `numpy`: For data handling
   - `pandapower`, `simbench`, `simses`: For power system modeling
   - `NREL-PySAM`: For renewable energy system modeling
   - `polars`: For data processing
   - `numba`: For performance optimization
   - `wetterdienst`: For weather data (version 0.89.0 specifically)
   - `marshmallow`: For object serialization (version 3.20.1 specifically)
   - `tqdm`: For progress bars
   - `matplotlib`: For basic visualization

## Performance-Related Dependencies

Several libraries in the requirements contribute to performance optimization:

1. **numba**: A Just-In-Time (JIT) compiler that accelerates Python code by compiling it to machine code at runtime.
   - Used extensively by `pandapower` for faster power flow calculations
   - Also used by `pandas` for optimized operations on DataFrames
   - Provides significant speedups for numerical computations

2. **polars**: A fast DataFrame library implemented in Rust
   - Used in `vpplib.environment` for efficient data processing
   - Provides much faster data manipulation than pandas for many operations
   - Particularly efficient for large datasets

3. **Cython**: While not directly imported in vpplib, it's used by several dependencies:
   - `numpy` uses Cython for optimized numerical operations
   - `scipy` uses Cython for efficient scientific computing functions
   - `pvlib` uses Cython for solar position algorithm calculations

These performance-related libraries are essential for the efficient operation of vpplib, especially when dealing with large datasets or complex simulations. Removing them would significantly impact performance.

## Testing Results

We created a test environment with only the minimal requirements and verified that all core components of VPPlib can be imported successfully:
- Component
- HeatPump
- Photovoltaic
- WindPower
- ElectricalEnergyStorage
- PySAMBatteryStateful

## Recommendations

1. **Use the Minimal Requirements**: For users experiencing installation issues, we recommend using the `requirements_minimal.txt` file instead of the original requirements.

2. **Version Pinning**: For critical dependencies with compatibility issues, we've pinned specific versions:
   - `wetterdienst==0.89.0`: Required for the `DwdObservationResolution` class
   - `marshmallow==3.20.1`: Required for compatibility with the `environs` package

3. **Performance Optimization**: Keep the performance-related libraries in the requirements:
   - `numba`: Essential for pandapower's power flow calculations
   - `polars`: Used for efficient data processing in the environment module
   - Dependencies that use Cython internally for optimization

4. **Future Maintenance**: Consider maintaining separate requirements files:
   - `requirements_core.txt`: Minimal dependencies for core functionality
   - `requirements_dev.txt`: Additional dependencies for development
   - `requirements_viz.txt`: Additional dependencies for visualization
   - `requirements_performance.txt`: Performance optimization libraries

This approach would make it easier for users to install only what they need and reduce installation failures.