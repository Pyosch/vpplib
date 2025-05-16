Simple Virtual Power Plant
======================

This example shows how to create a simple virtual power plant with a photovoltaic system and a battery.

.. code-block:: python

   import vpplib
   import pandas as pd
   import matplotlib.pyplot as plt
   
   # Create an environment
   env = vpplib.Environment(timebase=15, timezone="Europe/Berlin")
   
   # Create weather data
   weather_data = pd.DataFrame({
       "datetime": pd.date_range(start="2020-07-01", end="2020-07-02", freq="15min"),
       "temperature": [25.0] * 97,
       "irradiance": [0.0] * 97,
       "wind_speed": [5.0] * 97
   })
   
   # Set irradiance to follow a typical daily pattern
   for i in range(97):
       hour = i // 4
       if 6 <= hour < 21:  # Daylight hours (6:00 - 21:00)
           # Simple bell curve for irradiance
           irradiance = 1000 * (1 - ((hour - 13.5) / 7.5) ** 2)
           if irradiance < 0:
               irradiance = 0
           weather_data.loc[i, "irradiance"] = irradiance
   
   # Load weather data
   env.load_weather_from_dataframe(
       dataframe=weather_data,
       datetime_column="datetime",
       temperature_column="temperature",
       irradiance_column="irradiance",
       wind_speed_column="wind_speed"
   )
   
   # Create a photovoltaic system
   pv = vpplib.Photovoltaic(
       unit="kW",
       identifier="PV_1",
       environment=env,
       module_lib="SandiaMod",
       module="Canadian_Solar_CS5P_220M___2009_",
       inverter_lib="SandiaInverter",
       inverter="ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_",
       surface_tilt=30,
       surface_azimuth=180,
       modules_per_string=10,
       strings_per_inverter=2
   )
   
   # Create a battery
   battery = vpplib.ElectricalEnergyStorage(
       unit="kW",
       identifier="Battery_1",
       environment=env,
       capacity=100,
       max_power=50,
       efficiency=0.95,
       self_discharge=0.001
   )
   
   # Create a user profile with a constant load of 2 kW
   user = vpplib.UserProfile(timebase=15)
   user.load_power_from_csv(
       filepath="load_profile.csv",
       datetime_column="datetime",
       power_column="power"
   )
   
   # If the load profile file doesn't exist, create a constant load
   try:
       user.get_power("2020-07-01 00:00:00")
   except:
       # Create a constant load of 2 kW
       load_data = pd.DataFrame({
           "datetime": pd.date_range(start="2020-07-01", end="2020-07-02", freq="15min"),
           "power": [2.0] * 97
       })
       user.load_power_from_dataframe(
           dataframe=load_data,
           datetime_column="datetime",
           power_column="power"
       )
   
   # Create a virtual power plant
   vpp = vpplib.VirtualPowerPlant(identifier="VPP_1")
   
   # Add the photovoltaic system and battery to the virtual power plant
   vpp.add_component(pv)
   vpp.add_component(battery)
   
   # Create an operator that maximizes self-consumption
   class MaximizeSelfConsumption(vpplib.Operator):
       def operate(self, time):
           # Get the current power balance
           power_balance = self.vpp.get_power_balance(time)
           
           # Get the battery
           battery = self.vpp.get_component("Battery_1")
           
           # Get the user load
           user_load = user.get_power(time)
           
           # Calculate the net power (PV - load)
           pv_power = pv.get_power(time)
           net_power = pv_power - user_load
           
           # If there is excess power, charge the battery
           if net_power > 0:
               battery.charge(net_power, time)
           # If there is a power deficit, discharge the battery
           elif net_power < 0:
               battery.discharge(abs(net_power), time)
   
   operator = MaximizeSelfConsumption(vpp=vpp)
   
   # Prepare the simulation
   vpp.prepare_simulation()
   
   # Run the simulation
   vpp.simulate(start="2020-07-01 00:00:00", end="2020-07-02 00:00:00")
   
   # Get the results
   results = vpp.get_results()
   
   # Plot the results
   fig, ax = plt.subplots(figsize=(12, 6))
   
   # Plot PV power
   ax.plot(results.index, results["PV_1"], label="PV Power", color="orange")
   
   # Plot battery power
   ax.plot(results.index, results["Battery_1"], label="Battery Power", color="blue")
   
   # Plot user load
   user_load = pd.Series(
       [user.get_power(time) for time in results.index],
       index=results.index
   )
   ax.plot(results.index, -user_load, label="User Load", color="red")
   
   # Plot grid exchange
   grid_exchange = results["PV_1"] + results["Battery_1"] - user_load
   ax.plot(results.index, grid_exchange, label="Grid Exchange", color="green")
   
   ax.set_xlabel("Time")
   ax.set_ylabel("Power (kW)")
   ax.set_title("Virtual Power Plant Simulation")
   ax.legend()
   ax.grid(True)
   
   plt.tight_layout()
   plt.savefig("vpp_simulation.png")
   plt.show()
   
   print("Simulation completed successfully!")