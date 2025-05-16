Advanced Virtual Power Plant
=======================

This example shows how to create a more advanced virtual power plant with multiple components and a custom operation strategy.

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
   
   # Create a user profile
   user = vpplib.UserProfile(timebase=15)
   
   # Create a load profile
   load_data = pd.DataFrame({
       "datetime": pd.date_range(start="2020-07-01", end="2020-07-02", freq="15min"),
       "power": [2.0] * 97
   })
   
   # Set power to follow a typical daily pattern
   for i in range(97):
       hour = i // 4
       if 6 <= hour < 9:  # Morning peak (6:00 - 9:00)
           load_data.loc[i, "power"] = 4.0
       elif 17 <= hour < 22:  # Evening peak (17:00 - 22:00)
           load_data.loc[i, "power"] = 5.0
       elif 0 <= hour < 6:  # Night (0:00 - 6:00)
           load_data.loc[i, "power"] = 1.0
   
   user.load_power_from_dataframe(
       dataframe=load_data,
       datetime_column="datetime",
       power_column="power"
   )
   
   # Create a heat profile
   heat_data = pd.DataFrame({
       "datetime": pd.date_range(start="2020-07-01", end="2020-07-02", freq="15min"),
       "heat": [1.0] * 97
   })
   
   # Set heat to follow a typical daily pattern
   for i in range(97):
       hour = i // 4
       if 6 <= hour < 9:  # Morning peak (6:00 - 9:00)
           heat_data.loc[i, "heat"] = 3.0
       elif 17 <= hour < 22:  # Evening peak (17:00 - 22:00)
           heat_data.loc[i, "heat"] = 2.0
       elif 0 <= hour < 6:  # Night (0:00 - 6:00)
           heat_data.loc[i, "heat"] = 0.5
   
   user.load_heat_from_dataframe(
       dataframe=heat_data,
       datetime_column="datetime",
       heat_column="heat"
   )
   
   # Create components
   
   # Photovoltaic system
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
   
   # Wind turbine
   wind = vpplib.WindPower(
       unit="kW",
       identifier="Wind_1",
       environment=env,
       nominal_power=10,
       hub_height=50,
       rotor_diameter=20,
       cut_in_wind_speed=3,
       cut_out_wind_speed=25,
       nominal_wind_speed=12
   )
   
   # Combined heat and power
   chp = vpplib.CombinedHeatAndPower(
       unit="kW",
       identifier="CHP_1",
       environment=env,
       nominal_electrical_power=5,
       nominal_thermal_power=10,
       electrical_efficiency=0.3,
       thermal_efficiency=0.6,
       overall_efficiency=0.9
   )
   
   # Electrical energy storage
   battery = vpplib.ElectricalEnergyStorage(
       unit="kW",
       identifier="Battery_1",
       environment=env,
       capacity=20,
       max_power=10,
       efficiency=0.95,
       self_discharge=0.001
   )
   
   # Thermal energy storage
   tes = vpplib.ThermalEnergyStorage(
       unit="kW",
       identifier="TES_1",
       environment=env,
       capacity=50,
       max_power=10,
       efficiency=0.9,
       self_discharge=0.002
   )
   
   # Heat pump
   hp = vpplib.HeatPump(
       unit="kW",
       identifier="HP_1",
       environment=env,
       user_profile=user,
       nominal_power=5,
       cop=3.5
   )
   
   # Create a virtual power plant
   vpp = vpplib.VirtualPowerPlant(identifier="VPP_1")
   
   # Add components to the virtual power plant
   vpp.add_component(pv)
   vpp.add_component(wind)
   vpp.add_component(chp)
   vpp.add_component(battery)
   vpp.add_component(tes)
   vpp.add_component(hp)
   
   # Create a custom operator
   class AdvancedOperator(vpplib.Operator):
       def operate(self, time):
           # Get components
           battery = self.vpp.get_component("Battery_1")
           tes = self.vpp.get_component("TES_1")
           chp = self.vpp.get_component("CHP_1")
           hp = self.vpp.get_component("HP_1")
           
           # Get user demands
           electrical_demand = user.get_power(time)
           thermal_demand = user.get_heat(time)
           
           # Get renewable generation
           pv_power = pv.get_power(time)
           wind_power = wind.get_power(time)
           renewable_power = pv_power + wind_power
           
           # Calculate electrical balance
           electrical_balance = renewable_power - electrical_demand
           
           # Operate CHP based on thermal demand
           if thermal_demand > tes.get_power(time):
               chp.turn_on(time)
           else:
               chp.turn_off(time)
           
           # Update electrical balance with CHP
           electrical_balance += chp.get_power(time)
           
           # Operate battery
           if electrical_balance > 0:
               # Excess power, charge battery
               battery.charge(electrical_balance, time)
           else:
               # Power deficit, discharge battery
               battery.discharge(abs(electrical_balance), time)
           
           # Update electrical balance with battery
           electrical_balance += battery.get_power(time)
           
           # Operate heat pump if there's excess electrical power
           if electrical_balance > 0:
               hp.turn_on(time)
           else:
               hp.turn_off(time)
           
           # Update thermal balance
           thermal_balance = chp.get_thermal_power(time) + hp.get_thermal_power(time) - thermal_demand
           
           # Operate thermal energy storage
           if thermal_balance > 0:
               # Excess heat, charge TES
               tes.charge(thermal_balance, time)
           else:
               # Heat deficit, discharge TES
               tes.discharge(abs(thermal_balance), time)
   
   operator = AdvancedOperator(vpp=vpp)
   
   # Prepare the simulation
   vpp.prepare_simulation()
   
   # Run the simulation
   vpp.simulate(start="2020-07-01 00:00:00", end="2020-07-02 00:00:00")
   
   # Get the results
   results = vpp.get_results()
   
   # Plot the electrical results
   fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
   
   # Plot electrical power
   ax1.plot(results.index, results["PV_1"], label="PV", color="orange")
   ax1.plot(results.index, results["Wind_1"], label="Wind", color="blue")
   ax1.plot(results.index, results["CHP_1"], label="CHP (electrical)", color="red")
   ax1.plot(results.index, results["Battery_1"], label="Battery", color="green")
   ax1.plot(results.index, results["HP_1"], label="Heat Pump", color="purple")
   
   # Plot user electrical load
   user_load = pd.Series(
       [user.get_power(time) for time in results.index],
       index=results.index
   )
   ax1.plot(results.index, -user_load, label="Electrical Load", color="black", linestyle="--")
   
   ax1.set_xlabel("Time")
   ax1.set_ylabel("Power (kW)")
   ax1.set_title("Electrical Power Flows")
   ax1.legend()
   ax1.grid(True)
   
   # Plot thermal power
   thermal_results = pd.DataFrame(index=results.index)
   thermal_results["CHP"] = [chp.get_thermal_power(time) for time in results.index]
   thermal_results["HP"] = [hp.get_thermal_power(time) for time in results.index]
   thermal_results["TES"] = [tes.get_power(time) for time in results.index]
   
   ax2.plot(thermal_results.index, thermal_results["CHP"], label="CHP (thermal)", color="red")
   ax2.plot(thermal_results.index, thermal_results["HP"], label="Heat Pump", color="purple")
   ax2.plot(thermal_results.index, thermal_results["TES"], label="Thermal Storage", color="green")
   
   # Plot user thermal load
   user_heat = pd.Series(
       [user.get_heat(time) for time in results.index],
       index=results.index
   )
   ax2.plot(thermal_results.index, -user_heat, label="Thermal Load", color="black", linestyle="--")
   
   ax2.set_xlabel("Time")
   ax2.set_ylabel("Power (kW)")
   ax2.set_title("Thermal Power Flows")
   ax2.legend()
   ax2.grid(True)
   
   plt.tight_layout()
   plt.savefig("advanced_vpp_simulation.png")
   plt.show()
   
   print("Simulation completed successfully!")