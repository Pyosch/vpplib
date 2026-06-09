"""Offline unit tests for BatteryElectricVehicle (no DWD/network required).

These complement the integration tests in
``test_battery_electric_vehicle.py`` and can be run with::

    pytest -m "not integration"
"""

import random

import pandas as pd

from vpplib.environment import Environment
from vpplib.battery_electric_vehicle import BatteryElectricVehicle


def _make_bev(week_start, week_end, weekend_start, weekend_end):
    """Build a BEV on a tiny offline environment (no weather data needed)."""
    env = Environment(
        timebase=15,
        start="2020-01-01 00:00:00",
        end="2020-01-03 23:45:00",
        time_freq="15 min",
        surpress_output_globally=True,
    )
    return BatteryElectricVehicle(
        unit="kW",
        identifier="bev_test",
        environment=env,
        battery_max=50,
        battery_min=10,
        battery_usage=20,
        charging_power=11,
        load_degradation_begin=0.8,
        charge_efficiency=0.95,
        week_trip_start=week_start,
        week_trip_end=week_end,
        weekend_trip_start=weekend_start,
        weekend_trip_end=weekend_end,
    )


def test_set_at_home_single_trip_time_does_not_crash():
    """Regression for point D: randrange(0, len-1) crashed for length-1 lists.

    A single configured trip time previously raised
    ``ValueError: empty range for randrange()``.
    """
    bev = _make_bev(["07:00:00"], ["18:00:00"], ["09:00:00"], ["20:00:00"])
    bev.prepare_time_series()  # must not raise
    assert isinstance(bev.timeseries, pd.DataFrame)
    assert not bev.timeseries.empty
    assert "at_home" in bev.timeseries.columns


def test_set_at_home_can_select_last_trip_index(monkeypatch):
    """The last trip-time entry must be selectable (old code dropped it)."""
    # Force randrange to return its maximum valid index for the new single-arg
    # form randrange(len(x)) -> len(x) - 1.
    monkeypatch.setattr(random, "randrange", lambda stop: stop - 1)
    bev = _make_bev(
        ["07:00:00", "07:30:00"],
        ["17:00:00", "18:00:00"],
        ["09:00:00", "09:30:00"],
        ["19:00:00", "20:00:00"],
    )
    bev.prepare_time_series()  # exercises the last index without error
    assert not bev.timeseries.empty
