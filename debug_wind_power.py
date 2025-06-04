import pandas as pd
import numpy as np
from vpplib.environment import Environment
from vpplib.wind_power import WindPower
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a sample wind data DataFrame with the correct format for windpowerlib
def create_sample_wind_data(start_date="2023-01-01", periods=24):
    """Create a sample wind data DataFrame with the correct format for windpowerlib."""
    # Create index
    index = pd.date_range(start_date, periods=periods, freq='h')
    
    # Create data
    wind_speed = np.random.uniform(2, 15, periods)  # m/s
    temperature = np.random.uniform(273, 293, periods)  # K
    pressure = np.random.uniform(101000, 103000, periods)  # Pa
    roughness_length = np.ones(periods) * 0.15  # m
    
    # First create a regular DataFrame
    df = pd.DataFrame(
        {
            'wind_speed': wind_speed,
            'temperature': temperature,
            'pressure': pressure,
            'roughness_length': roughness_length
        },
        index=index
    )
    
    # Then convert to MultiIndex format
    df_multi = pd.DataFrame(
        {
            ('wind_speed', 10): df['wind_speed'],
            ('temperature', 2): df['temperature'],
            ('pressure', 0): df['pressure'],
            ('roughness_length', 0): df['roughness_length']
        },
        index=df.index
    )
    
    # Set the column names explicitly
    df_multi.columns.names = ['variable', 'height']
    
    return df_multi

# Create environment with sample wind data
env = Environment(
    start="2023-01-01 00:00:00",
    end="2023-01-01 23:00:00"
)

# Set the wind data directly
env.wind_data = create_sample_wind_data()

# Print wind data information
print("Wind data shape:", env.wind_data.shape)
print("Wind data columns:", env.wind_data.columns)
print("Wind data index:", env.wind_data.index[:5])
print("Wind data sample:")
print(env.wind_data.head())

# Create WindPower object
wind = WindPower(
    unit="kW",
    identifier="Test",
    environment=env,
    turbine_type="E-126/4200",
    hub_height=135,
    rotor_diameter=127,
    fetch_curve="power_curve",
    data_source="oedb",
    wind_speed_model="logarithmic",
    density_model="ideal_gas",
    temperature_model="linear_gradient",
    power_output_model="power_curve",
    density_correction=True,
    obstacle_height=0.0,
    hellman_exp=None
)

# Test the _ensure_wind_data_format method
print("\nTesting _ensure_wind_data_format method...")
formatted_data = wind._ensure_wind_data_format()
print("Formatted data shape:", formatted_data.shape)
print("Formatted data columns:", formatted_data.columns)
print("Formatted data sample:")
print(formatted_data.head())

# Try to check the data format using windpowerlib's check_weather_data function
try:
    from windpowerlib import data as wt
    print("\nChecking if the formatted data has the correct format for windpowerlib...")
    checked_data = wt.check_weather_data(formatted_data)
    print("Formatted data has the correct format!")
    print("Checked data sample:")
    print(checked_data.head())
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Try to run the model directly
try:
    from windpowerlib import ModelChain
    print("\nTrying to run the model directly...")
    
    # Initialize the wind turbine
    wind_turbine = wind.initialize_wind_turbine()
    print(f"Wind turbine initialized: {wind_turbine}")
    
    # Create modelchain data dictionary
    modelchain_data = {
        "wind_speed_model": wind.wind_speed_model,
        "density_model": wind.density_model,
        "temperature_model": wind.temperature_model,
        "power_output_model": wind.power_output_model,
        "density_correction": wind.density_correction,
        "obstacle_height": wind.obstacle_height,
        "hellman_exp": wind.hellman_exp
    }
    
    # Initialize ModelChain with specifications
    mc = ModelChain(wind_turbine, **modelchain_data)
    
    # Run the model
    mc.run_model(formatted_data)
    
    # Get power output
    power_output = mc.power_output / 1000  # convert to kW
    
    print("\nPower output time series:")
    print(power_output.head())
    
except Exception as e:
    print(f"Error running model directly: {e}")
    import traceback
    traceback.print_exc()