"""
Created on Thu Aug 22 15:33:53 2019

@author: patri, pyosch
"""
import matplotlib.pyplot as plt
import datetime
from tqdm import tqdm

from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.thermal_energy_storage import ThermalEnergyStorage
from vpplib.combined_heat_and_power import CombinedHeatAndPower

figsize = (10, 6)

start = "2015-01-01 00:00:00"
end = "2015-01-10 23:45:00"
year = "2015"
periods = None
time_freq = "15 min"

# Values for user_profile
yearly_thermal_energy_demand = 2500  # kWh
building_type = "DE_HEF33"
t_0 = 40  # °C

# Values for Thermal Storage
target_temperature = 60  # °C
min_temperature = 40  # °C
hysteresis = 5  # °K
mass_of_storage = 500  # kg
cp = 4.2
thermal_energy_loss_per_day = 0.13

# Values for chp
el_power = 4  # kw
th_power = 12  # kW
overall_efficiency = 0.8
ramp_up_time = 1 / 15  # timesteps
ramp_down_time = 1 / 15  # timesteps
min_runtime = 1  # timesteps
min_stop_time = 2  # timesteps
timebase = 15


environment = Environment(
    timebase=timebase, start=start, end=end, year=year, time_freq=time_freq
)

user_profile = UserProfile(
    identifier=None,
    latitude=None,
    longitude=None,
    thermal_energy_demand_yearly=yearly_thermal_energy_demand,
    building_type=building_type,
    comfort_factor=None,
    t_0=t_0,
)


def test_get_thermal_energy_demand(user_profile):

    user_profile.get_thermal_energy_demand()
    user_profile.thermal_energy_demand.plot()
    plt.show()


test_get_thermal_energy_demand(user_profile)

tes = ThermalEnergyStorage(
    environment=environment,
    unit="kWh",
    mass=mass_of_storage,
    hysteresis=hysteresis,
    target_temperature=target_temperature,
    min_temperature=min_temperature,
    cp=cp,
    thermal_energy_loss_per_day=thermal_energy_loss_per_day,
)

chp = CombinedHeatAndPower(
    unit="kW",
    identifier="chp1",
    environment=environment,
    thermal_energy_demand=user_profile.thermal_energy_demand,
    el_power=el_power,
    th_power=th_power,
    overall_efficiency=overall_efficiency,
    ramp_up_time=ramp_up_time,
    ramp_down_time=ramp_down_time,
    min_runtime=min_runtime,
    min_stop_time=min_stop_time,
)


for i in tqdm(chp.timeseries.index):
    tes.operate_storage(i, chp)


# tes.timeseries.plot(figsize=figsize, title="Yearly Temperature of Storage")
# plt.show()
tes.timeseries.iloc[0:960].plot(figsize=figsize,
                                title="10-Day View of Storagetemperature")
plt.show()
tes.timeseries.iloc[0:96].plot(figsize=figsize,
                               title="Daily View of Storagetemperature")
plt.show()
# chp.timeseries.el_demand.plot(
#     figsize=figsize, title="Yearly Electrical Loadshape"
# )
plt.show()
chp.timeseries.el_demand.iloc[0:960].plot(
    figsize=figsize, title="10-Day View of Electrical Generation"
)
plt.show()
chp.timeseries.el_demand.iloc[0:96].plot(
    figsize=figsize, title="Daily View of Electrical Generation"
)
plt.show()


"""MOSMIX
Using dwd mosmix (weather forecast) database for temperature data.
The forecast is queried for the next 10 days automatically.
"""
print("\n" + "="*60)
print("MOSMIX CHP Test")
print("="*60)

latitude = 50.941357
longitude = 6.958307
time_now = Environment().get_time_from_dwd()
# Round up to next full hour so the 15-min grid aligns with MOSMIX hourly data
mosmix_start = (time_now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
mosmix_environment = Environment(
    timebase=timebase,
    start=mosmix_start,
    end=mosmix_start + datetime.timedelta(hours=239),
    force_end_time=True,
    use_timezone_aware_time_index=True,
    time_freq=time_freq,
    surpress_output_globally=False
)
mosmix_environment.get_dwd_mean_temp_hours(lat=latitude, lon=longitude, min_quality_per_parameter=10)
mosmix_environment.get_dwd_mean_temp_days(lat=latitude, lon=longitude, min_quality_per_parameter=10)
mosmix_environment.mean_temp_quarter_hours = mosmix_environment.mean_temp_hours.resample("15 Min").interpolate()

mosmix_user_profile = UserProfile(
    identifier=None,
    latitude=None,
    longitude=None,
    thermal_energy_demand_yearly=yearly_thermal_energy_demand,
    mean_temp_days=mosmix_environment.mean_temp_days,
    mean_temp_hours=mosmix_environment.mean_temp_hours,
    mean_temp_quarter_hours=mosmix_environment.mean_temp_quarter_hours,
    building_type=building_type,
    comfort_factor=None,
    t_0=t_0,
)
mosmix_user_profile.get_thermal_energy_demand()

mosmix_chp = CombinedHeatAndPower(
    unit="kW",
    identifier="chp1_mosmix",
    environment=mosmix_environment,
    thermal_energy_demand=mosmix_user_profile.thermal_energy_demand,
    el_power=el_power,
    th_power=th_power,
    overall_efficiency=overall_efficiency,
    ramp_up_time=ramp_up_time,
    ramp_down_time=ramp_down_time,
    min_runtime=min_runtime,
    min_stop_time=min_stop_time,
)

mosmix_tes = ThermalEnergyStorage(
    environment=mosmix_environment,
    unit="kWh",
    mass=mass_of_storage,
    hysteresis=hysteresis,
    target_temperature=target_temperature,
    min_temperature=min_temperature,
    cp=cp,
    thermal_energy_loss_per_day=thermal_energy_loss_per_day,
)

try:
    for i in tqdm(mosmix_chp.timeseries.index):
        mosmix_tes.operate_storage(i, mosmix_chp)
except ValueError as e:
    print(f"\nStorage simulation stopped early: {e}")
    print("This can happen when CHP parameters are not tuned for the forecast period.")

print("MOSMIX CHP timeseries head:")
print(mosmix_chp.timeseries.head())
mosmix_chp.timeseries.el_demand.iloc[0:96].plot(
    figsize=figsize, title="MOSMIX Daily View of Electrical Generation"
)
plt.show()
