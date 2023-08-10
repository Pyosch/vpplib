import numpy as np
import pandas as pd
import sys
sys.path.append('../11120991_End_Moritz_MA/python_code')
from modell.electrolyzer_modell import Electrolyzer
import matplotlib.pyplot as plt

T = 50  # temp
#hhv = 39.41  # lower heating value of H2 [kWh/kg]
lhv = 33.33 # lower heating value of H2 [kWh/kg]
n_cells = 60
#n_cells = 1
M = 2.016 #g/mol
hilfs_variabel = M/1000 #kg/mol
roh_H2 = 0.08988 #kg/m3

#Simulate one stack with 682 kW nominal power
elec = Electrolyzer(n_cells, 2500, T, dt=1)
P_nominal_stack = elec.stack_nominal()  #Stack nominal in kW
print(P_nominal_stack)
#
# #create Dataframe with Power input of 1% to 100% of nominal Power of Stack
# P_in = np.arange(P_nominal_stack/100, P_nominal_stack, 6)
# data = pd.DataFrame({"Power AC [kW]": P_in})
# #data = data.assign(mass_flow=pd.Series(dtype=float))
#
#
#
# for i in range(len(data.index)):
#     #add an auxiliary column for relative power of the stack (1-100%)
#     data['relative power [%]'] = (data['Power AC [kW]'] / (P_nominal_stack))*100
#
#     #calculate cell current and voltage
#     data.loc[data.index[i], 'current'] = elec.calculate_cell_current((data.loc[data.index[i],'Power AC [kW]'])*1000)/2500 #Current with kW in W and devided with cell area
#     data.loc[data.index[i], 'voltage'] = elec.calc_cell_voltage(data.loc[data.index[i], 'current'], T)
#
#     #calculate mass flow H2 in kg
#     data.loc[data.index[i], 'mass_flow H2 [kg]'] = elec.run((data.loc[data.index[i], 'Power AC [kW]'])*1000)
#
#     #calculate specific energy consumption
#
#     #calculate mass flor rate O2 in kg
#     data.loc[data.index[i], 'mass_flow O2 [kg]'] = elec.calc_O_mfr(data.loc[data.index[i], 'mass_flow H2 [kg]'])
#
#     #calculale mass flow H20
#     data.loc[data.index[i], 'mass_flow H2O [kg]'] = elec.calc_H2O_mfr(data.loc[data.index[i], 'mass_flow H2 [kg]'])
#
#     #calculate heat prozentual and in KiloWatt
#     data.loc[data.index[i], 'heat [W]'] = elec.heat_cell((data.loc[data.index[i],'Power AC [kW]'])*1000)
#     data.loc[data.index[i], 'heat [kW]'] = data.loc[data.index[i], 'heat [W]']/1000
#     data['heat [%]'] = (data['heat [kW]'] / data['Power AC [kW]']) * 100 #prozenutal of nominal Power Stack
#
#
#     #calculate system heat
#     data.loc[data.index[i], 'heat fresh water [W]'] = (elec.heat_sys((data.loc[data.index[i], 'heat [kW]']),
#                                                                     (data.loc[data.index[i], 'mass_flow H2O [kg]'])
#                                                                      )[1])
#     data['heat fresh water [kW]'] = data['heat fresh water [W]']
#     data['heat fresh water [%]'] = (data['heat fresh water [kW]'] / data['Power AC [kW]']) * 100
#
#     data.loc[data.index[i], 'heat loss [W]'] = elec.heat_sys((data.loc[data.index[i], 'heat [kW]']),
#                                                                     (data.loc[data.index[i], 'mass_flow H2O [kg]']))[0]
#     data.loc[data.index[i], 'heat loss [kW]'] = data.loc[data.index[i], 'heat loss [W]']
#     data['heat loss [%]'] = (data['heat loss [kW]'] / data['Power AC [kW]']) * 100
#
#     data['heat system [kW]'] = data['heat [kW]'] + data['heat fresh water [kW]'] + data['heat loss [kW]']
#     data['heat system [%]'] = (data['heat system [kW]']/data['Power AC [kW]']) * 100
#
#     if data.loc[data.index[i], 'heat system [kW]'] < 0:
#         data.loc[data.index[i], 'Power heat fresh water [kW]'] = - data.loc[data.index[i],'heat fresh water [kW]']
#     else:
#         data.loc[data.index[i], 'Power heat fresh water [kW]'] = 0.0
#     data['Power heat fresh water [%]'] = (data['Power heat fresh water [kW]']/data['Power AC [kW]']) * 100
#
#     #calculate mfr cooling water
#     data.loc[data.index[i], 'mass_flow H2O cooling [kg]'] = elec.calc_mfr_cool(data.loc[data.index[i], 'heat system [kW]'])
#     #data['mass_flow H2O cooling [kg]'] = (data['mass_flow H2O cooling [kg]'])# + data['mass_flow H2O [kg]'])
#
#     #calculate Pump energy
#     data.loc[data.index[i], 'Pump fresh water [kW]'] = elec.calc_pump((data.loc[data.index[i], 'mass_flow H2O [kg]']),
#                                                                        (P_nominal_stack), (data.loc[data.index[i],'Power AC [kW]']),3000000)[0]
#     data['Pump fresh water [%]'] = (data['Pump fresh water [kW]']/data['Power AC [kW]'])*100
#
#     data.loc[data.index[i], 'Pump cooling [kW]'] = elec.calc_pump(data.loc[data.index[i], 'mass_flow H2O cooling [kg]'],
#                                                                                P_nominal_stack, (data.loc[data.index[i],'Power AC [kW]']),400000)[1]
#     data['Pump cooling [%]'] = (data['Pump cooling [kW]']/data['Power AC [kW]'])*100
#
#     data['pump energy total [kW]'] = data['Pump fresh water [kW]'] + data['Pump cooling [kW]']
#     data['pump energy total [%]'] = (data['pump energy total [kW]']/data['Power AC [kW]'])*100
#
#     #calculate the Power of the power electronics
#     data.loc[data.index[i], 'PE [kW]'] = elec.power_electronics(P_nominal_stack, data.loc[data.index[i], 'Power AC [kW]'])
#     data['eta PE [%]'] = (data['PE [kW]']/data['Power AC [kW]'])*100
#
#     #drying
#     data.loc[data.index[i], 'drying [kW]'] = (elec.gas_drying(data.loc[data.index[i], 'mass_flow H2 [kg]']))/1000
#     data['drying [%]'] = (data['drying [kW]']/data['Power AC [kW]'])*100
#
#     #all energy losses
#     data['energy losses total [kW]'] = data['pump energy total [kW]'] + data['PE [kW]'] + data['drying [kW]'] + data['Power heat fresh water [kW]']
#
#     data['energy losses total [%]'] = (data['energy losses total [kW]']/data['Power AC [kW]'])*100
#
#     #calculate eta
#     data['eta_lhv'] = (data['mass_flow H2 [kg]'] * lhv) / (data['Power AC [kW]'] + data['energy losses total [kW]'])
#     data['eta_lhv electrolyze'] = (data['mass_flow H2 [kg]'] * lhv) / data['Power AC [kW]']
#
#     #calculate energy consumption
#     data['energy consumption [kWh/m3]'] = (data['Power AC [kW]'] + data['energy losses total [kW]'])/ (data['mass_flow H2 [kg]']/roh_H2)
#
#
# #compression
# compression = elec.compression(200)
# #data['pump energy total [%]'] = (data['pump energy total [kW]']/data['Power AC [kW]'])*100
# print('P_compression:',compression,'kWh/kg')
# print('P_compression:',compression*data['mass_flow H2 [kg]'].iloc[-1],'kWh/h')
# #data.to_csv('electrolyzer_model.csv', index=False)
# #data[['relative power [%]', 'energy consumption [kWh/m3]']].to_csv('plots/my_power_curve.csv', index=False)
#
# data = data.drop(data.index[:5])
#
#
# # #Eta curve Power Electronics
# # fig, ax = plt.subplots()
# # ax.plot(data2["Power AC [%]"], data2['eta PE [%]'], 'bo-', linewidth=2)
# # ax.set_xlabel('Relative Leistung [%]', fontsize=12)
# # ax.set_ylabel('Wirkungsgrad [%]', fontsize=12)
# # ax.set_title('Wirkungsgradverlauf der Leistungselektronik', fontsize=16)
# # plt.grid(True)
#
# #heat curve
# # fig, ax = plt.subplots()
# # ax.plot(data2['relative power [kW]'], data2['heat [%]'], 'bo-', linewidth=2)
# # ax.set_xlabel('Relative Leistung [%]', fontsize=12)
# # ax.set_ylabel('Abwärme [%]', fontsize=12)
# # ax.set_title('prozentuale Wärmeabgabe', fontsize=16)
# # plt.grid(True)
#
# # #heat curve system
# fig, ax = plt.subplots()
# x = data['relative power [%]']
# ax.plot(x, data['heat [%]'], label='Wärmestrom Stack')
# ax.plot(x, data['heat fresh water [%]'], label='Wärmestrom Frischwasser')
# ax.plot(x, data['heat loss [%]'], label='Verlustwärmestrom')
# ax.plot(x, data['heat system [%]'], label='Wärmestrom System')
# ax.set_xlabel('Relative Leistung [%]')
# ax.set_ylabel('Wärmestrom [%]')
# ax.set_title('Wärmeströme im System')
# plt.grid(True)
# ax.legend()
#
#
# #Pump and mfr
# fig, ax = plt.subplots()
# x = data['relative power [%]']
# ax.plot(x, data['Pump fresh water [kW]']*0.3, label='Frischwasser Pumpe')
# ax.plot(x, data['Pump cooling [kW]']*0.3, label='Kühlpumpe')
# #ax.plot(x, data['pump energy total [%]'], label='total')
# ax.set_xlabel('Relative Leistung [%]')
# ax.set_ylabel('Leistungsverlust im System [%]')
# ax.set_title('Leistungsverluste der Pumpen')
# plt.grid(True)
# ax.legend()
#
# #eta curve system
# x = data['relative power [%]']
# y1 = data['energy consumption [kWh/m3]']
# y2 = data['eta_lhv']*100
# fig, ax1 = plt.subplots()
# ax2 = ax1.twinx()
# ax1.plot(x, y1, label='spez. Energieverbrauch')
# ax2.plot(x, y2, label='Wirkungsgrad',linestyle='--',color='b')
# ax1.set_xlabel('Relative Leistung [%]')
# ax1.set_ylabel('spezifischer Energieverbrauch [kWh/Nm3]')
# ax1.legend(loc='upper left')
# # Achsen und Titelbeschriftung für ax2
# ax2.set_ylabel('Wirkungsgrad [%]')
# ax2.tick_params(axis='y')
# ax2.legend(loc='upper right')
# ax1.grid(True)
#
# #masslow
# # fig, ax = plt.subplots()
# # ax.plot(data['mass_flow H2O cooling [kg]'], data['mass_flow H2O [kg]'], 'bo-', linewidth=2)
# # ax.set_xlabel('Relative Leistung [%]', fontsize=12)
# # ax.set_ylabel('massflow kg/h', fontsize=12)
# # ax.set_title('massflow', fontsize=16)
# # plt.grid(True)
#
#
# #specific energy consumption
# fig, ax = plt.subplots()
# ax.plot(data['relative power [%]'], data['energy consumption [kWh/m3]'], 'bo-', linewidth=2)
# ax.set_xlabel('Relative Leistung [%]', fontsize=12)
# ax.set_ylabel('spezifische Energie', fontsize=12)
# ax.set_title('Wirkungsgradkurve', fontsize=16)
# plt.grid(True)
# # Daten
# x = data['relative power [%]']
# y1 = data['eta PE [%]']
# y2 = data['drying [%]']
# y3 = data['pump energy total [%]']
# y4 = data['Power heat fresh water [%]']
#
# # Figure und Achsen erstellen
# fig, ax1 = plt.subplots()
# ax2 = ax1.twinx()  # zweite y-Achse
#
# # Farben definieren
# color1 = 'tab:blue'
# color2 = 'tab:orange'
# color3 = 'tab:green'
# color4 = 'tab:red'
#
# # Stacked plot für ax1
# ax1.fill_between(x, y1, color=color1, alpha=0.5, label='Leistungselektronik')
# ax1.fill_between(x, y1, y1+y2, color=color2, alpha=0.5, label='Gastrocknung')
# ax1.fill_between(x, y1+y2, y1+y2+y3, color=color3, alpha=0.5, label='Pumpen')
# ax1.fill_between(x, y1+y2+y3, y1+y2+y3+y4, color=color4, alpha=0.5, label='Heizlast')
#
# # Linie für ax2
# y5 = data['eta PE [%]']
# y6 = data['drying [%]']
# y7 = data['pump energy total [%]']
# y8 = data['Power heat fresh water [%]']
# ax2.plot(x, y5, linestyle='--', color=color1, label='Leistungselektronik')
# ax2.plot(x, y6, linestyle='--', color=color2, label='Gastrocknung')
# ax2.plot(x, y7, linestyle='--', color=color3, label='Pumpen')
# ax2.plot(x, y8, linestyle='--', color=color4, label='Heizlast')
# ax2.set_ylabel('absoluter Leistungsverlust [kW]', color='k')
# ax2.tick_params(axis='y', labelcolor='k')
# # Achsen und Titelbeschriftung für ax1
# ax1.set_xlabel('Relative Leistung [%]')
# ax1.set_ylabel('relativer Leistungsverlust im System [%]')
# ax1.set_title('Energieintensive Komponenten im System')
# ax1.legend(loc='upper left')
# # Gitter anzeigen
# ax1.grid(True)
#
#
# # #energy losses
# # fig, ax = plt.subplots()
# # # Daten
# # x = data['relative power [%]']
# # y1 = data['eta PE [%]']
# # y2 = data['drying [%]']
# # y3 = data['pump energy total [%]']
# # y4 = data['Power heat fresh water [%]']
# # # Stacked plot
# # ax.fill_between(x, y1, label='Leistungselektronik')
# # ax.fill_between(x, y1, y1+y2, label='Gastrocknung')
# # ax.fill_between(x, y1+y2, y1+y2+y3, label='Pumpen')
# # ax.fill_between(x, y1+y2+y3, y1+y2+y3+y4, label='Heizlast')
# # # Achsen und Titelbeschriftung
# # ax.set_xlabel('Relative Leistung [%]')
# # ax.set_ylabel('relativer Leistungsverlust im System [%]')
# # ax.set_title('Energieintensive Komponenten im System')
# # ax.legend()
# # # Gitter anzeigen
# # plt.grid(True)
#
# # hydrogen, oxygen and heat output
# # Daten
# x = data['relative power [%]']
# y1 = data['mass_flow H2 [kg]']/ roh_H2
# y2 = data['mass_flow O2 [kg]']/1.429
# y3 = data['heat system [kW]']
#
# # Figure und Achsen erstellen
# fig, ax1 = plt.subplots()
# ax2 = ax1.twinx()  # zweite y-Achse
# # Linien für ax1
# ax1.plot(x, y1, label='H2 Massestrom', color='blue')
# ax1.plot(x, y2, label='O2 Massestrom', color='red')
# # Linie für ax2
# ax2.plot(x, y3, label='System Abwärme', linestyle='--',color='orange')
# # Achsen und Titelbeschriftung für ax1
# ax1.set_xlabel('Relative Leistung [%]')
# ax1.set_ylabel('Massestrom [Nm3/h]')
# ax1.legend(loc='upper left')
# # Achsen und Titelbeschriftung für ax2
# ax2.set_ylabel('Abwärme [kW]')
# ax2.tick_params(axis='y')
# # Gitter anzeigen
# handles1, labels1 = ax1.get_legend_handles_labels()
# handles2, labels2 = ax2.get_legend_handles_labels()
# handles = handles1 + handles2
# labels = labels1 + labels2
# # Gemeinsame Legende erstellen
# ax1.legend(handles, labels, loc='upper left')
# ax1.grid(True)
#
# plt.show()
#
#
# print('Leistungselektronik eta:', data['eta PE [%]'].iloc[-1])
# print('Gastrocknung eta:', data['drying [%]'].iloc[-1])
# print('Gastrocknung Verbrauch:', data['drying [kW]'].iloc[-1],'kW')
# print('Pumpen eta:', data['pump energy total [%]'].iloc[-1])
# print('Pumpen verbrauch:', data['pump energy total [kW]'].iloc[-1],'kW')
# print('Heizlast kW', data['Power heat fresh water [kW]'].iloc[2])
# print('Elektrolyse Wirkungsgrad:',data['eta_lhv electrolyze'].iloc[-1])
# print('Wirkugsgrad insgesamt:', data['eta_lhv'].iloc[-1])
# print('Wasserstoff in Nm3', data['mass_flow H2 [kg]'].iloc[-1]/roh_H2)
# print('Wasserstoff in kg', data['mass_flow H2 [kg]'].iloc[-1])
#
# # p_pump = data.loc[data.index[83], 'pump energy total [kW]']/data.loc[data.index[83], 'mass_flow H2 [kg]']
# # print(p_pump,'kW/kg')
# # print(data.loc[data.index[83], 'drying [kW]'])
# # print(data.loc[data.index[83], 'mass_flow H2 [kg]'])
# #print(data.loc[data.index[73], 'heat fresh water [%]'])
# #print(data.loc[data.index[73], 'heat loss [%]'])
#
# #print(data.loc[data.index[72] , 'mass_flow H2O cooling [kg]'])
# #print(data.loc[data.index[72] , 'mass_flow H2O [kg]'])
# #print(data.loc[data.index[70] , 'voltage'])
# #print(data.loc[data.index[70] , 'current'])
# # print(data.loc[data.index[83],'mass_flow H2O [kg]'])
#
#
# #heat stack
# fig, ax = plt.subplots()
# x = data['relative power [%]']
# ax.plot(x, data['heat [%]'], label='Stackabwärme')
# ax.set_xlabel('Relative Leistung [%]')
# ax.set_ylabel('Abwärme prozentual [%]')
# ax.set_title('Stackabwärme')
# plt.grid(True)
# ax.legend()
plt.show()