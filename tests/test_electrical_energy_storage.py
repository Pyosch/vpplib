"""Integration tests for the ElectricalEnergyStorage component."""

import pytest
import pandas as pd


pytestmark = pytest.mark.integration


class TestElectricalEnergyStorageObservation:
    """Test electrical energy storage with DWD observation data."""

    def test_timeseries_not_empty(self, storage_obs):
        assert storage_obs.timeseries is not None
        assert isinstance(storage_obs.timeseries, pd.DataFrame)
        assert not storage_obs.timeseries.empty

    def test_value_for_timestamp_int(self, storage_obs):
        val = storage_obs.value_for_timestamp(0)
        assert isinstance(val, (int, float))

    def test_value_for_timestamp_str(self, storage_obs):
        ts = str(storage_obs.timeseries.index[48])
        val = storage_obs.value_for_timestamp(ts)
        assert isinstance(val, (int, float))

    def test_observations_for_timestamp_int(self, storage_obs):
        obs = storage_obs.observations_for_timestamp(0)
        assert isinstance(obs, dict)
        assert "state_of_charge" in obs

    def test_soc_in_bounds(self, storage_obs):
        """State of charge should remain within 0 and capacity."""
        ts = storage_obs.timeseries
        if "state_of_charge" in ts.columns:
            assert (ts["state_of_charge"] >= 0).all()
            assert (ts["state_of_charge"] <= storage_obs.capacity).all()

    def test_operate_storage_returns_tuple(self, storage_obs):
        soc, res = storage_obs.operate_storage(0.5)
        assert isinstance(soc, (int, float))
        assert isinstance(res, (int, float))
