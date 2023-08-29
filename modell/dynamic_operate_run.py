import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from modell.dynamic_operate_modell import operate_electrolyzer
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns


#read the power curve
pnominal_generation = 5000 #kW
dfpv = pd.read_csv('..\power_generation\pv_energy_cologne.csv', header=0, index_col=0, date_parser=lambda idx: pd.to_datetime(idx, utc=True))
dfpv['PV [W]'] = (dfpv['PV [W]']/1e3)*2.5
dfpv = dfpv.rename(columns={'PV [W]':'PV [kW]'})
dfwind = pd.read_csv('..\power_generation\wind_energy_cologne.csv',
                     header=0, index_col=0, date_parser=lambda idx: pd.to_datetime(idx, utc=True))
dfwind['feedin_power_plant'] = ((dfwind['feedin_power_plant']/1e3)/4.2)*2.5
dfwind = dfwind.rename(columns={'feedin_power_plant':'wind power [kW]'})
data = pd.concat([dfwind,dfpv], axis=1)

data = data.resample('1min').interpolate(method='linear')

data['power total [kW]'] = data['wind power [kW]'] + data['PV [kW]']

# # Wandle die Werte in der Spalte 'C' in Float-Werte um
data['power total [kW]'] = data['power total [kW]'].astype(float)
data = data.loc['2015-06-01 00:00:00+00:00':'2015-06-10 23:59:00+00:00']
#Jahresdauerlinie
# sorted_data = data['power total [kW]'].sort_values(ascending=False)
# hours = range(1, len(sorted_data) + 1)
#
# # Jahresdauerlinie plotten
# sorted_data = data['power total [kW]'].sort_values(ascending=False)
# hours = np.array(list(range(1, len(sorted_data) + 1)))
# plt.plot(hours, sorted_data, color='b', linewidth=2)
# plt.fill_between(hours, sorted_data, color='b', alpha=0.3)
# # Waagerechte rote Linie hinzufügen
# plt.axhline(y=2124, color='r', linestyle='--')
# # Index des Schnittpunkts finden
# idx = next(i for i, val in enumerate(sorted_data) if val < 2124)
# # Senkrechte rote Linie am Schnittpunkt hinzufügen
# plt.axvline(x=idx, ymin=0, ymax=sorted_data[idx] / max(sorted_data), color='r', linestyle='--')
# plt.xlabel('Stunden im Jahr')
# plt.ylabel('Stromerzeugung [kW]')
# plt.title('Jahresdauerlinie der Windenergieanlage')
# plt.grid(True)
# plt.show()


# #State plot
# elec = operate_electrolyzer(5)
# df = elec.state(data)
# fig, ax1 = plt.subplots()
# #Y1-Achse ('power total [kW]')
# ax1.fill_between(df.index, df['power total [kW]'], color='lightgrey')
# ax1.set_xlabel('Zeit')
# ax1.set_ylabel('Stromerzeugung [kW]')
# # Zweite Y-Achse ('hydrogen [Nm3]')
# ax2 = ax1.twinx()
# ax2.plot(data.index, data['status codes'], alpha=0.5, label='Status')
# ax2.set_ylabel('Betriebsmodus')
# ax2.legend(loc='upper right')
# ax2.set_yticks(np.arange(1, 4 + 1, 1))
# plt.grid(True)
# plt.show()




#case 1: power profile operate
print('Betriebsweise 1: Betriebsweise nach Stromprofil')
for i in [2,5,10]:
    elec = operate_electrolyzer(i)
    df = elec.power_profile(data)
    new_status_column = f'status_{i}'
    new_status_codes_column = f'status_codes_{i}'
    new_hydrogen_column = f'hydrogen_{i} [Nm3]'
    new_heat_energy_column = f'heat energy{i} [kW/h]'
    new_surplus_electricity_column = f'Surplus electricity{i} [kW]'
    new_heat_column = f'heat_{i} [kW/h]'
    data[new_status_column] = df['status']
    data[new_status_codes_column] = df['status codes']
    data[new_hydrogen_column] = df['hydrogen [Nm3]']
    data[new_heat_energy_column] = df['heat energy [kW/h]']
    data[new_surplus_electricity_column] = df['Surplus electricity [kW]']
    data[new_heat_column] = df['heat [kW/h]']
    print(elec.P_nominal)

    volllaststunden = elec.calculate_full_load_hours(df)
    print('Vollaststunden:', volllaststunden,'h')
    betriebsstunden = (data['status'].value_counts()['production']) / 60
    print('Betriebsstunden:', betriebsstunden,'h')
    h2_production = (data['hydrogen [Nm3]'].sum())
    print('Wasserstoff:',h2_production,'m3')
    surplus_power = data['Surplus electricity [kW]'].sum()/60
    print('Überschussstrom:', surplus_power, 'kWh')
    eta = data['specific consumption'].mean()
    print('Spez. Energieverbrauch:', eta,'kWh/Nm3')
    add_energyloss = (data['heat energy loss [kW]'].sum())/60
    print('zusätzlich. Energieaufwand:' ,add_energyloss, 'kWh')
    heat = data['heat [kW/h]'].sum()/60
    print('Wärmeabgabe:', heat, 'kWh')

# # data = data.resample(rule='1d').mean()

# fig, ax1 = plt.subplots()
# # Y1-Achse ('power total [kW]')
# ax1.fill_between(data.index, data['power total [kW]'], color='lightgrey')
# ax1.set_xlabel('Zeit')
# ax1.set_ylabel('Stromerzeugung [kW]')
#
# # Zweite Y-Achse ('hydrogen [Nm3]')
# ax2 = ax1.twinx()
# hydrogen_colors = ['red', 'green', 'blue']
# hydrogen_labels = []
# for i in [2,5,10]:
#     column_name = f'hydrogen_{i} [Nm3]'
#     #color_index = int(i /2)
#     #color = hydrogen_colors[color_index]
#     ax2.plot(data.index, data[column_name], alpha=0.5)
#     hydrogen_labels.append(f'{i*531} kW')
# ax2.set_ylabel('Wasserstoffprodution [Nm3/min]')
# ax2.legend(hydrogen_labels, loc='upper right')
# ax1.set_ylim(0, 4500)
# ax2.set_ylim(0, 20)
# plt.grid(True)
#
# plt.show()

# Case 2: peakload operate
# data['new power [kW]'] = data['power total [kW]'].clip(upper=(data['power total [kW]'].quantile(0.8)))
# print('Quantil:',data['power total [kW]'].quantile(0.8), 'kW')
print('Betriebsweise 2: Überschussstrom')
for i in [2,5,10]:
    elec = operate_electrolyzer(i)
    df = elec.hydrogen_production_peakload(data)
    new_status_column = f'status_{i}'
    new_status_codes_column = f'status_codes_{i}'
    new_hydrogen_column = f'hydrogen_{i} [Nm3]'
    new_heat_energy_column = f'heat energy{i} [kW/h]'
    new_surplus_electricity_column = f'Surplus electricity{i} [kW]'
    new_heat_column = f'heat_{i} [kW/h]'
    data[new_hydrogen_column] = df['hydrogen [Nm3]']
    data[new_heat_energy_column] = df['heat energy [kW/h]']
    data[new_surplus_electricity_column] = df['Surplus electricity [kW]']
    data[new_heat_column] = df['heat [kW/h]']
    print(elec.P_nominal)

    volllaststunden = elec.calculate_full_load_hours(df)
    print('Vollaststunden:', volllaststunden,'h')
    betriebsstunden = (data['status'].value_counts()['production']) / 60
    print('Betriebsstunden:', betriebsstunden,'h')
    h2_production = (data['hydrogen [Nm3]'].sum())
    print('Wasserstoff:',h2_production,'m3')
    surplus_power = data['Surplus electricity [kW]'].sum()/60
    print('Überschussstrom:', surplus_power, 'kWh')
    eta = data['specific consumption'].mean()
    print('Spez. Energieverbrauch: ',eta,'kWh/Nm3')
    add_energyloss = (data['heat energy loss [kW]'].sum())/60
    print('zusätzlich. Energieaufwand:' ,add_energyloss, 'kWh')
    heat = data['heat [kW/h]'].sum()/60
    print('Wärmeabgabe:', heat, 'kWh')
#
# # data = data.resample(rule='1d').mean()
#
# fig, ax1 = plt.subplots()
# # Y1-Achse ('power total [kW]')
# ax1.fill_between(data.index, data['power total [kW]'], color='lightgrey')
# ax1.plot(data.index, data['new power [kW]'], color='darkgrey')
# ax1.set_xlabel('Zeit')
# ax1.set_ylabel('Stromerzeugung [kW]')

# # Zweite Y-Achse ('hydrogen [Nm3]')
# ax2 = ax1.twinx()
# hydrogen_colors = ['red', 'green', 'blue']
# hydrogen_labels = []
# for i in [2,5,10]:
#     column_name = f'hydrogen_{i} [Nm3]'
#     #color_index = int(i /2)
#     #color = hydrogen_colors[color_index]
#     ax2.plot(data.index, data[column_name], alpha=0.5)
#     hydrogen_labels.append(f'{i*531} kW')
# ax2.set_ylabel('Wasserstoffprodution [Nm3/min]')
# ax2.legend(hydrogen_labels, loc='upper right')
# ax1.set_ylim(0, 4500)
# ax2.set_ylim(0, 14)
# plt.grid(True)
# plt.show()


#Case 3: baseload operate
#
# for i in range(len(data.index)):
#     if data.loc[data.index[i], 'power total [kW]'] > 100:
#         data.loc[data.index[i], 'new power [kW]'] = data.loc[data.index[i], 'power total [kW]'] - 100
# data['new power [kW]'] = data['power total [kW]']-(data['power total [kW]'].clip(upper=(900)))
# print('Quantil:',data['power total [kW]'].quantile(0.62),'kW')

print('Betriebsweise 3: Betriebsweise durch Strom aus dem unteren leistungsbereich')
for i in [2,5,10]:
    elec = operate_electrolyzer(i)
    df = elec.hydrogen_production_baseload(data)
    new_status_column = f'status_{i}'
    new_status_codes_column = f'status_codes_{i}'
    new_hydrogen_column = f'hydrogen_{i} [Nm3]'
    new_heat_energy_column = f'heat energy{i} [kW/h]'
    new_surplus_electricity_column = f'Surplus electricity{i} [kW]'
    new_heat_column = f'heat_{i} [kW/h]'
    data[new_status_column] = df['status']
    data[new_status_codes_column] = df['status codes']
    data[new_hydrogen_column] = df['hydrogen [Nm3]']
    data[new_heat_energy_column] = df['heat energy [kW/h]']
    data[new_surplus_electricity_column] = df['Surplus electricity [kW]']
    data[new_heat_column] = df['heat [kW/h]']
    print(elec.P_nominal)

    volllaststunden = elec.calculate_full_load_hours(df)
    print('Vollaststunden:', volllaststunden,'h')
    betriebsstunden = (data['status'].value_counts()['production']) / 60
    print('Betriebsstunden:', betriebsstunden,'h')
    h2_production = (data['hydrogen [Nm3]'].sum())
    print('Wasserstoff:',h2_production,'m3')
    surplus_power = data['Surplus electricity [kW]'].sum()/60
    print('Überschussstrom:', surplus_power, 'kWh')
    eta = data['specific consumption'].mean()
    print(eta,'kWh/Nm3')
    add_energyloss = (data['heat energy loss [kW]'].sum())/60
    print('zusätzlich. Energieaufwand:' ,add_energyloss, 'kWh')
    heat = data['heat [kW/h]'].sum()/60
    print('Wärmeabgabe:', heat, 'kWh')
# print(data)
# # # data = data.resample(rule='1d').mean()
#
# fig, ax1 = plt.subplots()
# # Y1-Achse ('power total [kW]')
# ax1.fill_between(data.index, data['power total [kW]'], color='lightgrey')
# ax1.plot(data.index, data['new power [kW]'], color='darkgrey')
# ax1.set_xlabel('Zeit')
# ax1.set_ylabel('Stromerzeugung [kW]')
#
# # Zweite Y-Achse ('hydrogen [Nm3]')
# ax2 = ax1.twinx()
# hydrogen_colors = ['red', 'green', 'blue']
# hydrogen_labels = []
# for i in [2,5,10]:
#     column_name = f'hydrogen_{i} [Nm3]'
#     #color_index = int(i /2)
#     #color = hydrogen_colors[color_index]
#     ax2.plot(data.index, data[column_name], alpha=0.5)
#     hydrogen_labels.append(f'{i*531} kW')
# ax2.set_ylabel('Wasserstoffprodution [Nm3/min]')
# ax2.legend(hydrogen_labels, loc='upper right')
# ax1.set_ylim(0, 4500)
# ax2.set_ylim(0, 20)
# plt.grid(True)
#
# plt.show()


# Case 4: combine operate
print('Betriebsweise 4: kombinierte Betriebsweise')
for i in [2,5,10]:
    elec = operate_electrolyzer(i)
    df = elec.production_costs_optimization(data)
    new_status_column = f'status_{i}'
    new_status_codes_column = f'status_codes_{i}'
    new_hydrogen_column = f'hydrogen_{i} [Nm3]'
    new_heat_energy_column = f'heat energy{i} [kW/h]'
    new_surplus_electricity_column = f'Surplus electricity{i} [kW]'
    new_heat_column = f'heat_{i} [kW/h]'
    data[new_status_column] = df['status']
    data[new_status_codes_column] = df['status codes']
    data[new_hydrogen_column] = df['hydrogen [Nm3]']
    data[new_heat_energy_column] = df['heat energy [kW/h]']
    data[new_surplus_electricity_column] = df['Surplus electricity [kW]']
    data[new_heat_column] = df['heat [kW/h]']
    print(elec.P_nominal)

    volllaststunden = elec.calculate_full_load_hours(df)
    print('Vollaststunden:', volllaststunden,'h')
    betriebsstunden = (data['status'].value_counts()['production']) / 60
    print('Betriebsstunden:', betriebsstunden,'h')
    h2_production = (data['hydrogen [Nm3]'].sum())
    print('Wasserstoff:',h2_production,'m3')
    surplus_power = data['Surplus electricity [kW]'].sum()/60
    print('Überschussstrom:', surplus_power, 'kWh')
    eta = data['specific consumption'].mean()
    print(eta,'kWh/Nm3')
    add_energyloss = (data['heat energy loss [kW]'].sum())/60
    print('zusätzlich. Energieaufwand:' ,add_energyloss, 'kWh')
    heat = data['heat [kW/h]'].sum()/60
    print('Wärmeabgabe:', heat, 'kWh')

# fig, ax1 = plt.subplots()
# # Y1-Achse ('power total [kW]')
# ax1.fill_between(data.index, data['power total [kW]'], color='lightgrey')
# ax1.plot(data.index, data[f'Surplus electricity{2} [kW]'], color='darkgrey')
# ax1.set_xlabel('Zeit')
# ax1.set_ylabel('Stromerzeugung [kW]')
#
# # Zweite Y-Achse ('hydrogen [Nm3]')
# ax2 = ax1.twinx()
# hydrogen_colors = ['red', 'green', 'blue']
# hydrogen_labels = []
# for i in [2,5,10]:
#     column_name = f'hydrogen_{i} [Nm3]'
#     #color_index = int(i /2)
#     #color = hydrogen_colors[color_index]
#     ax2.plot(data.index, data[column_name], alpha=0.5)
#     hydrogen_labels.append(f'{i*531} kW')
# ax2.set_ylabel('Wasserstoffprodution [Nm3/min]')
# ax2.legend(hydrogen_labels, loc='upper right')
# ax1.set_ylim(0, 4500)
# ax2.set_ylim(0, 20)
# plt.grid(True)
#
# plt.show()


# #modulation p_nenn
# elec = operate_electrolyzer(4)
# data = elec.modulation_pnenn(data)
#
# print(data)
# print('eta 1:',data['eta 1'].mean())
# print('eta 2:',data['eta 2'].mean())
# print('eta 3:',data['eta 3'].mean())
# print('eta 4:',data['eta 4'].mean())
# print('stack 1:', data['stack 1'].sum(),'Nm3')
# print('stack 2:', data['stack 2'].sum(),'Nm3')
# print('stack 3:', data['stack 3'].sum(),'Nm3')
# print('stack 4:', data['stack 4'].sum(),'Nm3')
#
# fig, ax1 = plt.subplots()
# # Y1-Achse ('power total [kW]')
# ax1.fill_between(data.index, data['power total [kW]'], color='lightgrey')
# ax1.set_xlabel('Zeit')
# ax1.set_ylabel('Stromerzeugung [kW]')
# # Zweite Y-Achse ('hydrogen [Nm3]')
# ax2 = ax1.twinx()
# ax2.plot(data.index, data['stack 1']+data['stack 2']+data['stack 3']+data['stack 4'], alpha=0.5, label='Stack 4')
# ax2.plot(data.index, data['stack 1']+data['stack 2']+data['stack 3'], alpha=0.5, label='Stack 3')
# ax2.plot(data.index, data['stack 1']+data['stack 2'], alpha=0.5, label='Stack 2')
# ax2.plot(data.index, data['stack 1'], alpha=0.5, label='Stack 1')
# ax2.set_ylabel('Wasserstoffprodution [Nm3/min]')
# ax2.legend(loc='upper right')
# ax1.set_ylim(0, 4500)
# ax2.set_ylim(0, 18)
# plt.grid(True)
# plt.show()


#
# #modulation eta
# elec = operate_electrolyzer(4)
# data = elec.modulation_eta(data)
# print('eta 1:',data['eta 1'].mean())
# print('eta 2:',data['eta 2'].mean())
# print('eta 3:',data['eta 3'].mean())
# print('eta 4:',data['eta 4'].mean())
# print('stack 1:', data['stack 1'].sum()/60,'Nm3')
# print('stack 2:', data['stack 2'].sum()/60,'Nm3')
# print('stack 3:', data['stack 3'].sum()/60,'Nm3')
# print('stack 4:', data['stack 4'].sum()/60,'Nm3')
#
#
# print(data)
#
# fig, ax1 = plt.subplots()
# # Y1-Achse ('power total [kW]')
# ax1.fill_between(data.index, data['power total [kW]'], color='lightgrey')
# ax1.set_xlabel('Zeit')
# ax1.set_ylabel('Stromerzeugung [kW]')
#
# # Zweite Y-Achse ('hydrogen [Nm3]')
# ax2 = ax1.twinx()
# ax2.plot(data.index, data['eta 1'], alpha=0.5, label='Stack 4')
# ax2.plot(data.index, data['eta 2'], alpha=0.5, label='Stack 3')
# ax2.plot(data.index, data['eta 3'], alpha=0.5, label='Stack 2')
# ax2.plot(data.index, data['eta 4'], alpha=0.5, label='Stack 1')
# ax2.set_ylabel('Wasserstoffprodution [Nm3/min]')
# ax2.legend(loc='upper right')
# ax1.set_ylim(0, 4500)
# #ax2.set_ylim(0, 15)
#
#
# plt.grid(True)
# plt.show()


#ratio
# for i in [1,2,3,4,5,6,7,8,9,10,11,12]:
#     elec = operate_electrolyzer(i)
#     df = elec.ratio(data)
#     new_hydrogen_column = f'hydrogen_{i} [Nm3]'
#     new_surplus_electricity_column = f'Surplus electricity{i} [kW]'
#     data[new_hydrogen_column] = df['hydrogen [Nm3]']
#     data[new_surplus_electricity_column] = df['Surplus electricity [kW]']
#     print(elec.P_nominal)
#
#     volllaststunden = ((data['energy consumption'].sum()))/(i*531)
#     print('Vollaststunden:', volllaststunden,'h')
#     betriebsstunden = (data['hydrogen [Nm3]'] > 1).sum()
#     print('Betriebsstunden:', betriebsstunden,'h')
#     h2_production = (data['hydrogen [Nm3]'].sum())
#     print('Wasserstoff:',h2_production,'m3')
#     surplus_power = data['Surplus electricity [kW]'].sum()
#     print('Überschussstrom:', surplus_power, 'kWh')
#     eta = data['specific consumption'].mean()
#     print(eta,'kWh/Nm3')

# daten = pd.read_csv('../plots/simulation.csv', sep=';', decimal=',', header=0)
# daten2 = pd.read_csv('../plots/simulation_2-1.csv', sep=';', decimal=',', header=0)
# daten3 = pd.read_csv('../plots/simulation_1-2.csv', sep=';', decimal=',', header=0)
#

# Erzeugung des 3D-Plots
# daten['Nennleistung'] = daten['Nennleistung']/1000
# fig = plt.figure()
# ax = fig.add_subplot(projection='3d')
# # Plot der Datenpunkte
# ax.scatter(daten['Nennleistung'], daten['VLS'], daten['Wasserstoff'])
#ax.set_xlim(0, 6)
#ax.set_ylim(500, 6000)
#ax.set_zlim(0, 2500)

# data = daten[['Nennleistung', 'VLS', 'Wasserstoff']]
# data2 = daten2[['Nennleistung', 'VLS', 'Wasserstoff']]
# data3 = daten3[['Nennleistung', 'VLS', 'Wasserstoff']]
# # Scatterplot erstellen
# plt.figure(figsize=(10, 6))  # Größe des Diagramms festlegen
# plt.scatter(data['Nennleistung'], data['VLS'], c=data['Wasserstoff'], cmap='PuBu', s=80, label='1')
# plt.scatter(data2['Nennleistung'], data2['VLS'], c=data2['Wasserstoff'], cmap='PuBu', s=80, label='Datenreihe 2')
# plt.scatter(data3['Nennleistung'], data3['VLS'], c=data3['Wasserstoff'], cmap='PuBu', s=80, label='Datenreihe 3')
# plt.colorbar(label='Wasserstoffproduktion [Nm3/a]')  # Farbskala für den Wasserstoff hinzufügen
# plt.xlabel('Elektrolyseur Nennleistung [MW]')  # Beschriftung der x-Achse festlegen
# plt.ylabel('Volllaststunden [h/a]')  # Beschriftung der y-Achse festlegen
# plt.grid(True)
# plt.show()


#Fall PPA
# elec = operate_electrolyzer(4)
# df = elec.calculate_excess_energy(data)[0]
# fig, ax1 = plt.subplots()
# #Y1-Achse ('power total [kW]')
# df['power total [kW]'] = df['generation_adjusted [kW]']
# ax1.plot(df.index, df['power total [kW]'], label='Stromerzeugung')
# ax1.set_xlabel('Zeit')
# ax1.set_ylabel('Stromerzeugung [kW]')
# ax1.legend(loc='upper left')
# plt.grid(True)
# plt.show()
#
# df = elec.power_profile(df)
# volllaststunden = elec.calculate_full_load_hours(df)
# print('Vollaststunden:', volllaststunden, 'h')
# betriebsstunden = (data['status'].value_counts()['production']) / 60
# print('Betriebsstunden:', betriebsstunden, 'h')
# h2_production = (data['hydrogen [Nm3]'].sum())
# print('Wasserstoff:', h2_production, 'm3')
# surplus_power = data['Surplus electricity [kW]'].sum() / 60
# print('Überschussstrom:', surplus_power, 'kWh')
# eta = data['specific consumption'].mean()
# print(eta, 'kWh/Nm3')
# # add_energyloss = (data['heat energy loss [kW]'].sum()) / 60
# # print('zusätzlich. Energieaufwand:', add_energyloss, 'kWh')
# heat = data['heat [kW/h]'].sum() / 60
# print('Wärmeabgabe:', heat, 'kWh')


# #shiftet power
# # fig, ax = plt.subplots(figsize=(15,6))
# # ax.plot(df.index, df['generation [kW]'], label='power [kW]')
# # ax.plot(df.index, df['generation_adjusted [kW]'], label='power shifted [kW]')
# # ax.set_xlabel('Time')
# # ax.set_ylabel('Power [kW]')
# # ax.legend()
# # plt.show()
#
# # #netziendlicher plot 1
# # fig, ax1 = plt.subplots()
# #
# # # linkes Diagramm
# # color = 'tab:blue'
# # ax1.set_xlabel('Time')
# # ax1.set_ylabel('Power [kW]')
# # ax1.plot(df['generation [kW]'], color=color)
# # ax1.plot(df['power new [kW]'], color=color, linestyle='--')
# # ax1.tick_params(axis='y', labelcolor=color)
# # # rechtes Diagramm
# # ax2 = ax1.twinx()  # Zweite y-Achse
# # color = 'tab:orange'
# # ax2.set_ylabel('Hydrogen [Nm3]')
# # ax2.plot(df['hydrogen [Nm3]'], color=color)
# # ax2.tick_params(axis='y', labelcolor=color)
# # # Überschrift und Layout
# # fig.tight_layout()



# #Anwendungsfall1
# elec = operate_electrolyzer(4)
# df = elec.production_costs_optimization(data)
# print(df)
#
# volllaststunden = elec.calculate_full_load_hours(df)
# print('Vollaststunden:', volllaststunden,'h')
# betriebsstunden = (data['status'].value_counts()['production']) / 60
# print('Betriebsstunden:', betriebsstunden,'h')
# h2_production = (data['hydrogen [Nm3]'].sum())
# print('Wasserstoff:',h2_production,'m3')
# surplus_power = data['Surplus electricity [kW]'].sum()/60
# print('Überschussstrom:', surplus_power, 'kWh')
# eta = data['specific consumption'].mean()
# print(eta,'kWh/Nm3')
# add_energyloss = (data['heat energy loss [kW]'].sum())/60
# print('zusätzlich. Energieaufwand:' ,add_energyloss, 'kWh')
# heat = data['heat [kW/h]'].sum()/60
# print('Wärmeabgabe:', heat, 'kWh')
# sum_energy = (df['power total [kW]']*df['Day-ahead Price [EUR/kWh]']).sum()
# print('Erlös aus EE:',sum_energy/60,'€')
# ueberschuss_erlös = (df['Day-ahead Price [EUR/kWh]']*df['Surplus electricity [kW]']).sum()
# print('ueberschusserlös aus EE:',ueberschuss_erlös/60,'€')



# elec = operate_electrolyzer(4)
# df = elec.power_profile(data)
# print(df)
#
# volllaststunden = elec.calculate_full_load_hours(df)
# print('Vollaststunden:', volllaststunden,'h')
# betriebsstunden = (data['status'].value_counts()['production']) / 60
# print('Betriebsstunden:', betriebsstunden,'h')
# h2_production = (data['hydrogen [Nm3]'].sum())
# print('Wasserstoff:',h2_production,'m3')
# surplus_power = data['Surplus electricity [kW]'].sum()/60
# print('Überschussstrom:', surplus_power, 'kWh')
# eta = data['specific consumption'].mean()
# print(eta,'kWh/Nm3')
# add_energyloss = (data['heat energy loss [kW]'].sum())/60
# print('zusätzlich. Energieaufwand:' ,add_energyloss, 'kWh')
# heat = data['heat [kW/h]'].sum()/60
# print('Wärmeabgabe:', heat, 'kWh')
# sum_energy = (df['power total [kW]']*df['Day-ahead Price [EUR/kWh]']).sum()
# print('Erlös aus EE:',sum_energy/60,'€')
# ueberschuss_erlös = (df['Day-ahead Price [EUR/kWh]']*df['Surplus electricity [kW]']).sum()
# print('ueberschusserlös aus EE:',ueberschuss_erlös/60,'€')
#
# #rows = data.loc[data['Day-ahead Price [EUR/kWh]'] == quantile_value]
#
# fig, ax1 = plt.subplots()
# # Daten für linke Achse
# ax1.fill_between(df.index, df['power total [kW]'], color='gray', alpha=0.3)
# ax1.set_ylabel('Stromerzeugung [kW]')
# # Rechte Achse
# ax2 = ax1.twinx()
# ax2.plot(data.index, df['Day-ahead Price [EUR/kWh]'], color='b', linewidth=2)
# ax2.set_ylabel('Day-ahead Preis [EUR/kWh]')
# plt.xlabel('Zeit')
# plt.grid(True)
# plt.show()