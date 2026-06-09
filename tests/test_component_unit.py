"""Offline unit tests for the timezone-alignment helper.

Run with ``pytest -m "not integration"`` (no DWD/network needed).
"""

import pandas as pd

from vpplib.component import align_timestamp_tz


def test_naive_to_naive_unchanged():
    ts = align_timestamp_tz("2026-03-01 00:00:00", None)
    assert ts.tzinfo is None
    assert ts == pd.Timestamp("2026-03-01 00:00:00")


def test_naive_to_aware_localizes_wallclock():
    ts = align_timestamp_tz("2026-03-01 00:00:00", "Europe/Berlin")
    assert ts.tzinfo is not None
    assert ts.tz_localize(None) == pd.Timestamp("2026-03-01 00:00:00")


def test_aware_to_naive_keeps_wallclock():
    aware = pd.Timestamp("2026-03-01 00:00:00", tz="Europe/Berlin")
    ts = align_timestamp_tz(aware, None)
    assert ts.tzinfo is None
    assert ts == pd.Timestamp("2026-03-01 00:00:00")


def test_aware_to_aware_keeps_instant():
    aware = pd.Timestamp("2026-03-01 00:00:00", tz="UTC")
    ts = align_timestamp_tz(aware, "Europe/Berlin")
    assert ts.tzinfo is not None
    assert ts == aware  # same instant, different representation
