"""Offline unit tests for controlled observations (point B).

``observations_for_timestamp`` must reflect the controlled operation driven by
``is_running`` and must NOT fall back to a pre-filled (uncontrolled) timeseries
value — otherwise ``operate_storage`` can never charge the storage.

Run with ``pytest -m "not integration"`` (no DWD/network needed).
"""

import pandas as pd

from vpplib.environment import Environment
from vpplib.heat_pump import HeatPump
from vpplib.heating_rod import HeatingRod


def _env_idx():
    env = Environment(
        timebase=15,
        start="2020-01-01 00:00:00",
        end="2020-01-01 03:00:00",
        time_freq="15 min",
        surpress_output_globally=True,
    )
    idx = pd.date_range(start=env.start, end=env.end, freq=env.time_freq)
    return env, idx


def test_heat_pump_observation_uses_full_capacity_when_running():
    env, idx = _env_idx()
    demand = pd.DataFrame({"thermal_energy_demand": [0.5] * len(idx)}, index=idx)
    hp = HeatPump(
        identifier="hp", unit="kW", environment=env, thermal_energy_demand=demand,
        heat_pump_type="Air", heat_sys_temp=60, el_power=5, th_power=8,
        ramp_up_time=1, ramp_down_time=1, min_runtime=1, min_stop_time=2,
    )
    # Provide temperatures for the on-the-fly COP, and pre-fill the timeseries
    # row with (uncontrolled) values to prove they are NOT used while running.
    hp.environment.mean_temp_quarter_hours = pd.DataFrame(
        {"temperature": [5.0] * len(idx)}, index=idx
    )
    hp.timeseries.loc[idx[0]] = [0.5, 3.0, 0.2]  # thermal_energy_output, cop, el_demand

    hp.is_running = True
    obs = hp.observations_for_timestamp(idx[0])
    assert obs["el_demand"] == 5  # el_power, not the pre-filled 0.2
    assert obs["thermal_energy_output"] == 5 * obs["cop"]
    assert obs["thermal_energy_output"] > 0.5  # not the pre-filled demand value

    hp.is_running = False
    obs_off = hp.observations_for_timestamp(idx[0])
    assert obs_off == {"thermal_energy_output": 0, "cop": 0, "el_demand": 0}


def test_heat_pump_observation_int_timestamp_when_running():
    """Point J: the integer-timestamp branch must not double-index temperature."""
    env, idx = _env_idx()
    demand = pd.DataFrame({"thermal_energy_demand": [0.5] * len(idx)}, index=idx)
    hp = HeatPump(
        identifier="hp", unit="kW", environment=env, thermal_energy_demand=demand,
        heat_pump_type="Air", heat_sys_temp=60, el_power=5, th_power=8,
        ramp_up_time=1, ramp_down_time=1, min_runtime=1, min_stop_time=2,
    )
    hp.environment.mean_temp_quarter_hours = pd.DataFrame(
        {"temperature": [5.0] * len(idx)}, index=idx
    )
    hp.is_running = True
    obs = hp.observations_for_timestamp(0)  # integer position -> .iloc[0]
    assert obs["el_demand"] == 5
    assert obs["cop"] > 0
    assert obs["thermal_energy_output"] == 5 * obs["cop"]


def test_heating_rod_observation_uses_full_capacity_when_running():
    env, idx = _env_idx()
    demand = pd.DataFrame({"thermal_energy_demand": [0.5] * len(idx)}, index=idx)
    hr = HeatingRod(
        identifier="hr", unit="kW", environment=env, thermal_energy_demand=demand,
        el_power=3, rampUpTime=1, rampDownTime=1, min_runtime=1, min_stop_time=2,
        efficiency=0.95,
    )
    hr.timeseries.loc[idx[0]] = [0.5, 0.2]  # heat_output, el_demand (uncontrolled)

    hr.isRunning = True
    obs = hr.observationsForTimestamp(idx[0])
    assert obs["el_demand"] == 3  # el_power, not the pre-filled 0.2
    assert obs["heat_output"] == 3 * 0.95

    hr.isRunning = False
    obs_off = hr.observationsForTimestamp(idx[0])
    assert obs_off["el_demand"] == 0 and obs_off["heat_output"] == 0
