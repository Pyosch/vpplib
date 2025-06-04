import pandas as pd
import numpy as np

# Create a sample DataFrame with MultiIndex columns
data = {
    ('wind_speed', 10): np.random.rand(5),
    ('temperature', 2): np.random.rand(5),
    ('pressure', 0): np.random.rand(5),
    ('roughness_length', 0): np.random.rand(5)
}

# Create index
index = pd.date_range('2023-01-01', periods=5, freq='H')

# Create DataFrame with MultiIndex columns
df = pd.DataFrame(data, index=index)

# Set the column names explicitly
df.columns = pd.MultiIndex.from_tuples(
    [('wind_speed', 10), ('temperature', 2), ('pressure', 0), ('roughness_length', 0)],
    names=['variable', 'height']
)

print("DataFrame with MultiIndex columns:")
print(df)
print("\nColumn names:", df.columns.names)
print("Column values:", df.columns.values)
print("Column level 0:", df.columns.get_level_values(0))
print("Column level 1:", df.columns.get_level_values(1))

# Check if the DataFrame has the correct format for windpowerlib
try:
    from windpowerlib import data
    print("\nChecking if the DataFrame has the correct format for windpowerlib...")
    result = data.check_weather_data(df)
    print("Success! The DataFrame has the correct format.")
    print(result)
except Exception as e:
    print(f"Error: {e}")