"""Offline unit tests for HeatingRod (point I).

Run with ``pytest -m "not integration"`` (no DWD/network needed).
"""

import pandas as pd

from vpplib.component import Component
from vpplib.environment import Environment
from vpplib.heating_rod import HeatingRod


def test_heating_rod_defines_snake_case_prepare():
    """HeatingRod must not fall back to the base-class stub (sets timeseries=[])."""
    assert HeatingRod.prepare_time_series is not Component.prepare_time_series


def test_prepare_time_series_returns_dataframe():
    env = Environment(
        timebase=15,
        start="2020-01-01 00:00:00",
        end="2020-01-01 06:00:00",
        time_freq="15 min",
        surpress_output_globally=True,
    )
    idx = pd.date_range(start=env.start, end=env.end, freq=env.time_freq)
    demand = pd.DataFrame({"thermal_energy_demand": [1.0] * len(idx)}, index=idx)
    hr = HeatingRod(
        identifier="hr", unit="kW", environment=env, thermal_energy_demand=demand,
        el_power=3, rampUpTime=1, rampDownTime=1, min_runtime=1, min_stop_time=2,
        efficiency=0.95,
    )
    result = hr.prepare_time_series()  # snake_case alias -> prepareTimeSeries
    assert isinstance(result, pd.DataFrame)
    assert isinstance(hr.timeseries, pd.DataFrame)
    assert not hr.timeseries.empty
