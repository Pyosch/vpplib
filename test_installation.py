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
    from vpplib.environment import Environment
    
    # Create environment
    try:
        env = Environment(timebase=15, timezone='Europe/Berlin')
        print("✓ Successfully created Environment")
    except Exception as e:
        print(f"✗ Failed to create Environment: {e}")
        return False
    
    # Test importing component classes
    try:
        from vpplib.photovoltaic import Photovoltaic
        from vpplib.wind_power import WindPower
        from vpplib.electrical_energy_storage import ElectricalEnergyStorage
        from vpplib.heat_pump import HeatPump
        
        print("✓ Successfully imported all component classes")
        return True
    except Exception as e:
        print(f"✗ Failed to import component classes: {e}")
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