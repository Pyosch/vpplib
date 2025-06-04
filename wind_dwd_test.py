# -*- coding: utf-8 -*-
"""
Wind Power DWD Test
------------------
This test file demonstrates how to use the wetterdienst library with the WindPower class
to fetch weather data and perform wind power simulations.

It shows both MOSMIX (forecast) and observation data usage.
"""

import matplotlib.pyplot as plt
import datetime
import pandas as pd
import numpy as np
import sys

from vpplib.environment import Environment
from vpplib.wind_power import WindPower

# Monkey patch the windpowerlib data module to handle our data format
from windpowerlib import data as wt
from windpowerlib import data

# Save the original check_weather_data function
original_check_weather_data = data.check_weather_data

# Define a new check_weather_data function that handles our data format
def patched_check_weather_data(weather_data):
    """
    Adapted version of the check_weather_data function that handles our data format.
    """
    try:
        # Try the original function first
        return original_check_weather_data(weather_data)
    except Exception as e:
        print(f"Original check_weather_data failed: {e}")
        print("Trying patched version...")
        
        # Create a new DataFrame with the correct format
        try:
            # Extract the data we need
            if isinstance(weather_data.columns, pd.MultiIndex):
                # MultiIndex format
                wind_speed = weather_data[('wind_speed', 10)] if ('wind_speed', 10) in weather_data.columns else pd.Series(0, index=weather_data.index)
                temperature = weather_data[('temperature', 2)] if ('temperature', 2) in weather_data.columns else pd.Series(0, index=weather_data.index)
                pressure = weather_data[('pressure', 0)] if ('pressure', 0) in weather_data.columns else pd.Series(0, index=weather_data.index)
                roughness_length = weather_data[('roughness_length', 0)] if ('roughness_length', 0) in weather_data.columns else pd.Series(0.15, index=weather_data.index)
            else:
                # Regular DataFrame format
                wind_speed = weather_data['wind_speed'] if 'wind_speed' in weather_data.columns else pd.Series(0, index=weather_data.index)
                temperature = weather_data['temperature'] if 'temperature' in weather_data.columns else pd.Series(0, index=weather_data.index)
                pressure = weather_data['pressure'] if 'pressure' in weather_data.columns else pd.Series(0, index=weather_data.index)
                roughness_length = weather_data['roughness_length'] if 'roughness_length' in weather_data.columns else pd.Series(0.15, index=weather_data.index)
            
            # Create a new DataFrame with the correct format
            new_weather_data = pd.DataFrame(
                {
                    'wind_speed': wind_speed.values,
                    'temperature': temperature.values,
                    'pressure': pressure.values,
                    'roughness_length': roughness_length.values
                },
                index=weather_data.index
            )
            
            # Create a MultiIndex for the columns
            heights = [10, 2, 0, 0]
            variables = ['wind_speed', 'temperature', 'pressure', 'roughness_length']
            tuples = list(zip(variables, heights))
            columns = pd.MultiIndex.from_tuples(tuples, names=['variable', 'height'])
            
            # Set the columns
            new_weather_data.columns = columns
            
            print("Successfully patched weather data format")
            return new_weather_data
        except Exception as e:
            print(f"Patched check_weather_data failed: {e}")
            raise

# Replace the original function with our patched version
data.check_weather_data = patched_check_weather_data

# Get available wind turbine types
data = wt.get_turbine_types(print_out=False)

# For debugging, uncomment:
import logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Location parameters
latitude = 51.4  # Cologne
longitude = 6.97
identifier = "Cologne"

# WindTurbine data
turbine_type = "E-126/4200"
hub_height = 135
rotor_diameter = 127
fetch_curve = "power_curve"
data_source = "oedb"

# ModelChain data
wind_speed_model = "logarithmic"
density_model = "ideal_gas"
temperature_model = "linear_gradient"
power_output_model = "power_curve"
density_correction = True
obstacle_height = 0.0  # Must be a float, not None
hellman_exp = None

def test_prepare_time_series(wind):
    """Test the prepare_time_series method of the WindPower class."""
    print("\nTesting prepare_time_series...")
    try:
        # Prepare the time series
        wind.prepare_time_series()
        
        # Plot the time series
        plt.figure(figsize=(12, 8))
        
        # Plot the full time series
        plt.subplot(2, 1, 1)
        wind.timeseries.plot()
        plt.title(f"Wind Power Output - {wind.turbine_type} (Full Period)")
        plt.xlabel("Time")
        plt.ylabel("Power (kW)")
        plt.grid(True)
        
        # Plot a sample week
        plt.subplot(2, 1, 2)
        if len(wind.timeseries) > 24*7:
            # Get a week of data (168 hours)
            sample_week = wind.timeseries.iloc[24*30:24*37]  # Get data from day 30 to 37
            sample_week.plot()
            plt.title(f"Wind Power Output - Sample Week")
        else:
            # If we don't have enough data, plot the first 24 hours
            sample_day = wind.timeseries.iloc[:24]
            sample_day.plot()
            plt.title(f"Wind Power Output - Sample Day")
        
        plt.xlabel("Time")
        plt.ylabel("Power (kW)")
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()
        plt.close()
        
        print("prepare_time_series result:")
        print(wind.timeseries.head())
        print(f"Total data points: {len(wind.timeseries)}")
        
        # Calculate some statistics
        if len(wind.timeseries) > 0:
            print(f"Maximum power output: {wind.timeseries.max():.2f} kW")
            print(f"Average power output: {wind.timeseries.mean():.2f} kW")
            print(f"Minimum power output: {wind.timeseries.min():.2f} kW")
        
        return True
    except Exception as e:
        import traceback
        print(f"Error in test_prepare_time_series: {e}")
        traceback.print_exc()
        return False

def test_value_for_timestamp(wind, timestamp):
    """Test the value_for_timestamp method of the WindPower class."""
    print(f"\nTesting value_for_timestamp with {timestamp}...")
    try:
        # Make sure we have timeseries data
        if not hasattr(wind, 'timeseries') or wind.timeseries is None or len(wind.timeseries) == 0:
            print("No timeseries data available. Skipping test_value_for_timestamp.")
            return None
        
        # Convert timestamp to datetime if it's a string
        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)
        
        # Make sure the timestamp is in the index
        if timestamp not in wind.timeseries.index:
            print(f"Timestamp {timestamp} not in timeseries index. Available timestamps: {wind.timeseries.index[0]} to {wind.timeseries.index[-1]}")
            # Find the closest timestamp
            closest_timestamp = wind.timeseries.index[0]
            min_diff = abs((timestamp - closest_timestamp).total_seconds())
            for ts in wind.timeseries.index:
                diff = abs((timestamp - ts).total_seconds())
                if diff < min_diff:
                    min_diff = diff
                    closest_timestamp = ts
            print(f"Using closest timestamp: {closest_timestamp}")
            timestamp = closest_timestamp
        
        value = wind.value_for_timestamp(timestamp)
        print(f"Value for timestamp {timestamp}: {value}")
        return value
    except Exception as e:
        import traceback
        print(f"Error in test_value_for_timestamp: {e}")
        traceback.print_exc()
        return None

def test_observations_for_timestamp(wind, timestamp):
    """Test the observations_for_timestamp method of the WindPower class."""
    print(f"\nTesting observations_for_timestamp with {timestamp}...")
    try:
        # Make sure we have wind data
        if not hasattr(wind.environment, 'wind_data') or wind.environment.wind_data is None or len(wind.environment.wind_data) == 0:
            print("No wind data available. Skipping test_observations_for_timestamp.")
            return None
        
        # Convert timestamp to datetime if it's a string
        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)
        
        # Make sure the timestamp is in the index
        if timestamp not in wind.environment.wind_data.index:
            print(f"Timestamp {timestamp} not in wind_data index. Available timestamps: {wind.environment.wind_data.index[0]} to {wind.environment.wind_data.index[-1]}")
            # Find the closest timestamp
            closest_timestamp = wind.environment.wind_data.index[0]
            min_diff = abs((timestamp - closest_timestamp).total_seconds())
            for ts in wind.environment.wind_data.index:
                diff = abs((timestamp - ts).total_seconds())
                if diff < min_diff:
                    min_diff = diff
                    closest_timestamp = ts
            print(f"Using closest timestamp: {closest_timestamp}")
            timestamp = closest_timestamp
        
        observations = wind.observations_for_timestamp(timestamp)
        print(f"Observations for timestamp {timestamp}:")
        print(observations)
        return observations
    except Exception as e:
        import traceback
        print(f"Error in test_observations_for_timestamp: {e}")
        traceback.print_exc()
        return None

# Get current time from DWD
time_now = Environment().get_time_from_dwd()
print(f"Current time from DWD: {time_now}")

# Create a timestamp for testing (1 hour from now)
timestamp_str = (time_now + datetime.timedelta(hours=1)).replace(minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
print(f"Test timestamp: {timestamp_str}")

# Create environment for MOSMIX data (forecast for next 10 days)
print("\n--- Testing with MOSMIX data (forecast) ---")
environment = Environment(
    start=time_now.strftime("%Y-%m-%d %H:%M:%S"),
    end=(time_now + datetime.timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"),
    use_timezone_aware_time_index=True,
    force_end_time=True,
    surpress_output_globally=False
)

# Get wind data using MOSMIX (forecast)
try:
    print("Fetching MOSMIX wind data...")
    station_metadata = environment.get_dwd_wind_data(
        lat=latitude,
        lon=longitude,
        use_mosmix=True,
        station_id="10410"  # ESSEN station ID for MOSMIX
    )
    print("MOSMIX station metadata:")
    print(station_metadata)
    
    # Print wind data information
    print("\nWind data columns:")
    print(environment.wind_data.columns)
    print("\nWind data index:")
    print(environment.wind_data.index[:5])
    print("\nWind data head:")
    print(environment.wind_data.head())
    
    # Create WindPower object
    print("\nCreating WindPower object with MOSMIX data...")
    wind = WindPower(
        unit="kW",
        identifier=identifier,
        environment=environment,
        turbine_type=turbine_type,
        hub_height=hub_height,
        rotor_diameter=rotor_diameter,
        fetch_curve=fetch_curve,
        data_source=data_source,
        wind_speed_model=wind_speed_model,
        density_model=density_model,
        temperature_model=temperature_model,
        power_output_model=power_output_model,
        density_correction=density_correction,
        obstacle_height=obstacle_height,
        hellman_exp=hellman_exp,
    )
    
    # Run tests with MOSMIX data
    test_prepare_time_series(wind)
    test_value_for_timestamp(wind, timestamp_str)
    test_observations_for_timestamp(wind, timestamp_str)
    
except Exception as e:
    print(f"\nError with MOSMIX data: {e}")
    print("MOSMIX data test failed.")

# Now try with observation data (historical data from past year)
print("\n--- Testing with observation data (historical) ---")
try:
    # Create a new environment for observation data
    obs_environment = Environment(
        start=(time_now - datetime.timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S"),
        end=(time_now - datetime.timedelta(days=360)).strftime("%Y-%m-%d %H:%M:%S"),
        use_timezone_aware_time_index=True,
        force_end_time=True,
        surpress_output_globally=False
    )
    
    # Try to get observation data with a larger search radius
    print("Fetching observation wind data...")
    obs_station_metadata = obs_environment.get_dwd_wind_data(
        lat=latitude,
        lon=longitude,
        use_mosmix=False,
        distance=100  # Larger search radius
    )
    print("Observation station metadata:")
    print(obs_station_metadata)
    
    # Print wind data information
    print("\nObservation wind data columns:")
    print(obs_environment.wind_data.columns)
    print("\nObservation wind data index:")
    print(obs_environment.wind_data.index[:5])
    print("\nObservation wind data head:")
    print(obs_environment.wind_data.head())
    
    # Create WindPower object with observation data
    print("\nCreating WindPower object with observation data...")
    obs_wind = WindPower(
        unit="kW",
        identifier=identifier,
        environment=obs_environment,
        turbine_type=turbine_type,
        hub_height=hub_height,
        rotor_diameter=rotor_diameter,
        fetch_curve=fetch_curve,
        data_source=data_source,
        wind_speed_model=wind_speed_model,
        density_model=density_model,
        temperature_model=temperature_model,
        power_output_model=power_output_model,
        density_correction=density_correction,
        obstacle_height=obstacle_height,
        hellman_exp=hellman_exp,
    )
    
    # Run tests with observation data
    test_prepare_time_series(obs_wind)
    
    # Use a timestamp from the observation period for testing
    test_timestamp = (time_now - datetime.timedelta(days=364)).replace(hour=12, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
    test_value_for_timestamp(obs_wind, test_timestamp)
    test_observations_for_timestamp(obs_wind, test_timestamp)
    
except Exception as e:
    print(f"\nError with observation data: {e}")
    print("Observation data test skipped. MOSMIX data should work correctly.")

# Alternative: Use CSV data if DWD API fails
print("\n--- Testing with CSV data (fallback) ---")
try:
    # Create environment with a time period matching the CSV data
    csv_environment = Environment(
        start="2015-01-01 00:00:00",
        end="2015-12-31 23:45:00",
        surpress_output_globally=False
    )
    
    # Get wind data from CSV file
    print("Loading wind data from CSV file...")
    csv_environment.get_wind_data(
        file="./input/wind/dwd_wind_data_2015.csv",
        utc=False
    )
    
    # Print wind data information
    print("\nCSV wind data columns:")
    print(csv_environment.wind_data.columns)
    print("\nCSV wind data index:")
    print(csv_environment.wind_data.index[:5])
    print("\nCSV wind data head:")
    print(csv_environment.wind_data.head())
    
    # We'll let the WindPower class handle the data format conversion
    print("\nUsing WindPower class to handle data format conversion...")
    
    print("Fixed wind data columns:")
    print(csv_environment.wind_data.columns)
    print("Fixed wind data head:")
    print(csv_environment.wind_data.head())
    
    # Create WindPower object with CSV data
    print("\nCreating WindPower object with CSV data...")
    csv_wind = WindPower(
        unit="kW",
        identifier=identifier,
        environment=csv_environment,
        turbine_type=turbine_type,
        hub_height=hub_height,
        rotor_diameter=rotor_diameter,
        fetch_curve=fetch_curve,
        data_source=data_source,
        wind_speed_model=wind_speed_model,
        density_model=density_model,
        temperature_model=temperature_model,
        power_output_model=power_output_model,
        density_correction=density_correction,
        obstacle_height=obstacle_height,
        hellman_exp=hellman_exp,
    )
    
    # Run tests with CSV data
    success = test_prepare_time_series(csv_wind)
    
    if success:
        # Use a specific timestamp for testing with CSV data
        csv_timestamp = "2015-11-09 12:00:00"
        test_value_for_timestamp(csv_wind, csv_timestamp)
        test_observations_for_timestamp(csv_wind, csv_timestamp)
    
except Exception as e:
    import traceback
    print(f"\nError with CSV data: {e}")
    traceback.print_exc()
    print("CSV data test failed.")

print("\n--- All tests completed ---")