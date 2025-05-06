"""
Test script to verify that the core components of vpplib can be imported.
"""

try:
    print("Importing Component...")
    from vpplib.component import Component
    print("Success!")
except Exception as e:
    print(f"Failed to import Component: {e}")

try:
    print("\nImporting HeatPump...")
    from vpplib.heat_pump import HeatPump
    print("Success!")
except Exception as e:
    print(f"Failed to import HeatPump: {e}")

try:
    print("\nImporting Photovoltaic...")
    from vpplib.photovoltaic import Photovoltaic
    print("Success!")
except Exception as e:
    print(f"Failed to import Photovoltaic: {e}")

try:
    print("\nImporting WindPower...")
    from vpplib.wind_power import WindPower
    print("Success!")
except Exception as e:
    print(f"Failed to import WindPower: {e}")

try:
    print("\nImporting ElectricalEnergyStorage...")
    from vpplib.electrical_energy_storage import ElectricalEnergyStorage
    print("Success!")
except Exception as e:
    print(f"Failed to import ElectricalEnergyStorage: {e}")

try:
    print("\nImporting PySAMBatteryStateful...")
    from vpplib.electrical_energy_storage import PySAMBatteryStateful
    print("Success!")
except Exception as e:
    print(f"Failed to import PySAMBatteryStateful: {e}")