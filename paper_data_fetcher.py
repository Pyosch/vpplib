
from vpplib.environment import Environment


latitude = 51.090674
longitude = 6.49642

#timezone = "Europe/Berlin"
timestamp_int = 12

environment = Environment(
    start="2024-03-01 00:00:00", 
    end="2024-03-07 23:45:00",
    time_freq="15min",
    surpress_output_globally=False,
    force_end_time=False,
    extended_solar_data=True
    )
environment.get_dwd_wind_data(lat=latitude, lon=longitude,station_splitting=True)

environment.wind_data.to_csv("/Users/x/Documents/Uni/MaEE/Masterprojekt/Paper/wind.csv", sep =';')
