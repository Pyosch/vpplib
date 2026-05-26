"""Integration tests for the WindPower component."""

import pytest
import pandas as pd

from vpplib.wind_power import WindPower


pytestmark = pytest.mark.integration


class TestWindPowerObservation:
    """Test wind turbine with DWD observation data."""

    def test_timeseries_not_empty(self, wind_power_obs):
        assert wind_power_obs.timeseries is not None
        assert isinstance(wind_power_obs.timeseries, (pd.Series, pd.DataFrame))
        assert not wind_power_obs.timeseries.empty

    def test_value_for_timestamp_int(self, wind_power_obs):
        val = wind_power_obs.value_for_timestamp(0)
        assert isinstance(val, (int, float))

    def test_value_for_timestamp_str(self, wind_power_obs):
        ts = str(wind_power_obs.timeseries.index[12])
        val = wind_power_obs.value_for_timestamp(ts)
        assert isinstance(val, (int, float))

    def test_observations_for_timestamp_int(self, wind_power_obs):
        obs = wind_power_obs.observations_for_timestamp(0)
        assert isinstance(obs, dict)
        assert "wind_generation" in obs

    def test_observations_for_timestamp_str(self, wind_power_obs):
        ts = str(wind_power_obs.timeseries.index[12])
        obs = wind_power_obs.observations_for_timestamp(ts)
        assert isinstance(obs, dict)
        assert "wind_generation" in obs

    def test_generation_is_nonzero(self, wind_power_obs):
        """Wind generation timeseries should contain non-zero values."""
        ts = wind_power_obs.timeseries
        if isinstance(ts, pd.DataFrame):
            col = ts.columns[0]
            values = ts[col]
        else:
            values = ts
        assert (values != 0).any(), "Expected some non-zero generation values"

    def test_power_coefficient_curve_model(self, environment_obs):
        """Exercise power_coefficient_curve model — this is what demo_wind_power.py uses."""
        wp = WindPower(
            unit="kW",
            identifier="test_wind_cp",
            environment=environment_obs,
            turbine_type="E-126/4200",
            hub_height=135,
            rotor_diameter=127,
            fetch_curve="power_curve",
            data_source="oedb",
            wind_speed_model="logarithmic",
            density_model="ideal_gas",
            temperature_model="linear_gradient",
            power_output_model="power_coefficient_curve",
            density_correction=True,
            obstacle_height=0,
            hellman_exp=None,
        )
        wp.prepare_time_series()
        assert wp.timeseries is not None
        assert not wp.timeseries.empty
        val = wp.value_for_timestamp(0)
        assert isinstance(val, (int, float))


class TestWindPowerMOSMIX:
    """Test wind turbine with MOSMIX forecast data."""

    def test_mosmix_wind_timeseries(self, environment_mosmix):
        wp = WindPower(
            unit="kW",
            identifier="test_wind_mosmix",
            environment=environment_mosmix,
            turbine_type="E-126/4200",
            hub_height=135,
            rotor_diameter=127,
            fetch_curve="power_curve",
            data_source="oedb",
            wind_speed_model="logarithmic",
            density_model="ideal_gas",
            temperature_model="linear_gradient",
            power_output_model="power_curve",
            density_correction=True,
            obstacle_height=0,
            hellman_exp=None,
        )
        wp.prepare_time_series()
        assert wp.timeseries is not None
        assert not wp.timeseries.empty
