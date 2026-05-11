"""Smoke test: verify all public classes can be imported."""

import pytest


@pytest.mark.integration
class TestImports:
    """Verify that all public vpplib classes can be imported."""

    def test_import_component(self):
        from vpplib.component import Component
        assert Component is not None

    def test_import_environment(self):
        from vpplib.environment import Environment
        assert Environment is not None

    def test_import_photovoltaic(self):
        from vpplib.photovoltaic import Photovoltaic
        assert Photovoltaic is not None

    def test_import_wind_power(self):
        from vpplib.wind_power import WindPower
        assert WindPower is not None

    def test_import_heat_pump(self):
        from vpplib.heat_pump import HeatPump
        assert HeatPump is not None

    def test_import_heating_rod(self):
        from vpplib.heating_rod import HeatingRod
        assert HeatingRod is not None

    def test_import_combined_heat_and_power(self):
        from vpplib.combined_heat_and_power import CombinedHeatAndPower
        assert CombinedHeatAndPower is not None

    def test_import_electrical_energy_storage(self):
        from vpplib.electrical_energy_storage import ElectricalEnergyStorage
        assert ElectricalEnergyStorage is not None

    def test_import_thermal_energy_storage(self):
        from vpplib.thermal_energy_storage import ThermalEnergyStorage
        assert ThermalEnergyStorage is not None

    def test_import_battery_electric_vehicle(self):
        from vpplib.battery_electric_vehicle import BatteryElectricVehicle
        assert BatteryElectricVehicle is not None

    def test_import_user_profile(self):
        from vpplib.user_profile import UserProfile
        assert UserProfile is not None

    def test_import_virtual_power_plant(self):
        from vpplib.virtual_power_plant import VirtualPowerPlant
        assert VirtualPowerPlant is not None

    def test_import_operator(self):
        from vpplib.operator import Operator
        assert Operator is not None

    def test_import_pysam_battery_stateful(self):
        try:
            from vpplib.electrical_energy_storage import PySAMBatteryStateful
            assert PySAMBatteryStateful is not None
        except ImportError:
            pytest.skip("NREL-PySAM not installed")

    def test_import_electrolysis_simses(self):
        try:
            from vpplib.hydrogen import ElectrolysisSimses
            assert ElectrolysisSimses is not None
        except ImportError:
            pytest.skip("simses not installed")

    def test_import_dwd_client(self):
        from vpplib.dwd_client import DWDClient
        assert DWDClient is not None

    def test_package_version(self):
        import vpplib
        assert hasattr(vpplib, "__version__")
        assert isinstance(vpplib.__version__, str)
