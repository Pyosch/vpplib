"""Integration tests for the CombinedHeatAndPower component."""

import pytest
import pandas as pd

from vpplib.thermal_energy_storage import ThermalEnergyStorage


pytestmark = pytest.mark.integration


class TestCHPObservation:
    """Test CHP with DWD observation data."""

    def test_timeseries_not_empty(self, chp_obs):
        assert chp_obs.timeseries is not None
        assert isinstance(chp_obs.timeseries, pd.DataFrame)
        assert not chp_obs.timeseries.empty

    def test_value_for_timestamp_int(self, chp_obs):
        val = chp_obs.value_for_timestamp(0)
        assert isinstance(val, (int, float))

    def test_observations_for_timestamp_int(self, chp_obs):
        obs = chp_obs.observations_for_timestamp(0)
        assert isinstance(obs, dict)

    def test_chp_with_thermal_storage(self, chp_obs, environment_obs):
        """Test CHP coupled with a thermal energy storage."""
        tes = ThermalEnergyStorage(
            environment=environment_obs,
            unit="kWh",
            mass=500,
            hysteresis=5,
            target_temperature=60,
            min_temperature=40,
            cp=4.2,
            thermal_energy_loss_per_day=0.13,
        )
        # Run a subset of timesteps to keep test fast.
        # With live weather data the CHP may not always produce enough
        # thermal energy, which is an expected library ValueError.
        indices = chp_obs.timeseries.index[:96]
        operated_steps = 0
        for i in indices:
            try:
                tes.operate_storage(i, chp_obs)
                operated_steps += 1
            except ValueError:
                break

        assert operated_steps > 0, "TES did not operate for any timesteps"
