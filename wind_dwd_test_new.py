# -*- coding: utf-8 -*-
"""
Wind Power DWD Test (New Version)
--------------------------------
This test file demonstrates how to use the latest version of wetterdienst library (0.109.0)
with the WindPower class to fetch weather data and perform wind power simulations.

It shows both MOSMIX (forecast) and observation data usage with the updated API.
"""

import matplotlib.pyplot as plt
import datetime
import pandas as pd
import numpy as np
import sys

from vpplib.environment import Environment
from vpplib.wind_power import WindPower

# windpowerlib imports
from windpowerlib import data as wt
from windpowerlib import data

# Get available wind turbine types
turbine_types = wt.get_turbine_types(print_out=False)
print(f"Available turbine types: {len(turbine_types)}")

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

def print_wind_data_info(wind_data, title="Wind Data"):
    """Print information about the wind data."""
    print(f"\n{title} Information:")
    print(f"Shape: {wind_data.shape}")
    print(f"Columns: {wind_data.columns}")
    print(f"Index: {wind_data.index[:5]}")
    print(f"Data types: {wind_data.dtypes}")
    print(f"Sample data:")
    print(wind_data.head())
    
    # Check for missing values
    missing = wind_data.isna().sum()
    print(f"\nMissing values per column:")
    print(missing)
    
    # Check for MultiIndex columns
    if isinstance(wind_data.columns, pd.MultiIndex):
        print("\nMultiIndex column levels:")
        for i, level in enumerate(wind_data.columns.names):
            print(f"Level {i}: {level}")
            print(f"Unique values: {wind_data.columns.get_level_values(i).unique()}")

def prepare_wind_data_for_windpowerlib(wind_data):
    """
    Prepare wind data for use with windpowerlib by ensuring it has the correct format.
    
    Parameters
    ----------
    wind_data : pandas.DataFrame
        The wind data to prepare
        
    Returns
    -------
    pandas.DataFrame
        The prepared wind data with the correct format for windpowerlib
    """
    print("\nPreparing wind data for windpowerlib...")
    
    try:
        # Extract the data we need
        if isinstance(wind_data.columns, pd.MultiIndex):
            # MultiIndex format
            wind_speed = wind_data[('wind_speed', 10)] if ('wind_speed', 10) in wind_data.columns else pd.Series(0, index=wind_data.index)
            temperature = wind_data[('temperature', 2)] if ('temperature', 2) in wind_data.columns else pd.Series(0, index=wind_data.index)
            pressure = wind_data[('pressure', 0)] if ('pressure', 0) in wind_data.columns else pd.Series(0, index=wind_data.index)
            roughness_length = wind_data[('roughness_length', 0)] if ('roughness_length', 0) in wind_data.columns else pd.Series(0.15, index=wind_data.index)
        else:
            # Regular DataFrame format
            wind_speed = wind_data['wind_speed'] if 'wind_speed' in wind_data.columns else pd.Series(0, index=wind_data.index)
            temperature = wind_data['temperature'] if 'temperature' in wind_data.columns else pd.Series(0, index=wind_data.index)
            pressure = wind_data['pressure'] if 'pressure' in wind_data.columns else pd.Series(0, index=wind_data.index)
            roughness_length = wind_data['roughness_length'] if 'roughness_length' in wind_data.columns else pd.Series(0.15, index=wind_data.index)
        
        # Create a new DataFrame with the correct format
        data = {
            ('wind_speed', 10): wind_speed.values,
            ('temperature', 2): temperature.values,
            ('pressure', 0): pressure.values,
            ('roughness_length', 0): roughness_length.values
        }
        
        # Create a new DataFrame with the correct MultiIndex format
        new_wind_data = pd.DataFrame(data=data, index=wind_data.index)
        
        # Set the column names explicitly
        new_wind_data.columns = pd.MultiIndex.from_tuples(
            [('wind_speed', 10), ('temperature', 2), ('pressure', 0), ('roughness_length', 0)],
            names=['variable', 'height']
        )
        
        print("Successfully prepared wind data for windpowerlib")
        return new_wind_data
    except Exception as e:
        import traceback
        print(f"Error preparing wind data: {e}")
        traceback.print_exc()
        return wind_data

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
    print_wind_data_info(environment.wind_data, "MOSMIX Wind Data")
    
    # Prepare wind data for windpowerlib
    environment.wind_data = prepare_wind_data_for_windpowerlib(environment.wind_data)
    
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
    print_wind_data_info(obs_environment.wind_data, "Observation Wind Data")
    
    # Prepare wind data for windpowerlib
    obs_environment.wind_data = prepare_wind_data_for_windpowerlib(obs_environment.wind_data)
    
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
    try:
        csv_environment.get_wind_data(
            file="./input/wind/dwd_wind_data_2015.csv",
            utc=False
        )
        
        # Print wind data information
        print_wind_data_info(csv_environment.wind_data, "CSV Wind Data")
        
        # Prepare wind data for windpowerlib
        csv_environment.wind_data = prepare_wind_data_for_windpowerlib(csv_environment.wind_data)
        
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
        test_prepare_time_series(csv_wind)
        
        # Use a timestamp from the CSV data period for testing
        test_timestamp = "2015-06-15 12:00:00"
        test_value_for_timestamp(csv_wind, test_timestamp)
    except FileNotFoundError:
        print("CSV file not found. Skipping CSV data test.")
    
except Exception as e:
    print(f"\nError with CSV data: {e}")
    print("CSV data test failed.")

print("\nWind power tests completed.")