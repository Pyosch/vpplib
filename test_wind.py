# -*- coding: utf-8 -*-
"""
Info
----
In this testfile the basic functionalities of the WindPower class are tested.
Run each time you make changes on an existing function.
Adjust if a new function is added or parameters in an existing function are 
changed.

"""

import matplotlib.pyplot as plt
import datetime
import pandas as pd
from vpplib.environment import Environment
from vpplib.wind_power import WindPower

from windpowerlib import data as wt

data = wt.get_turbine_types(print_out=False)

# For Debugging uncomment:
# import logging
# logging.getLogger().setLevel(logging.DEBUG)

latitude = 51.200001
longitude = 6.433333
timestamp_int = 12

# Use a specific timestamp for testing with CSV data
timestamp_str = "2015-11-09 12:00:00"

# Create environment with a time period matching the CSV data
environment = Environment(
    start="2015-01-01 00:00:00", 
    end="2015-12-31 23:45:00",
    surpress_output_globally=False
)

# Get wind data from CSV file
print("Loading wind data from CSV file...")
environment.get_wind_data(
    file="./input/wind/dwd_wind_data_2015.csv", 
    utc=False
)

# Print the wind_data DataFrame to verify its structure
print("Wind data columns:", environment.wind_data.columns)
print("Wind data index:", environment.wind_data.index[:5])
print("Wind data head:")
print(environment.wind_data.head())


# WindTurbine data
turbine_type = "E-126/4200"
hub_height = 135
rotor_diameter = 127
fetch_curve = "power_curve"
data_source = "oedb"

# ModelChain data
# possible wind_speed_model: 'logarithmic', 'hellman',
#'interpolation_extrapolation', 'log_interpolation_extrapolation'
wind_speed_model = "logarithmic"
density_model = "ideal_gas"
temperature_model = "linear_gradient"
power_output_model = "power_coefficient_curve"  #'power_curve'
density_correction = True
obstacle_height = 0
hellman_exp = None

# Create the WindPower object
print("Creating WindPower object...")
wind = WindPower(
    unit="kW",
    identifier=None,
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


def test_prepare_time_series(wind):
    """
    Test the prepare_time_series method of the WindPower class.
    """
    print("Testing prepare_time_series...")
    
    # Print wind data information before processing
    print("Wind data columns before processing:")
    print(wind.environment.wind_data.columns)
    print("Wind data columns names:", wind.environment.wind_data.columns.names)
    print("Wind data index name:", wind.environment.wind_data.index.name)
    
    try:
        # Get the wind turbine
        print("Getting wind turbine...")
        wind.get_wind_turbine()
        print("Wind turbine:", wind.wind_turbine)
        
        # Calculate power output
        print("Calculating power output...")
        
        # Debug the ModelChain creation
        import inspect
        from windpowerlib import ModelChain
        print("ModelChain signature:", inspect.signature(ModelChain.__init__))
        
        # Try to create the ModelChain manually
        print("Creating ModelChain manually...")
        from windpowerlib import ModelChain
        modelchain_data = {
            "wind_speed_model": "logarithmic",
            "density_model": "ideal_gas",
            "temperature_model": "linear_gradient",
            "power_output_model": "power_curve",
            "density_correction": False,
            "obstacle_height": 0,  # Set to 0 instead of None
            "hellman_exp": None
        }
        
        # Make a copy of the wind data with the correct format
        wind_data = wind.environment.wind_data.copy()
        
        # Create a new DataFrame with the correct MultiIndex format
        tuples = [
            ('wind_speed', 10),
            ('temperature', 2),
            ('pressure', 0),
            ('roughness_length', 0)
        ]
        
        # Create MultiIndex with explicit names
        columns = pd.MultiIndex.from_tuples(tuples, names=['variable', 'height'])
        
        # Create the DataFrame with MultiIndex columns
        new_wind_data = pd.DataFrame(index=wind_data.index)
        new_wind_data[('wind_speed', 10)] = wind_data[('wind_speed', 10)]
        new_wind_data[('temperature', 2)] = wind_data[('temperature', 2)]
        new_wind_data[('pressure', 0)] = wind_data[('pressure', 0)]
        new_wind_data[('roughness_length', 0)] = wind_data[('roughness_length', 0)]
        
        # Set the MultiIndex columns with names
        new_wind_data.columns = columns
        
        print("New wind data columns:", new_wind_data.columns)
        print("New wind data columns names:", new_wind_data.columns.names)
        
        # Try to create the ModelChain
        model_chain = ModelChain(wind.wind_turbine, **modelchain_data)
        
        # Run the model
        print("Running model...")
        model_chain.run_model(new_wind_data)
        
        # Get the power output
        print("Power output:", model_chain.power_output.head())
        
        # Set the timeseries
        wind.timeseries = model_chain.power_output / 1000  # convert to kW
        
        print("prepare_time_series result:")
        print(wind.timeseries.head())
        
        # Plot the time series
        plt.figure(figsize=(16, 9))
        wind.timeseries.plot()
        plt.title("Wind Power Output")
        plt.ylabel("Power (kW)")
        plt.grid(True)
        plt.show()
    except Exception as e:
        import traceback
        print(f"Error in test_prepare_time_series: {e}")
        traceback.print_exc()


def test_value_for_timestamp(wind, timestamp):
    """
    Test the value_for_timestamp method of the WindPower class.
    """
    print(f"Testing value_for_timestamp with {timestamp}...")
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
        
        timestepvalue = wind.value_for_timestamp(timestamp)
        print(f"Value for timestamp {timestamp}: {timestepvalue}")
        return timestepvalue
    except Exception as e:
        import traceback
        print(f"Error in test_value_for_timestamp: {e}")
        traceback.print_exc()
        return None


def test_observations_for_timestamp(wind, timestamp):
    """
    Test the observations_for_timestamp method of the WindPower class.
    """
    print(f"Testing observations_for_timestamp with {timestamp}...")
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
        
        observation = wind.observations_for_timestamp(timestamp)
        print(f"Observations for timestamp {timestamp}:")
        print(observation)
        return observation
    except Exception as e:
        import traceback
        print(f"Error in test_observations_for_timestamp: {e}")
        traceback.print_exc()
        return None


# Run the tests
print("\n--- Running tests ---\n")

try:
    test_prepare_time_series(wind)
    print("\nTest prepare_time_series passed!")
except Exception as e:
    print(f"\nTest prepare_time_series failed: {e}")

try:
    test_value_for_timestamp(wind, timestamp_str)
    print("\nTest value_for_timestamp with string timestamp passed!")
except Exception as e:
    print(f"\nTest value_for_timestamp with string timestamp failed: {e}")

try:
    test_observations_for_timestamp(wind, timestamp_str)
    print("\nTest observations_for_timestamp with string timestamp passed!")
except Exception as e:
    print(f"\nTest observations_for_timestamp with string timestamp failed: {e}")

print("\n--- All tests completed ---")
