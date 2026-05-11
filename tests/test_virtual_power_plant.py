"""Integration tests for the VirtualPowerPlant class."""

import pytest

from vpplib.virtual_power_plant import VirtualPowerPlant


pytestmark = pytest.mark.integration


class TestVirtualPowerPlant:
    """Test VPP component management."""

    def test_create_vpp(self):
        vpp = VirtualPowerPlant("test_vpp")
        assert vpp.name == "test_vpp"
        assert isinstance(vpp.components, dict)
        assert len(vpp.components) == 0

    def test_add_component(self, photovoltaic_obs):
        vpp = VirtualPowerPlant("test_vpp")
        vpp.add_component(photovoltaic_obs)
        assert photovoltaic_obs.identifier in vpp.components

    def test_remove_component(self, photovoltaic_obs):
        vpp = VirtualPowerPlant("test_vpp")
        vpp.add_component(photovoltaic_obs)
        vpp.remove_component(photovoltaic_obs.identifier)
        assert photovoltaic_obs.identifier not in vpp.components

    def test_add_multiple_components(
        self, photovoltaic_obs, wind_power_obs, bev_obs
    ):
        vpp = VirtualPowerPlant("test_vpp")
        vpp.add_component(photovoltaic_obs)
        vpp.add_component(wind_power_obs)
        vpp.add_component(bev_obs)
        assert len(vpp.components) == 3

    def test_export_component_values(
        self, photovoltaic_obs, wind_power_obs
    ):
        vpp = VirtualPowerPlant("test_vpp_export")
        vpp.add_component(photovoltaic_obs)
        vpp.add_component(wind_power_obs)
        result = vpp.export_component_values()
        assert result is not None
