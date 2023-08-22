from modell.electrolyzer_modell import Electrolyzer
import matplotlib.pyplot as plt
import pandas as pd

T=50
elec = Electrolyzer(60, 2500, T, dt=1)

r = elec.create_polarization()
print(r)
r['current_A'] = r['current_A']/2500
#r = r.drop(r.index[:-500])
#print(r)
#print(elec.stack_nominal())

# #garcia et all
# garcia = pd.read_csv('polarization/garcia_et_all.csv', sep=';',decimal=',',header=0)
#
# #fz juelicj tjarks et all
# tjarks = pd.read_csv('polarization/tjarks_fzj.csv', sep=';',decimal=',',header=0)
#
# #fz Juelich
# fzj = pd.read_csv('polarization/fzjuelich.csv', sep=';',decimal=',',header=0)
#
# #ayer et all 2016
# ayers = pd.read_csv('polarization/ayers_et_all.csv', sep=';',decimal=',',header=0)

fig, ax = plt.subplots()

# Plotting the data
#ax.plot(tjarks['x'], tjarks['y'], label='Tjarks 2017')
#ax.plot(fzj['x'], fzj['y'], label='FZ Jülich 2022')
#ax.plot(ayers['x'], ayers['y'], label='Ayers et al.')
#ax.plot(garcia['x'], garcia['y'], label='Garcia et al 2011')
ax.plot(r['current_A'], r['voltage_U'], label='Simuliert')

# Adding the legend, x and y labels, and the title
ax.legend()
ax.set_xlabel('Strom [A/cm2]')
ax.set_ylabel('Spannung [V]')
ax.set_title('Vergleich der Polarisationskurven')
ax.grid(True)
plt.show()