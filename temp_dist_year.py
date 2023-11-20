
from vpplib.user_profile import UserProfile
from vpplib.environment import Environment
from vpplib.heat_pump import HeatPump
import matplotlib.pyplot as plt

# Values for environment
start = "2012-01-01 00:00:00"
end = "2022-12-31 23:45:00"
year = "2015"
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

environment = Environment(
    timebase=timebase, start=start, end=end, year=year, time_freq=time_freq
)

environment.get_dwd_temp_data(lat=latitude,lon=longitude)

daily_temp = environment.temp_data.resample('D').mean()
daily_temp["day_of_year"] = daily_temp.index.dayofyear
daily_mean_temperature = daily_temp.groupby('day_of_year')['temperature'].mean()
print(daily_mean_temperature.head())
daily_mean_temperature.plot()