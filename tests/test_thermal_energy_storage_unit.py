"""Offline unit tests for ThermalEnergyStorage (points G and E).

Run with ``pytest -m "not integration"`` (no DWD/network needed).
"""

import logging

import pytest

from vpplib.environment import Environment
from vpplib.thermal_energy_storage import ThermalEnergyStorage


def _env():
    return Environment(
        timebase=15,
        start="2020-01-01 00:00:00",
        end="2020-01-01 06:00:00",
        time_freq="15 min",
        surpress_output_globally=True,
    )


def _tes(initial_temperature=None, raise_on_undersupply=True):
    return ThermalEnergyStorage(
        target_temperature=60,
        min_temperature=40,
        hysteresis=5,
        mass=300,
        cp=4.18,
        thermal_energy_loss_per_day=0.13,
        unit="kW",
        identifier="tes",
        environment=_env(),
        initial_temperature=initial_temperature,
        raise_on_undersupply=raise_on_undersupply,
    )


def _usable_kwh(temp, mass=300, cp=4.18, ambient=20.0):
    """Usable energy above ambient in kWh (matches the model in point C)."""
    return mass * cp * (temp - ambient) / 3600.0


def test_default_start_temperature_unchanged():
    tes = _tes()
    assert tes.current_temperature == 60 - 5  # target - hysteresis
    assert tes.state_of_charge == _usable_kwh(60 - 5)


def test_initial_temperature_sets_consistent_soc():
    tes = _tes(initial_temperature=50)
    assert tes.current_temperature == 50
    assert tes.state_of_charge == _usable_kwh(50)


def test_state_of_charge_round_trips_to_temperature():
    tes = _tes(initial_temperature=52)
    assert tes._temperature_from_energy(tes.state_of_charge) == 52


def test_undersupply_raises_by_default():
    tes = _tes()
    tes.current_temperature = 39.0  # below min_temperature (40)
    with pytest.raises(ValueError):
        tes.get_needs_loading()
    assert tes.undersupplied is True


def test_undersupply_soft_mode_warns_and_continues(caplog):
    tes = _tes(raise_on_undersupply=False)
    tes.current_temperature = 39.0
    with caplog.at_level(logging.WARNING):
        result = tes.get_needs_loading()  # must not raise
    assert tes.undersupplied is True
    assert result is True  # still needs loading
    assert "too low" in caplog.text.lower()
