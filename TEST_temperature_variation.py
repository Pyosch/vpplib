# -*- coding: utf-8 -*-
"""
Created on Tue May 12 08:42:44 2020

@author: andre
hier wird mal getestet, wie es sich auswirkt, wenn die Temperaturen immer
auf -15 bzw. 20 °C gesetzt werden. Hierzu wird (siehe user_profile)
dwd_temp_days_2015 angepasst.
Der Fehler bisher war, dass wir gar keine schöne Temperaturachse (mit linear
aufsteigenden Werten) hatten, sondern nur die geordneten Temperaturwerte über
das gesamte Jahr. So gab es bestimmte Temperaturen öfter, die öfter als nur
einmal vorkamen => Zitterlinie
Hier soll eine schöne Linie der Heizlast entstehen
"""

import pandas as pd

mean_temp_days = pd.read_csv("input/thermal/dwd_temp_days_2015.csv",
                             index_col="time")
mean_temp_days.index = pd.to_datetime(mean_temp_days.index)

print(str(mean_temp_days))

i = 0
start = -20
while i < len(mean_temp_days):
    mean_temp_days['temperature'].iat[i] = start
    start = start + i * (30 + 20) / 365
    i += 1

print(str(mean_temp_days))

SigLinDe = pd.read_csv("./input/thermal/SigLinDe.csv", decimal=",")

building_type = "DE_HEF33"

for i, Sig in SigLinDe.iterrows():
    if Sig.Type == building_type:             
        building_parameters=(Sig.A, Sig.B, Sig.C, Sig.D, Sig.m_H, Sig.b_H, Sig.m_W,
                     Sig.b_W)
        
A, B, C, D, m_H, b_H, m_W, b_W = building_parameters

 # Calculating the daily heat demand h_del for each day of the year
h_lst = []
t_0 = 40

#for i, temp in mean_temp_days.iterrows():
temperature = []
start = -20
end = 30
for i in range(999):
    value = start + (end - start) / 1000 * i
    temperature.append(value)
    
print(str(temperature))
    
for i in range(999):
    # H and W are for linearisation in SigLinDe function below 8°C
    H = m_H * temperature[i] + b_H
    W = m_W * temperature[i] + b_W
    if H > W:
        h_del = ((A/(1+((B/(temperature[i] - t_0))**C))) + D) + H
        h_lst.append(h_del)

    else:
        h_del = ((A/(1+((B/(temperature[i] - t_0))**C))) + D) + W
        h_lst.append(h_del)

h_del = pd.DataFrame(h_lst, columns = ["h_del"])

print(str(h_del))
