"""Offline unit tests for ThermalEnergyStorage (point G).

Run with ``pytest -m "not integration"`` (no DWD/network needed).
"""

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


def _tes(initial_temperature=None):
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
    )


def test_default_start_temperature_unchanged():
    tes = _tes()
    assert tes.current_temperature == 60 - 5  # target - hysteresis
    assert tes.state_of_charge == 300 * 4.18 * ((60 - 5) + 273.15)


def test_initial_temperature_sets_consistent_soc():
    tes = _tes(initial_temperature=50)
    assert tes.current_temperature == 50
    assert tes.state_of_charge == 300 * 4.18 * (50 + 273.15)
