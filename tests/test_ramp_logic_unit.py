"""Offline unit tests for the ramp control logic (point A).

Verifies that the ramp validators are side-effect-free predicates and that
``ramp_up``/``ramp_down`` update ``last_ramp_up``/``last_ramp_down`` so that
``min_runtime``/``min_stop_time`` are actually enforced.

Run with ``pytest -m "not integration"`` (no DWD/network needed).
"""

import pandas as pd

from vpplib.environment import Environment
from vpplib.heat_pump import HeatPump
from vpplib.heating_rod import HeatingRod


def _env_and_demand(hours=6):
    env = Environment(
        timebase=15,
        start="2020-01-01 00:00:00",
        end=f"2020-01-01 {hours:02d}:00:00",
        time_freq="15 min",
        surpress_output_globally=True,
    )
    idx = pd.date_range(start=env.start, end=env.end, freq=env.time_freq)
    demand = pd.DataFrame({"thermal_energy_demand": [1.0] * len(idx)}, index=idx)
    return env, idx, demand


def test_heat_pump_ramp_respects_min_stop_and_run_time():
    env, idx, demand = _env_and_demand()
    hp = HeatPump(
        identifier="hp", unit="kW", environment=env, thermal_energy_demand=demand,
        heat_pump_type="Air", heat_sys_temp=60, el_power=5, th_power=8,
        ramp_up_time=1, ramp_down_time=1, min_runtime=2, min_stop_time=3,
    )
    assert hp.is_running is False
    assert hp.last_ramp_up == idx[0] and hp.last_ramp_down == idx[0]

    # Too early: min_stop_time (3 steps) not yet elapsed since last_ramp_down.
    assert hp.ramp_up(idx[2]) is False
    assert hp.is_running is False

    # After min_stop_time elapsed -> may switch on; last_ramp_up updated.
    assert hp.ramp_up(idx[4]) is True
    assert hp.is_running is True
    assert hp.last_ramp_up == idx[4]

    # Too early to switch off: min_runtime (2 steps) not yet elapsed.
    assert hp.ramp_down(idx[5]) is False
    assert hp.is_running is True

    # After min_runtime elapsed -> may switch off; last_ramp_down updated.
    assert hp.ramp_down(idx[7]) is True
    assert hp.is_running is False
    assert hp.last_ramp_down == idx[7]


def test_heat_pump_validators_are_pure_predicates():
    env, idx, demand = _env_and_demand()
    hp = HeatPump(
        identifier="hp", unit="kW", environment=env, thermal_energy_demand=demand,
        heat_pump_type="Air", heat_sys_temp=60, el_power=5, th_power=8,
        ramp_up_time=1, ramp_down_time=1, min_runtime=2, min_stop_time=3,
    )
    before = hp.is_running
    result = hp.is_valid_ramp_up(idx[4])
    assert isinstance(result, bool)
    assert hp.is_running == before  # no side effect


def test_heating_rod_ramp_respects_min_stop_and_run_time():
    env, idx, demand = _env_and_demand()
    hr = HeatingRod(
        identifier="hr", unit="kW", environment=env, thermal_energy_demand=demand,
        el_power=3, rampUpTime=1, rampDownTime=1, min_runtime=2, min_stop_time=3,
    )
    assert hr.isRunning is False
    assert hr.lastRampUp == idx[0] and hr.lastRampDown == idx[0]

    assert hr.rampUp(idx[2]) is False
    assert hr.isRunning is False

    assert hr.rampUp(idx[4]) is True
    assert hr.isRunning is True
    assert hr.lastRampUp == idx[4]

    assert hr.rampDown(idx[5]) is False
    assert hr.isRunning is True

    assert hr.rampDown(idx[7]) is True
    assert hr.isRunning is False
    assert hr.lastRampDown == idx[7]
