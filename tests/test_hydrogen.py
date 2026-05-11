"""Integration tests for the Hydrogen (ElectrolysisSimses) component."""

import pytest
import pandas as pd


pytestmark = pytest.mark.integration


class TestElectrolysisSimses:
    """Test ElectrolysisSimses with DWD observation data."""

    @pytest.fixture(autouse=True)
    def _check_simses(self):
        try:
            from vpplib.hydrogen import ElectrolysisSimses
            self.ElectrolysisSimses = ElectrolysisSimses
        except ImportError:
            pytest.skip("simses not installed")

    def test_create_and_prepare(self, environment_obs, photovoltaic_obs):
        hydrogen = self.ElectrolysisSimses(
            electrolyzer_power=4,
            fuelcell_power=None,
            tank_size=700,
            capacity=4,
            soc_start=0.1,
            soc_min=0.1,
            soc_max=0.9,
            identifier="test_h2",
            result_path="./Results/SimSES/hydrogen",
            environment=environment_obs,
            unit="kW",
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
        hydrogen.residual_load = baseload_kw + pv_series

        try:
            hydrogen.prepare_time_series()
            assert hydrogen.timeseries is not None
            assert not hydrogen.timeseries.empty

            val = hydrogen.value_for_timestamp(0)
            assert isinstance(val, (int, float))

            obs = hydrogen.observations_for_timestamp(0)
            assert isinstance(obs, dict)
        finally:
            hydrogen.simses.close()
