import pandas as pd
import matplotlib.pyplot as plt

elogen_data = pd.read_csv('efficiency_curves/elogen_powercurve_data.csv', sep=';', decimal=',', header=0)
htec = pd.read_csv('efficiency_curves/HTec_powercurve_data.csv', sep=';', decimal=',', header=0)
htec = htec.rename(columns={'Energieverbrauch [kWh/Nm3]' : 'htec'})

my_data = pd.read_csv('../modell/power_curve.csv',sep=',',decimal='.',header=0)

fig, ax = plt.subplots()

# Plotte df1 als Linie in Blau
ax.plot(elogen_data['relative Leistung [%]'], elogen_data['Energieverbrauch [kWh/Nm3]'], label='Elogen', color='blue')

# Plotte df2 als Linie in Rot
ax.plot(htec['relative Leistung [%]'], htec['htec'], label='HTEC', color='red')

# Plotte df3 als Scatter in Grün
ax.scatter(my_data['relative power [%]'], my_data['energy consumption [kWh/m3]'], label='modellierter Elektrolyseur', color='green')

# Titel und Achsenbeschriftung
ax.set_title('Vergleich der Betriebskurven')
ax.set_xlabel('relative Leistung [%]')
ax.set_ylabel('spez. Energieverbrauch [kWh/Nm3]')
ax.set_ylim([3.8, 5.6])
plt.grid(True)

ax.legend()
plt.show()