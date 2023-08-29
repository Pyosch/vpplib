import pandas as pd
from matplotlib import pyplot as plt
from windpowerlib import WindTurbine, TurbineClusterModelChain, WindTurbineCluster, WindFarm

weather = pd.read_csv('../weather_data/dwd_pv_data_2015.csv', index_col=0, header=[0,1], sep=',',
                         date_parser=lambda idx: pd.to_datetime(idx, utc=True))

print(weather)

enercon_e126 = {
    "turbine_type": "E-126/4200",  # turbine type as in register
    "hub_height": 135,  # in m
}
e126 = WindTurbine(**enercon_e126)
print('nominal power of e126: {}'.format(e126.nominal_power))

wind_turbine_fleet = pd.DataFrame({'wind_turbine': [e126],
                                   'number_of_turbines': [1],
                                   'efficiency': [1]
                                   #'total capacity': 25.2e6
                                   })
windfarm1 = WindFarm(name='windfarm1', wind_turbine_fleet=wind_turbine_fleet)

cluster_data1 = {'name': 'example_cluster',
                 'wind_farms:': 'windfarm1'}
cluster1 = WindTurbineCluster(cluster_data1)

mc_windfarm1 = TurbineClusterModelChain(windfarm1).run_model(weather)

windfarm1.power_output = mc_windfarm1.power_output
print(windfarm1.power_output)
if plt:
    windfarm1.power_output.plot(legend=True, label='example farm')
    plt.xlabel('Wind speed in m/s')
    plt.ylabel('Power in W')
    plt.show()


# mc_data = {
#     'wake_losses_model': 'wind_farm_efficiency',
#     'smoothing': True,
#     'block_width': 0.5,
#     'standard_deviation_method': 'staffel_pfenninger',
#     'smoothing_order' : 'wind_farm_power_curves',
#     'wind_speed_model': 'logarithmic',
#     'density_model': 'ideal_gas',
#     'temperature_model': 'linear_gradient',
#     'power_output_model': 'power_curve',
#     'density_correction': True,
#     'obstacle_height': 0,
#     'hellman_exp': None,
# }
# mc_cluster1 = TurbineClusterModelChain(cluster1, **mc_data).run_model(weather)
# cluster1.power_output = mc_cluster1.power_output
# print(cluster1.power_output)

#windfarm1.power_output.to_csv('e126/4.2MW.csv')
df = windfarm1.power_output.to_frame()
#df.to_csv('wind_energy_cologne.csv')
print(df)
summe = df['feedin_power_plant'].sum()

#print(summe/1000000,'MWh')

#mc.ac.plot()
plt.show()