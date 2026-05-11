"""Integration tests for the Environment class and DWD data retrieval."""

import datetime
import pytest
import pandas as pd

from vpplib.environment import Environment


pytestmark = pytest.mark.integration


class TestEnvironmentConstruction:
    """Test Environment creation with various parameter combinations."""

    def test_minimal_environment(self):
        env = Environment()
        assert env is not None

    def test_environment_with_datetime_start_end(self, timestamp_now):
        start = timestamp_now + datetime.timedelta(days=-3)
        end = timestamp_now + datetime.timedelta(days=-1)
        env = Environment(
            timebase=15,
            start=start,
            end=end,
            surpress_output_globally=True,
        )
        assert env is not None

    def test_environment_with_string_start_end(self):
        env = Environment(
            start="2025-01-01 00:00:00",
            end="2025-01-02 00:00:00",
            surpress_output_globally=True,
        )
        assert env is not None

    def test_environment_rejects_invalid_range(self):
        with pytest.raises(ValueError):
            Environment(
                start="2025-01-02 00:00:00",
                end="2025-01-01 00:00:00",
                surpress_output_globally=True,
            )

    def test_get_time_from_dwd(self):
        env = Environment()
        t = env.get_time_from_dwd()
        assert isinstance(t, datetime.datetime)
        assert t.tzinfo is not None


class TestDWDObservationData:
    """Test fetching observation data from DWD."""

    def test_pv_data(self, environment_obs):
        assert environment_obs.pv_data is not None
        assert isinstance(environment_obs.pv_data, pd.DataFrame)
        assert not environment_obs.pv_data.empty

    def test_wind_data(self, environment_obs):
        assert environment_obs.wind_data is not None
        assert isinstance(environment_obs.wind_data, pd.DataFrame)
        assert not environment_obs.wind_data.empty

    def test_mean_temp_hours(self, environment_obs):
        assert environment_obs.mean_temp_hours is not None
        assert isinstance(environment_obs.mean_temp_hours, pd.DataFrame)
        assert not environment_obs.mean_temp_hours.empty

    def test_mean_temp_days(self, environment_obs):
        assert environment_obs.mean_temp_days is not None
        assert isinstance(environment_obs.mean_temp_days, pd.DataFrame)
        assert not environment_obs.mean_temp_days.empty

    def test_mean_temp_quarter_hours(self, environment_obs):
        assert environment_obs.mean_temp_quarter_hours is not None
        assert not environment_obs.mean_temp_quarter_hours.empty


class TestDWDMOSMIXData:
    """Test fetching MOSMIX forecast data from DWD."""

    def test_pv_data(self, environment_mosmix):
        assert environment_mosmix.pv_data is not None
        assert isinstance(environment_mosmix.pv_data, pd.DataFrame)
        assert not environment_mosmix.pv_data.empty

    def test_wind_data(self, environment_mosmix):
        assert environment_mosmix.wind_data is not None
        assert isinstance(environment_mosmix.wind_data, pd.DataFrame)
        assert not environment_mosmix.wind_data.empty

    def test_mean_temp_hours(self, environment_mosmix):
        assert environment_mosmix.mean_temp_hours is not None
        assert not environment_mosmix.mean_temp_hours.empty

    def test_mean_temp_days(self, environment_mosmix):
        assert environment_mosmix.mean_temp_days is not None
        assert not environment_mosmix.mean_temp_days.empty
