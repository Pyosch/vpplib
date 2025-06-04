import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from windpowerlib import ModelChain, WindTurbine
from windpowerlib import data as wt

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

# Create sample wind data
wind_data = create_sample_wind_data()

# Print wind data information
print("Wind data shape:", wind_data.shape)
print("Wind data columns:", wind_data.columns)
print("Wind data index:", wind_data.index[:5])
print("Wind data sample:")
print(wind_data.head())

# Get available wind turbine types
turbine_types = wt.get_turbine_types(print_out=False)
print(f"Available turbine types: {len(turbine_types)}")

# Create wind turbine
turbine_type = "E-126/4200"
hub_height = 135
rotor_diameter = 127

# Initialize wind turbine
wind_turbine = WindTurbine(
    turbine_type=turbine_type,
    hub_height=hub_height,
    rotor_diameter=rotor_diameter,
    fetch_curve="power_curve",
    data_source="oedb"
)

# Create modelchain data dictionary
modelchain_data = {
    "wind_speed_model": "logarithmic",
    "density_model": "ideal_gas",
    "temperature_model": "linear_gradient",
    "power_output_model": "power_curve",
    "density_correction": True,
    "obstacle_height": 0.0,
    "hellman_exp": None
}

# Try to run the model
try:
    # Initialize ModelChain with specifications and use run_model method
    mc = ModelChain(wind_turbine, **modelchain_data)
    
    # Check if the wind data has the correct format
    print("\nChecking if wind data has the correct format...")
    checked_data = wt.check_weather_data(wind_data)
    print("Wind data format is correct!")
    
    # Run the model
    print("\nRunning the model...")
    mc.run_model(wind_data)
    
    # Get power output
    power_output = mc.power_output / 1000  # convert to kW
    
    print("\nPower output time series:")
    print(power_output.head())
    
    # Plot the time series
    plt.figure(figsize=(10, 6))
    power_output.plot()
    plt.title(f"Wind Power Output - {turbine_type}")
    plt.xlabel("Time")
    plt.ylabel("Power (kW)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("windpowerlib_output.png")
    print("Plot saved to windpowerlib_output.png")
    
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()