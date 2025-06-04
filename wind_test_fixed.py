import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from vpplib.environment import Environment
from vpplib.wind_power import WindPower

# Create a sample wind data DataFrame with the correct format for windpowerlib
def create_sample_wind_data(start_date="2023-01-01", periods=24):
    """Create a sample wind data DataFrame with the correct format for windpowerlib."""
    # Create index
    index = pd.date_range(start_date, periods=periods, freq='H')
    
    # Create data
    wind_speed = np.random.uniform(2, 15, periods)  # m/s
    temperature = np.random.uniform(273, 293, periods)  # K
    pressure = np.random.uniform(101000, 103000, periods)  # Pa
    roughness_length = np.ones(periods) * 0.15  # m
    
    # Create MultiIndex columns
    columns = pd.MultiIndex.from_tuples(
        [('wind_speed', 10), ('temperature', 2), ('pressure', 0), ('roughness_length', 0)],
        names=['variable', 'height']
    )
    
    # Create DataFrame
    df = pd.DataFrame(
        {
            ('wind_speed', 10): wind_speed,
            ('temperature', 2): temperature,
            ('pressure', 0): pressure,
            ('roughness_length', 0): roughness_length
        },
        index=index
    )
    
    # Set the column names explicitly
    df.columns = columns
    
    return df

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

# Prepare time series
try:
    wind.prepare_time_series()
    print("\nPower output time series:")
    print(wind.timeseries.head())
    
    # Plot the time series
    plt.figure(figsize=(10, 6))
    wind.timeseries.plot()
    plt.title("Wind Power Output")
    plt.xlabel("Time")
    plt.ylabel("Power (kW)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("wind_power_output.png")
    print("Plot saved to wind_power_output.png")
    
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()