"""Integration tests for the Operator class."""

import pytest
import pandas as pd

try:
    import pandapower as pp
    import pandapower.networks as pn
    HAS_PANDAPOWER = True
except ImportError:
    HAS_PANDAPOWER = False

from vpplib.operator import Operator
from vpplib.virtual_power_plant import VirtualPowerPlant
from vpplib.photovoltaic import Photovoltaic
from vpplib.electrical_energy_storage import ElectricalEnergyStorage
from vpplib.battery_electric_vehicle import BatteryElectricVehicle


pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def simple_vpp_and_net(environment_obs, photovoltaic_obs, bev_obs, storage_obs):
    """Create a simple VPP with a pandapower network for operator tests."""
    if not HAS_PANDAPOWER:
        pytest.skip("pandapower not installed")

    vpp = VirtualPowerPlant("operator_test_vpp")

    # Add components and assign bus names
    pv = photovoltaic_obs
    pv.bus = "bus3"
    vpp.add_component(pv)

    bev = bev_obs
    bev.bus = "bus5"
    vpp.add_component(bev)

    storage = storage_obs
    storage.bus = "bus5"
    vpp.add_component(storage)

    # Create pandapower network
    net = pn.panda_four_load_branch()

    # Assign names and types to existing loads
    for bus in net.bus.index:
        net.load.loc[net.load.bus == bus, "name"] = (
            net.bus.loc[bus, "name"] + "_baseload"
        )
        net.load.loc[net.load.bus == bus, "type"] = "baseload"

    # Add PV as static generator
    pp.create_sgen(
        net,
        bus=net.bus[net.bus.name == "bus3"].index[0],
        p_mw=0.001,
        name="test_pv",
        type="PV",
    )

    # Add BEV as load
    pp.create_load(
        net,
        bus=net.bus[net.bus.name == "bus5"].index[0],
        p_mw=0.011,
        name="test_bev",
        type="BEV",
    )

    # Add storage
    pp.create_storage(
        net,
        bus=net.bus[net.bus.name == "bus5"].index[0],
        p_mw=0,
        max_e_mwh=0.004,
        name="test_storage",
        type="LiIon",
    )

    return vpp, net


class TestOperator:
    """Test Operator instantiation and basic methods."""

    def test_create_operator(self, simple_vpp_and_net):
        vpp, net = simple_vpp_and_net
        operator = Operator(virtual_power_plant=vpp, net=net, target_data=None)
        assert operator is not None
        assert operator.virtual_power_plant is vpp
        assert operator.net is net
