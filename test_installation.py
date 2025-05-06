#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script to verify that vpplib can be installed and used with the minimal requirements.
"""

import sys
import importlib

def test_imports():
    """Test importing key modules from vpplib."""
    modules = [
        'vpplib',
        'vpplib.component',
        'vpplib.environment',
        'vpplib.heat_pump',
        'vpplib.photovoltaic',
        'vpplib.wind_power',
        'vpplib.electrical_energy_storage'
    ]
    
    failed_imports = []
    
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✓ Successfully imported {module}")
        except ImportError as e:
            failed_imports.append((module, str(e)))
            print(f"✗ Failed to import {module}: {e}")
    
    if failed_imports:
        print("\nThe following imports failed:")
        for module, error in failed_imports:
            print(f"  - {module}: {error}")
        return False
    else:
        print("\nAll imports successful!")
        return True

def test_component_creation():
    """Test creating basic components."""
    try:
        from vpplib.environment import Environment
        from vpplib.photovoltaic import Photovoltaic
        from vpplib.wind_power import WindPower
        from vpplib.electrical_energy_storage import ElectricalEnergyStorage
        
        # Create environment
        env = Environment(timebase=15, timezone='Europe/Berlin')
        print("✓ Successfully created Environment")
        
        # Create PV system with required parameters
        pv = Photovoltaic(
            unit='kW', 
            environment=env,
            latitude=52.5,
            longitude=13.4,
            module_lib='SandiaMod',
            inverter_lib='SandiaInverter',
            surface_tilt=30,
            surface_azimuth=180
        )
        print("✓ Successfully created Photovoltaic")
        
        # Create wind power with required parameters
        wind = WindPower(
            unit='kW', 
            environment=env,
            turbine_type='E-126/4200',
            hub_height=135,
            nominal_power=4200
        )
        print("✓ Successfully created WindPower")
        
        # Create storage with required parameters
        storage = ElectricalEnergyStorage(
            unit='kW', 
            environment=env,
            capacity=100,
            max_power=50
        )
        print("✓ Successfully created ElectricalEnergyStorage")
        
        print("\nAll components created successfully!")
        return True
    except Exception as e:
        print(f"\nError creating components: {e}")
        return False

if __name__ == "__main__":
    print("Testing vpplib installation...\n")
    
    import_success = test_imports()
    print("\n" + "-"*50 + "\n")
    component_success = test_component_creation()
    
    if import_success and component_success:
        print("\nAll tests passed! vpplib is installed correctly.")
        sys.exit(0)
    else:
        print("\nSome tests failed. Please check the error messages above.")
        sys.exit(1)