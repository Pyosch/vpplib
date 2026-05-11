"""Integration tests for the HeatPump component."""

import pytest
import pandas as pd


pytestmark = pytest.mark.integration


class TestHeatPumpObservation:
    """Test heat pump with DWD observation data."""

    def test_timeseries_not_empty(self, heat_pump_obs):
        assert heat_pump_obs.timeseries is not None
        assert isinstance(heat_pump_obs.timeseries, pd.DataFrame)
        assert not heat_pump_obs.timeseries.empty

    def test_has_cop(self, heat_pump_obs):
        assert heat_pump_obs.cop is not None

    def test_value_for_timestamp_int(self, heat_pump_obs):
        val = heat_pump_obs.value_for_timestamp(0)
        assert isinstance(val, (int, float))

    def test_value_for_timestamp_str(self, heat_pump_obs):
        ts = str(heat_pump_obs.timeseries.index[48])
        val = heat_pump_obs.value_for_timestamp(ts)
        assert isinstance(val, (int, float))

    def test_observations_for_timestamp_int(self, heat_pump_obs):
        obs = heat_pump_obs.observations_for_timestamp(0)
        assert isinstance(obs, dict)

    def test_observations_for_timestamp_str(self, heat_pump_obs):
        ts = str(heat_pump_obs.timeseries.index[48])
        obs = heat_pump_obs.observations_for_timestamp(ts)
        assert isinstance(obs, dict)

    def test_el_demand_non_negative(self, heat_pump_obs):
        """Heat pump electrical demand should be >= 0 (consumption)."""
        ts = heat_pump_obs.timeseries
        if "el_demand" in ts.columns:
            assert (ts["el_demand"] >= 0).all()
