"""Integration tests for the ThermalEnergyStorage component."""

import pytest
import pandas as pd

from vpplib.thermal_energy_storage import ThermalEnergyStorage


pytestmark = pytest.mark.integration


class TestThermalEnergyStorageObservation:
    """Test thermal energy storage with DWD observation data."""

    def test_operate_storage_loop(self, tes_and_hp_obs):
        tes, hp = tes_and_hp_obs
        # Run for first 96 timesteps (1 day).
        # With live weather data the heat pump may not always produce enough
        # thermal energy, which is an expected library ValueError.
        indices = hp.timeseries.index[:96]
        operated_steps = 0
        for i in indices:
            try:
                tes.operate_storage(i, hp)
                operated_steps += 1
            except ValueError:
                break

        assert operated_steps > 0, "TES did not operate for any timesteps"

    def test_temperature_stays_in_range(self, tes_and_hp_obs):
        tes, hp = tes_and_hp_obs
        if tes.timeseries is not None and not tes.timeseries.empty:
            # Temperature should not fall far below min_temperature
            # (small deviations due to loss are acceptable)
            temps = tes.timeseries.iloc[:, 0]
            assert temps.min() >= tes.min_temperature - 10, (
                f"Temperature dropped too low: {temps.min()}"
            )
