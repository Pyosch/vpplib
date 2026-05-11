"""Integration tests for the HeatingRod component."""

import pytest
import pandas as pd


pytestmark = pytest.mark.integration


class TestHeatingRodObservation:
    """Test heating rod with DWD observation data."""

    def test_timeseries_not_empty(self, heating_rod_obs):
        assert heating_rod_obs.timeseries is not None
        assert isinstance(heating_rod_obs.timeseries, pd.DataFrame)
        assert not heating_rod_obs.timeseries.empty

    def test_value_for_timestamp_int(self, heating_rod_obs):
        val = heating_rod_obs.valueForTimestamp(0)
        assert isinstance(val, (int, float))

    def test_value_for_timestamp_str(self, heating_rod_obs):
        ts = str(heating_rod_obs.timeseries.index[48])
        val = heating_rod_obs.valueForTimestamp(ts)
        assert isinstance(val, (int, float))

    def test_observations_for_timestamp_int(self, heating_rod_obs):
        obs = heating_rod_obs.observationsForTimestamp(0)
        assert isinstance(obs, dict)

    def test_observations_for_timestamp_str(self, heating_rod_obs):
        ts = str(heating_rod_obs.timeseries.index[48])
        obs = heating_rod_obs.observationsForTimestamp(ts)
        assert isinstance(obs, dict)

    def test_el_demand_non_negative(self, heating_rod_obs):
        """Heating rod electrical demand should be >= 0 (consumption)."""
        ts = heating_rod_obs.timeseries
        if "el_demand" in ts.columns:
            assert (ts["el_demand"] >= 0).all()
