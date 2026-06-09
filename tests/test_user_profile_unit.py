"""Offline unit tests for UserProfile.get_consumerfactor (point H).

Calibrating the consumerfactor on a window much shorter than a year scales the
demand so the short window carries the full yearly demand. The library now warns
about that. Run with ``pytest -m "not integration"`` (no DWD/network needed).
"""

import logging

import pandas as pd

from vpplib.user_profile import UserProfile


def _profile_with_hdel(n_days, consumerfactor=None):
    """Build a UserProfile with only the attributes get_consumerfactor needs."""
    up = UserProfile.__new__(UserProfile)
    up.consumerfactor = consumerfactor
    up.thermal_energy_demand_yearly = 12500
    up.h_del = pd.DataFrame(
        {"h_del": [1.0] * n_days},
        index=pd.date_range("2020-01-01", periods=n_days, freq="D"),
    )
    return up


def test_short_window_warns(caplog):
    up = _profile_with_hdel(7)
    with caplog.at_level(logging.WARNING):
        cf = up.get_consumerfactor()
    assert cf == 12500 / 7
    assert "calibrated on only 7 day" in caplog.text


def test_full_year_does_not_warn(caplog):
    up = _profile_with_hdel(365)
    with caplog.at_level(logging.WARNING):
        up.get_consumerfactor()
    assert "calibrated on only" not in caplog.text


def test_supplied_consumerfactor_is_kept_and_silent(caplog):
    up = _profile_with_hdel(7, consumerfactor=0.5)
    with caplog.at_level(logging.WARNING):
        cf = up.get_consumerfactor()
    assert cf == 0.5  # not recomputed
    assert "calibrated on only" not in caplog.text
