
from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.heat_pump import HeatPump
import matplotlib.pyplot as plt
import pandas as pd

# Values for environment
start = "2012-01-01 00:00:00"
end = "2022-12-31 23:45:00"
time_freq = "15 min"
timestamp_int = 48
timestamp_str = "2015-01-01 12:00:00"
timebase = 15
latitude = 50.941357
longitude = 6.958307

# Values for user_profile
yearly_thermal_energy_demand = 12500
building_type = "DE_HEF33"
t_0 = 40

# Values for Heatpump
el_power = 5  # kW electric
th_power = 8  # kW thermal
heat_pump_type = "Air"
heat_sys_temp = 60
ramp_up_time = 1 / 15  # timesteps
ramp_down_time = 1 / 15  # timesteps
min_runtime = 1  # timesteps
min_stop_time = 2  # timesteps

# Create env and user_profile for ten year average values
environment = Environment(
    timebase=timebase, start=start, end=end, time_freq=time_freq
)

environment.get_dwd_temp_data(lat=latitude,lon=longitude)

#Calculate the mean temperature for each day of the year
daily_temp = environment.temp_data.resample('D').mean()
daily_temp["day_of_year"] = daily_temp.index.dayofyear
daily_mean_temperature = daily_temp.groupby('day_of_year')['temperature'].mean()
print(daily_mean_temperature.head())
daily_mean_temperature.index = pd.date_range(start='2012-01-01', periods=len(daily_mean_temperature), freq='D')
daily_mean_temperature.plot()

# Create userprofile with mean temperature und calculate thermal demand distribution
user_profile = UserProfile(
    identifier='Mean temp',
    latitude=None,
    longitude=None,
    thermal_energy_demand_yearly=yearly_thermal_energy_demand,
    mean_temp_days=pd.DataFrame(daily_mean_temperature),
    mean_temp_hours=environment.temp_data.resample('H').mean().loc["2012-01-01 00:00:00+01:00":"2012-12-31 23:45:00+01:00"],
    mean_temp_quarter_hours=environment.temp_data.loc["2012-01-01 00:00:00+01:00":"2012-12-31 23:45:00+01:00"],
    building_type=building_type,
    comfort_factor=None,
    t_0=t_0,
)

user_profile.get_thermal_energy_demand()
user_profile.thermal_energy_demand.plot()

# Create env and user_profile for actual time period
new_start = "2023-01-01 00:00:00"
new_end = "2023-01-31 23:45:00"
new_env = Environment(
    timebase=timebase, start=new_start, end=new_end, time_freq=time_freq
)

new_env.get_dwd_temp_data(lat=latitude,lon=longitude)

new_daily_temp = new_env.temp_data.resample('D').mean()
new_hourly_temp = new_env.temp_data.resample('H').mean()

# Scale the demand data to the new time period
scaled_yearly_demand = user_profile.thermal_energy_demand.loc["2012-01-01 00:00:00+01:00":"2012-01-31 23:45:00+01:00"].sum().iloc[0]/4

new_user_profile = UserProfile(
    identifier='Mean temp',
    latitude=None,
    longitude=None,
    thermal_energy_demand_yearly=scaled_yearly_demand,
    mean_temp_days=pd.DataFrame(new_daily_temp),
    mean_temp_hours=new_hourly_temp,
    mean_temp_quarter_hours=new_env.temp_data,
    building_type=building_type,
    comfort_factor=None,
    t_0=t_0,
)

new_user_profile.get_thermal_energy_demand()
new_user_profile.thermal_energy_demand.plot()