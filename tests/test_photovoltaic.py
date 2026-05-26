"""Integration tests for the Photovoltaic component."""

import pytest
import pandas as pd

from vpplib.photovoltaic import Photovoltaic


pytestmark = pytest.mark.integration


class TestPhotovoltaicObservation:
    """Test PV with DWD observation data."""

    def test_timeseries_not_empty(self, photovoltaic_obs):
        assert photovoltaic_obs.timeseries is not None
        assert isinstance(photovoltaic_obs.timeseries, pd.DataFrame)
        assert not photovoltaic_obs.timeseries.empty

    def test_value_for_timestamp_int(self, photovoltaic_obs):
        val = photovoltaic_obs.value_for_timestamp(0)
        assert isinstance(val, (int, float))

    def test_value_for_timestamp_str(self, photovoltaic_obs):
        ts = str(photovoltaic_obs.timeseries.index[48])
        val = photovoltaic_obs.value_for_timestamp(ts)
        assert isinstance(val, (int, float))

    def test_observations_for_timestamp_int(self, photovoltaic_obs):
        obs = photovoltaic_obs.observations_for_timestamp(0)
        assert isinstance(obs, dict)
        assert "el_generation" in obs

    def test_observations_for_timestamp_str(self, photovoltaic_obs):
        ts = str(photovoltaic_obs.timeseries.index[48])
        obs = photovoltaic_obs.observations_for_timestamp(ts)
        assert isinstance(obs, dict)
        assert "el_generation" in obs

    def test_generation_is_negative(self, photovoltaic_obs):
        """PV generation should be negative (generation = negative by convention)."""
        # At least some values should be negative (during daylight hours)
        ts = photovoltaic_obs.timeseries
        col = ts.columns[0]
        assert (ts[col] < 0).any(), "Expected some negative (generation) values"

    def test_surface_tilt_tuple_matches_scalar(self, environment_obs):
        """pvlib accepts surface_tilt=(20,) silently — assert it stays equivalent to scalar 20.
        Guards against a future pvlib version treating a 1-element tuple as a multi-array system."""
        common = dict(
            unit="kW",
            latitude=50.941357,
            longitude=6.958307,
            environment=environment_obs,
            module_lib="SandiaMod",
            module="Canadian_Solar_CS5P_220M___2009_",
            inverter_lib="cecinverter",
            inverter="ABB__MICRO_0_25_I_OUTD_US_208__208V_",
            surface_azimuth=200,
            modules_per_string=2,
            strings_per_inverter=2,
            temp_lib="sapm",
            temp_model="open_rack_glass_glass",
        )
        pv_scalar = Photovoltaic(identifier="tilt_scalar", surface_tilt=20, **common)
        pv_tuple = Photovoltaic(identifier="tilt_tuple", surface_tilt=(20,), **common)
        pv_scalar.prepare_time_series()
        pv_tuple.prepare_time_series()
        pd.testing.assert_frame_equal(
            pv_scalar.timeseries.rename(columns={"tilt_scalar": "power"}),
            pv_tuple.timeseries.rename(columns={"tilt_tuple": "power"}),
        )

    def test_module_peak_power_attributes(self, photovoltaic_obs):
        """module.Impo and module.Vmpo must exist and be positive — used in demo_base_scenario.py:371."""
        assert hasattr(photovoltaic_obs.module, "Impo")
        assert hasattr(photovoltaic_obs.module, "Vmpo")
        assert float(photovoltaic_obs.module.Impo) > 0
        assert float(photovoltaic_obs.module.Vmpo) > 0


class TestPhotovoltaicMOSMIX:
    """Test PV with MOSMIX forecast data."""

    def test_mosmix_pv_timeseries(self, environment_mosmix):
        pv = Photovoltaic(
            unit="kW",
            latitude=50.941357,
            longitude=6.958307,
            identifier="test_pv_mosmix",
            environment=environment_mosmix,
            module_lib="SandiaMod",
            module="Canadian_Solar_CS5P_220M___2009_",
            inverter_lib="cecinverter",
            inverter="ABB__MICRO_0_25_I_OUTD_US_208__208V_",
            surface_tilt=20,
            surface_azimuth=200,
            modules_per_string=2,
            strings_per_inverter=2,
            temp_lib="sapm",
            temp_model="open_rack_glass_glass",
        )
        pv.prepare_time_series()
        assert pv.timeseries is not None
        assert not pv.timeseries.empty

    def test_mosmix_value_for_timestamp(self, environment_mosmix):
        pv = Photovoltaic(
            unit="kW",
            latitude=50.941357,
            longitude=6.958307,
            identifier="test_pv_mosmix2",
            environment=environment_mosmix,
            module_lib="SandiaMod",
            module="Canadian_Solar_CS5P_220M___2009_",
            inverter_lib="cecinverter",
            inverter="ABB__MICRO_0_25_I_OUTD_US_208__208V_",
            surface_tilt=20,
            surface_azimuth=200,
            modules_per_string=2,
            strings_per_inverter=2,
            temp_lib="sapm",
            temp_model="open_rack_glass_glass",
        )
        pv.prepare_time_series()
        val = pv.value_for_timestamp(0)
        assert isinstance(val, (int, float))
