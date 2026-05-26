"""Integration tests for the ElectricalEnergyStorage component."""

import datetime

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

    def test_observations_for_timestamp_str(self, storage_obs):
        """String timestamp path — exercised by demo_energy_storage.py but not previously tested."""
        ts = str(storage_obs.timeseries.index[48])
        obs = storage_obs.observations_for_timestamp(ts)
        assert isinstance(obs, dict)
        assert "state_of_charge" in obs

    def test_timeseries_has_no_nan(self, storage_obs):
        """prepare_time_series must produce no NaN values."""
        assert not storage_obs.timeseries.isnull().any().any()

    def test_operate_storage_negative_residual(self, storage_obs):
        """Negative residual (surplus) routes to charge() — never previously tested."""
        soc, res = storage_obs.operate_storage(-2.0)
        assert isinstance(soc, (int, float))
        assert isinstance(res, (int, float))
        assert soc >= 0

    def test_charge_power_capped_at_max_power(self):
        """charge() must cap at max_power — currently broken: negative power never triggers guard."""
        from vpplib.environment import Environment
        from vpplib.electrical_energy_storage import ElectricalEnergyStorage
        now = datetime.datetime.now()
        env = Environment(
            timebase=15,
            start=now - datetime.timedelta(hours=1),
            end=now,
            time_freq="15 min",
            surpress_output_globally=True,
        )
        storage = ElectricalEnergyStorage(
            unit="kW",
            identifier="cap_test",
            environment=env,
            capacity=10,
            charge_efficiency=1.0,
            discharge_efficiency=1.0,
            max_power=2,
            max_c=1,
        )
        storage.state_of_charge = 0
        soc, _ = storage.charge(-100.0)  # 100 kW surplus — must be capped at 2 kW
        max_chargeable_kwh = 2 * (15 / 60)  # 0.5 kWh
        assert soc <= max_chargeable_kwh, (
            f"charge() ignored max_power: SoC={soc:.3f} kWh > {max_chargeable_kwh} kWh"
        )
