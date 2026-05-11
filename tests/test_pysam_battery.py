"""Integration tests for the PySAMBatteryStateful component."""

import pytest
import pandas as pd


pytestmark = pytest.mark.integration


class TestPySAMBatteryStateful:
    """Test PySAMBatteryStateful with DWD observation data."""

    @pytest.fixture(autouse=True)
    def _check_pysam(self):
        try:
            from vpplib.electrical_energy_storage import PySAMBatteryStateful
            self.PySAMBatteryStateful = PySAMBatteryStateful
        except ImportError:
            pytest.skip("NREL-PySAM not installed")

    def test_create_and_operate(self, environment_obs, photovoltaic_obs):
        storage = self.PySAMBatteryStateful(
            identifier="test_pysam_storage",
            environment=environment_obs,
            unit=None,
        )
        storage.init_battery_stateful(
            nominal_energy=20,
            nominal_voltage=500,
            Vnom_default=3.600,
            resistance=0.0001,
            Vfull=4.100,
            Vexp=4.050,
            Vnom=3.400,
            Qfull=2.250,
            Qexp=0.040,
            Qnom=2.000,
            C_rate=0.200,
            Vcut=2,
            initial_SOC=50.0,
            maximum_SOC=95.0,
            minimum_SOC=5.0,
        )

        # Build residual load from PV, aligned to the full environment range
        full_index = pd.date_range(
            start=environment_obs.start,
            end=environment_obs.end,
            freq=environment_obs.time_freq,
        )
        pv_ts = photovoltaic_obs.timeseries
        col = pv_ts.columns[0]
        pv_series = pv_ts[col].reindex(full_index, fill_value=0)
        baseload_kw = pd.Series(0.5, index=full_index)
        storage.residual_load = baseload_kw + pv_series

        # Test single operate_storage call
        ts = str(storage.residual_load.index[48])
        soc, ac_power = storage.operate_storage(storage.residual_load.loc[ts])
        assert isinstance(soc, (int, float))
        assert isinstance(ac_power, (int, float))

        # Test prepare_time_series
        storage.prepare_time_series()
        assert storage.timeseries is not None
        assert not storage.timeseries.empty

        val = storage.value_for_timestamp(0)
        assert isinstance(val, (int, float))

        obs = storage.observations_for_timestamp(0)
        assert isinstance(obs, dict)
