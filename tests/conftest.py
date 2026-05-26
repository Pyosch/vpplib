"""Shared fixtures for vpplib integration tests.

All tests in this suite are integration tests that require internet access
to fetch weather data from the DWD Open Data portal. They are marked with
``@pytest.mark.integration`` so they can be skipped with::

    pytest -m "not integration"
"""

import datetime
import pytest
import pandas as pd

from vpplib.environment import Environment
from vpplib.user_profile import UserProfile
from vpplib.photovoltaic import Photovoltaic
from vpplib.wind_power import WindPower
from vpplib.heat_pump import HeatPump
from vpplib.heating_rod import HeatingRod
from vpplib.combined_heat_and_power import CombinedHeatAndPower
from vpplib.electrical_energy_storage import ElectricalEnergyStorage
from vpplib.battery_electric_vehicle import BatteryElectricVehicle
from vpplib.thermal_energy_storage import ThermalEnergyStorage
from vpplib.virtual_power_plant import VirtualPowerPlant


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LATITUDE = 50.941357
LONGITUDE = 6.958307
TIMEBASE = 15
TIME_FREQ = "15 min"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _round_to_quarter_hour(dt):
    """Round a datetime down to the nearest 15-minute boundary."""
    minute = (dt.minute // 15) * 15
    return dt.replace(minute=minute, second=0, microsecond=0)


# ---------------------------------------------------------------------------
# Environment fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def timestamp_now():
    """Current UTC time rounded to the last quarter hour."""
    return _round_to_quarter_hour(
        datetime.datetime.now(datetime.timezone.utc)
    )


@pytest.fixture(scope="session")
def environment_obs(timestamp_now):
    """Environment with DWD observation data (last 5 days)."""
    env = Environment(
        timebase=TIMEBASE,
        start=timestamp_now + datetime.timedelta(days=-5),
        end=timestamp_now + datetime.timedelta(days=-1),
        time_freq=TIME_FREQ,
        use_timezone_aware_time_index=True,
        surpress_output_globally=True,
    )
    env.get_dwd_pv_data(lat=LATITUDE, lon=LONGITUDE)
    env.get_dwd_wind_data(lat=LATITUDE, lon=LONGITUDE)
    env.get_dwd_mean_temp_hours(lat=LATITUDE, lon=LONGITUDE)
    env.get_dwd_mean_temp_days(lat=LATITUDE, lon=LONGITUDE)
    env.mean_temp_quarter_hours = (
        env.mean_temp_hours.resample("15min").interpolate()
    )
    return env


@pytest.fixture(scope="session")
def environment_mosmix(timestamp_now):
    """Environment with DWD MOSMIX forecast data (next ~10 days)."""
    start = (timestamp_now + datetime.timedelta(hours=1)).replace(
        minute=0, second=0, microsecond=0
    )
    env = Environment(
        timebase=TIMEBASE,
        start=start,
        end=start + datetime.timedelta(hours=239),
        time_freq=TIME_FREQ,
        force_end_time=True,
        use_timezone_aware_time_index=True,
        surpress_output_globally=True,
    )
    env.get_dwd_pv_data(
        lat=LATITUDE, lon=LONGITUDE, min_quality_per_parameter=10
    )
    env.get_dwd_wind_data(lat=LATITUDE, lon=LONGITUDE)
    env.get_dwd_mean_temp_hours(
        lat=LATITUDE, lon=LONGITUDE, min_quality_per_parameter=10
    )
    env.get_dwd_mean_temp_days(
        lat=LATITUDE, lon=LONGITUDE, min_quality_per_parameter=10
    )
    env.mean_temp_quarter_hours = (
        env.mean_temp_hours.resample("15min").interpolate()
    )
    return env


# ---------------------------------------------------------------------------
# UserProfile fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def user_profile_obs(environment_obs):
    """UserProfile with observation-based temperature data."""
    up = UserProfile(
        identifier="test_user",
        latitude=LATITUDE,
        longitude=LONGITUDE,
        thermal_energy_demand_yearly=12500,
        mean_temp_days=environment_obs.mean_temp_days,
        mean_temp_hours=environment_obs.mean_temp_hours,
        mean_temp_quarter_hours=environment_obs.mean_temp_quarter_hours,
        building_type="DE_HEF33",
        t_0=40,
    )
    up.get_thermal_energy_demand()
    return up


@pytest.fixture(scope="session")
def user_profile_mosmix(environment_mosmix):
    """UserProfile with MOSMIX-based temperature data."""
    up = UserProfile(
        identifier="test_user_mosmix",
        latitude=LATITUDE,
        longitude=LONGITUDE,
        thermal_energy_demand_yearly=12500,
        mean_temp_days=environment_mosmix.mean_temp_days,
        mean_temp_hours=environment_mosmix.mean_temp_hours,
        mean_temp_quarter_hours=environment_mosmix.mean_temp_quarter_hours,
        building_type="DE_HEF33",
        t_0=40,
    )
    up.get_thermal_energy_demand()
    return up


# ---------------------------------------------------------------------------
# Component fixtures — Observation
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def photovoltaic_obs(environment_obs):
    """PV system with observation data."""
    pv = Photovoltaic(
        unit="kW",
        latitude=LATITUDE,
        longitude=LONGITUDE,
        identifier="test_pv",
        environment=environment_obs,
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
    return pv


@pytest.fixture(scope="session")
def wind_power_obs(environment_obs):
    """Wind turbine with observation data."""
    wp = WindPower(
        unit="kW",
        identifier="test_wind",
        environment=environment_obs,
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
    return wp


@pytest.fixture(scope="session")
def heat_pump_obs(environment_obs, user_profile_obs):
    """Heat pump with observation data."""
    hp = HeatPump(
        identifier="test_hp",
        unit="kW",
        environment=environment_obs,
        thermal_energy_demand=user_profile_obs.thermal_energy_demand,
        el_power=5,
        th_power=8,
        heat_pump_type="Air",
        heat_sys_temp=60,
        ramp_up_time=1 / 15,
        ramp_down_time=1 / 15,
        min_runtime=1,
        min_stop_time=2,
    )
    hp.prepare_time_series()
    return hp


@pytest.fixture(scope="session")
def bev_obs(environment_obs):
    """Battery electric vehicle with observation data."""
    bev = BatteryElectricVehicle(
        unit="kW",
        identifier="test_bev",
        environment=environment_obs,
        battery_max=16,
        battery_min=0,
        battery_usage=1,
        charging_power=11,
        load_degradation_begin=0.8,
        charge_efficiency=0.98,
    )
    bev.prepare_time_series()
    return bev


@pytest.fixture(scope="session")
def chp_obs(environment_obs, user_profile_obs):
    """Combined heat and power with observation data."""
    chp = CombinedHeatAndPower(
        unit="kW",
        identifier="test_chp",
        environment=environment_obs,
        thermal_energy_demand=user_profile_obs.thermal_energy_demand,
        el_power=4,
        th_power=12,
        overall_efficiency=0.8,
        ramp_up_time=1 / 15,
        ramp_down_time=1 / 15,
        min_runtime=1,
        min_stop_time=2,
    )
    return chp


@pytest.fixture(scope="session")
def heating_rod_obs(environment_obs, user_profile_obs):
    """Heating rod with observation data."""
    hr = HeatingRod(
        identifier="test_hr",
        unit="kW",
        environment=environment_obs,
        thermal_energy_demand=user_profile_obs.thermal_energy_demand,
        el_power=3,
        rampUpTime=1 / 15,
        rampDownTime=1 / 15,
        min_runtime=1,
        min_stop_time=2,
    )
    hr.prepareTimeSeries()
    return hr


@pytest.fixture(scope="session")
def storage_obs(environment_obs, photovoltaic_obs):
    """Electrical energy storage with observation data and residual load."""
    storage = ElectricalEnergyStorage(
        unit="kW",
        identifier="test_storage",
        environment=environment_obs,
        capacity=4,
        charge_efficiency=0.98,
        discharge_efficiency=0.98,
        max_power=4,
        max_c=1,
    )
    # Build a residual load from PV, aligned to the full environment range
    full_index = pd.date_range(
        start=environment_obs.start,
        end=environment_obs.end,
        freq=environment_obs.time_freq,
    )
    pv_ts = photovoltaic_obs.timeseries
    col = pv_ts.columns[0] if hasattr(pv_ts, "columns") else None
    pv_series = pv_ts[col] if col is not None else pv_ts.iloc[:, 0]
    pv_series = pv_series.reindex(full_index, fill_value=0)
    baseload_kw = pd.Series(0.5, index=full_index)
    storage.residual_load = baseload_kw + pv_series  # positive=load, negative=generation
    storage.prepare_time_series()
    return storage


@pytest.fixture(scope="session")
def tes_and_hp_obs(environment_obs, user_profile_obs):
    """Thermal energy storage + heat pump pair for operate_storage tests."""
    hp = HeatPump(
        identifier="test_tes_hp",
        unit="kW",
        environment=environment_obs,
        thermal_energy_demand=user_profile_obs.thermal_energy_demand,
        el_power=5,
        th_power=8,
        heat_pump_type="Air",
        heat_sys_temp=60,
        ramp_up_time=1 / 15,
        ramp_down_time=1 / 15,
        min_runtime=1,
        min_stop_time=2,
    )
    tes = ThermalEnergyStorage(
        environment=environment_obs,
        unit="kWh",
        mass=500,
        hysteresis=5,
        target_temperature=60,
        min_temperature=40,
        cp=4.2,
        thermal_energy_loss_per_day=0.13,
    )
    return tes, hp


@pytest.fixture(scope="session")
def heating_rod_mosmix(environment_mosmix, user_profile_mosmix):
    """HeatingRod using MOSMIX forecast data — mirrors demo_heating_rod.py MOSMIX block."""
    hr = HeatingRod(
        identifier="test_hr_mosmix",
        unit="kW",
        environment=environment_mosmix,
        thermal_energy_demand=user_profile_mosmix.thermal_energy_demand,
        el_power=3,
        rampUpTime=1 / 15,
        rampDownTime=1 / 15,
        min_runtime=1,
        min_stop_time=2,
    )
    hr.prepareTimeSeries()
    return hr


@pytest.fixture(scope="session")
def heat_pump_mosmix(environment_mosmix, user_profile_mosmix):
    """HeatPump using MOSMIX forecast data — mirrors demo_heat_pump.py MOSMIX block."""
    hp = HeatPump(
        identifier="test_hp_mosmix",
        unit="kW",
        environment=environment_mosmix,
        thermal_energy_demand=user_profile_mosmix.thermal_energy_demand,
        el_power=5,
        th_power=8,
        heat_pump_type="Air",
        heat_sys_temp=60,
        ramp_up_time=1 / 15,
        ramp_down_time=1 / 15,
        min_runtime=1,
        min_stop_time=2,
    )
    hp.prepare_time_series()
    return hp
