"""Integration tests for the BatteryElectricVehicle component."""

import pytest
import pandas as pd


pytestmark = pytest.mark.integration


class TestBEV:
    """Test BEV component."""

    def test_timeseries_not_empty(self, bev_obs):
        assert bev_obs.timeseries is not None
        assert isinstance(bev_obs.timeseries, pd.DataFrame)
        assert not bev_obs.timeseries.empty

    def test_value_for_timestamp_int(self, bev_obs):
        val = bev_obs.value_for_timestamp(0)
        assert isinstance(val, (int, float))

    def test_value_for_timestamp_str(self, bev_obs):
        ts = str(bev_obs.timeseries.index[48])
        val = bev_obs.value_for_timestamp(ts)
        assert isinstance(val, (int, float))

    def test_observations_for_timestamp_int(self, bev_obs):
        obs = bev_obs.observations_for_timestamp(0)
        assert isinstance(obs, dict)

    def test_timeseries_has_expected_columns(self, bev_obs):
        ts = bev_obs.timeseries
        assert "car_charger" in ts.columns
        assert "at_home" in ts.columns
