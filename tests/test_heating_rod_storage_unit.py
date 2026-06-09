"""Offline test for point F: a HeatingRod can charge a ThermalEnergyStorage.

ThermalEnergyStorage.operate_storage expects the snake_case generator API
(is_running, ramp_up/ramp_down, observations_for_timestamp -> thermal_energy_output).
HeatingRod historically only offered camelCase; this verifies the compatibility
layer lets it drive a storage end to end.

Run with ``pytest -m "not integration"`` (no DWD/network needed).
"""

import pandas as pd

from vpplib.environment import Environment
from vpplib.heating_rod import HeatingRod
from vpplib.thermal_energy_storage import ThermalEnergyStorage


def test_heating_rod_charges_thermal_storage():
    env = Environment(
        timebase=15, start="2020-01-01 00:00:00", end="2020-01-01 23:45:00",
        time_freq="15 min", surpress_output_globally=True,
    )
    idx = pd.date_range(start=env.start, end=env.end, freq=env.time_freq)
    demand = pd.DataFrame({"thermal_energy_demand": [0.5] * len(idx)}, index=idx)

    hr = HeatingRod(
        identifier="hr", unit="kW", environment=env, thermal_energy_demand=demand,
        el_power=5, rampUpTime=1, rampDownTime=1, min_runtime=1, min_stop_time=2,
        efficiency=0.95,
    )
    tes = ThermalEnergyStorage(
        unit="kW", identifier="tes", environment=env,
        target_temperature=60, min_temperature=40, hysteresis=5,
        mass=300, cp=4.18, thermal_energy_loss_per_day=0.13,
        initial_temperature=50, raise_on_undersupply=False,
    )
    # Align both timeseries on the demand index (as a caller would).
    hr.timeseries = pd.DataFrame(columns=["heat_output", "el_demand"], index=idx)
    tes.timeseries = pd.DataFrame(columns=["temperature"], index=idx)

    for ts in idx:
        tes.operate_storage(ts, hr)  # must not raise AttributeError/KeyError

    temps = tes.timeseries["temperature"].astype(float)
    assert temps.notna().all()
    assert tes.undersupplied is False
    assert temps.min() > 40          # never drops below the minimum
    assert temps.max() > 55          # the rod actually charged the store
    # log_observation wrote back through the snake wrapper
    assert hr.timeseries["heat_output"].notna().any()
