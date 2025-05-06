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
        'vpplib.electrical_energy_storage',
        'vpplib.pysam_battery_stateful'
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
        
        # Create PV system
        pv = Photovoltaic(unit='kW', environment=env)
        print("✓ Successfully created Photovoltaic")
        
        # Create wind power
        wind = WindPower(unit='kW', environment=env)
        print("✓ Successfully created WindPower")
        
        # Create storage
        storage = ElectricalEnergyStorage(unit='kW', environment=env)
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