# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 14:59:32 2021

@author: ageil
"""


import pandas as pd
import pandapower as pp
import pandapower.networks as pn
import pandapower.plotting as pp_plot
import tkinter as tk
from tkinter import Tk
from tkinter import ttk
from tkinter import filedialog
import tkcalendar as tkc
from datetime import datetime
from PIL import ImageTk, Image
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from vpplib.environment import Environment
from vpplib.user_profile import UserProfile
from vpplib.photovoltaic import Photovoltaic
from vpplib.battery_electric_vehicle import BatteryElectricVehicle
from vpplib.heat_pump import HeatPump
from vpplib.electrical_energy_storage import ElectricalEnergyStorage
from vpplib.wind_power import WindPower
from vpplib.virtual_power_plant import VirtualPowerPlant
from vpplib.operator import Operator


# GUI
WIDTH = 1000
HEIGHT = 500


root = tk.Tk()  # Erstellen des Hauptfensters
root.title('VPPlib')  # Benennung der Kopfzeile
# Hinzufügen eines Icon in der Kopfzeile
root.iconbitmap('./input/graphics/power-plant.ico')


# Erstellunf der Resgisterkarten (Notebooks)
Registerkarten = ttk.Notebook(root)
Registerkarten.pack()  # Resgisterkarten auf das Hauptfenster packen

'Ertellung der verschiedenen Registerkarten.'
Grundeinstellungen_Frame = tk.Frame(Registerkarten, width=WIDTH, height=HEIGHT)
Environment_Frame = tk.Frame(Registerkarten, width=WIDTH, height=HEIGHT)
User_Frame = tk.Frame(Registerkarten, width=WIDTH, height=HEIGHT)
BEV_Frame = tk.Frame(Registerkarten, width=WIDTH, height=HEIGHT)
PV_Frame = tk.Frame(Registerkarten, width=WIDTH, height=HEIGHT)
heat_pump_Frame = tk.Frame(Registerkarten, width=WIDTH, height=HEIGHT)
storage_Frame = tk.Frame(Registerkarten, width=WIDTH, height=HEIGHT)
Wind_Frame = tk.Frame(Registerkarten, width=WIDTH, height=HEIGHT)
Ergebnis_Frame = tk.Frame(Registerkarten, width=WIDTH, height=HEIGHT)

Grundeinstellungen_Frame.pack()
Environment_Frame.pack()
User_Frame.pack()
BEV_Frame.pack()
PV_Frame.pack()
Wind_Frame.pack()
storage_Frame.pack()
heat_pump_Frame.pack()
Ergebnis_Frame.pack()

Registerkarten.add(Grundeinstellungen_Frame, text="Grundeinstellungen ")
Registerkarten.add(Environment_Frame, text="Environment ")
Registerkarten.add(User_Frame, text="User Profil ")
Registerkarten.add(BEV_Frame, text="BEV         ")
Registerkarten.add(PV_Frame, text="PV           ")
Registerkarten.add(Wind_Frame, text="Wind        ")
Registerkarten.add(heat_pump_Frame, text="Wärmepumpe        ")
Registerkarten.add(storage_Frame, text="Speicher    ")
Registerkarten.add(Ergebnis_Frame, text="Ergebnis    ")

"""
In der Funktion simulieren werden die Parameter aus den Registerkarten ausgelesen und dem Szenario zur Verfügungf gestellt.
Weiterhin wird dasv Szenario ausgeführt. In diesem Fall ist das base scenario implementiert. Eine auswahl verschiedener Szenarien ist nochnicht möglich.
Zudem werden die Ergebnisse der Simulation aus dem Operatior übergeben und für die Visualisierung vorbereitet.

"""


def simulieren():
    global vpp_key
    global result_key
    global results
    global vpp
    global key
    global temp_hours_file
    global temp_days_file
    global net
    global ppnet_dict
    global button_dict
    global button_dict_2
    global dd_date
    global sld_line_max
    global sld_line_min
    global sld_trafo_max
    global sld_trafo_min
    global sld_bus_max
    global sld_bus_min

    'Die folgenden Zeilen dienen dem Übergeben der variablen aus den Eingabefeldern in den Registerkarten.'
    # environment
    timezone = ent_timezone.get()
    year = ent_year.get()
    time_freq = ent_time_freq.get()
    timebase = int(ent_timebase.get())
    index = pd.date_range(start=start, end=end, freq=time_freq)

    # user_profile
    identifier = ent_identifier.get()
    latitude = float(ent_latitude.get())
    longitude = float(ent_longitude.get())
    yearly_thermal_energy_demand = float(
        ent_yearly_thermal_energy_demand.get())
    comfort_factor = ent_comfort_factor.get()
    daily_vehicle_usage = ent_daily_vehicle_usage.get()
    building_type = ent_building_type.get()
    t_0 = int(ent_t_0.get())

    week_trip_start = []
    week_trip_end = []
    weekend_trip_start = []
    weekend_trip_end = []
    global baseload_file
    baseload = pd.read_csv(baseload_file)
    baseload.drop(columns=["Time"], inplace=True)
    baseload.index = pd.date_range(
        start=year, periods=35040, freq=time_freq, name='time')

    unit = "kW"
    # WindTurbine data

    turbine_type = ent_turbine_type.get()
    hub_height = int(ent_hub_height.get())
    rotor_diameter = int(ent_rotor_diameter.get())
    fetch_curve = ent_fetch_curve.get()
    data_source = ent_data_source.get()

    # WindPower ModelChain data

    global wind_file

    wind_speed_model = ent_wind_speed_model.get()
    density_model = ent_density_model.get()
    temperature_model = ent_temperature_model.get()
    power_output_model = ent_power_output_model.get()
    density_correction = bool(ent_density_correction.get())
    obstacle_height = int(ent_obstacle_height.get())
    hellman_exp = ent_hellman_exp.get()

    # PV data
    global pv_file

    module_lib = ent_module_lib.get()
    module = ent_module.get()
    inverter_lib = ent_inverter_lib.get()
    inverter = ent_inverter.get()
    surface_tilt = int(ent_surface_tilt.get())
    surface_azimuth = int(ent_surface_azimuth.get())
    modules_per_string = int(ent_modules_per_string.get())
    strings_per_inverter = int(ent_strings_per_inverter.get())

    # BEV data
    battery_max = int(ent_battery_max.get())
    battery_min = int(ent_battery_min.get())
    battery_usage = int(ent_battery_usage.get())
    charging_power = int(ent_charging_power.get())
    charge_efficiency_bev = float(ent_charge_efficiency_bev.get())

    # heat pump data
    heatpump_type = ent_heatpump_type.get()
    heat_sys_temp = int(ent_heat_sys_temp.get())
    el_power = int(ent_el_power.get())

    # storage
    charge_efficiency_storage = float(ent_charge_efficiency_storage.get())
    discharge_efficiency_storage = float(
        ent_discharge_efficiency_storage.get())
    max_power = int(ent_max_power.get())
    capacity = int(ent_capacity.get())
    max_c = int(ent_max_c.get())

    # define the amount of components in the grid
    # NOT VALID for all component distribution methods (see line 131-143)

    pv_percentage = int(ent_pv_percentage.get())
    storage_percentage = int(ent_storage_percentage.get())
    bev_percentage = int(ent_bev_percentage.get())
    hp_percentage = int(ent_hp_percentage.get())
    wind_percentage = int(ent_wind_percentage.get())

    # %% environment
    'Ab hier beginnt das base scenario, welches als Teil der VPPlib zu sehen ist und dieser Arbeit als Beispiel dient.'

    """
    Created on Tue Jul  2 10:38:17 2019

    @author: Sascha Birk
    """
    environment = Environment(timebase=timebase, timezone=timezone,
                              start=start, end=end, year=year,
                              time_freq=time_freq)

    environment.get_wind_data(file=wind_file, utc=False)
    environment.get_pv_data(file=pv_file)
    environment.get_mean_temp_days(file=temp_days_file)
    environment.get_mean_temp_hours(file=temp_hours_file)

    # %% user profile

    user_profile = UserProfile(identifier=identifier,
                               latitude=latitude,
                               longitude=longitude,
                               thermal_energy_demand_yearly=yearly_thermal_energy_demand,
                               building_type=building_type,
                               comfort_factor=comfort_factor,
                               t_0=t_0,
                               daily_vehicle_usage=daily_vehicle_usage,
                               week_trip_start=week_trip_start,
                               week_trip_end=week_trip_end,
                               weekend_trip_start=weekend_trip_start,
                               weekend_trip_end=weekend_trip_end)

    user_profile.get_thermal_energy_demand()

    # %% create instance of VirtualPowerPlant and the designated grid
    vpp = VirtualPowerPlant("Master")

    net = pn.panda_four_load_branch()

    # %% assign names and types to baseloads for later p and q assignment
    for bus in net.bus.index:

        net.load.name[net.load.bus == bus] = net.bus.name[bus]+'_baseload'
        net.load.type[net.load.bus == bus] = 'baseload'

    # %% assign components to random bus names

    def test_get_buses_with_components(vpp):
        vpp.get_buses_with_components(net, method='random',
                                      pv_percentage=pv_percentage,
                                      hp_percentage=hp_percentage,
                                      bev_percentage=bev_percentage,
                                      wind_percentage=wind_percentage,
                                      storage_percentage=storage_percentage)

    # %% assign components to the bus names for testing purposes

    def test_get_assigned_buses_with_components(vpp,
                                                buses_with_pv,
                                                buses_with_hp,
                                                buses_with_bev,
                                                buses_with_storage,
                                                buses_with_wind):

        vpp.buses_with_pv = buses_with_pv

        vpp.buses_with_hp = buses_with_hp

        vpp.buses_with_bev = buses_with_bev

        vpp.buses_with_wind = buses_with_wind

        # storages should only be assigned to buses with pv
        vpp.buses_with_storage = buses_with_storage

    # %% assign components to the loadbuses

    def test_get_loadbuses_with_components(vpp):

        vpp.get_buses_with_components(net, method='random_loadbus',
                                      pv_percentage=pv_percentage,
                                      hp_percentage=hp_percentage,
                                      bev_percentage=bev_percentage,
                                      wind_percentage=wind_percentage,
                                      storage_percentage=storage_percentage)

    # %% Choose assignment methode for component distribution

    # test_get_buses_with_components(vpp)

    test_get_assigned_buses_with_components(vpp,
                                            buses_with_pv=[
                                                'bus3', 'bus4', 'bus5', 'bus6'],
                                            buses_with_hp=['bus4'],
                                            buses_with_bev=['bus5'],
                                            buses_with_storage=['bus5'],
                                            buses_with_wind=['bus1'])

    # test_get_loadbuses_with_components(vpp)

    # %% create components and assign components to the Virtual Powerplant

    for bus in vpp.buses_with_pv:

        vpp.add_component(Photovoltaic(unit=unit, identifier=(bus + '_PV'),
                                       environment=environment,
                                       user_profile=user_profile,
                                       module_lib=module_lib,
                                       module=module,
                                       inverter_lib=inverter_lib,
                                       inverter=inverter,
                                       surface_tilt=surface_tilt,
                                       surface_azimuth=surface_azimuth,
                                       modules_per_string=modules_per_string,
                                       strings_per_inverter=strings_per_inverter))

        vpp.components[list(vpp.components.keys())[-1]].prepare_time_series()

    for bus in vpp.buses_with_storage:

        vpp.add_component(ElectricalEnergyStorage(unit=unit,
                                                  identifier=(bus+'_storage'),
                                                  environment=environment,
                                                  user_profile=user_profile,
                                                  capacity=capacity,
                                                  charge_efficiency=charge_efficiency_storage,
                                                  discharge_efficiency=discharge_efficiency_storage,
                                                  max_power=max_power, max_c=max_c))

        vpp.components[
            list(vpp.components.keys())[-1]].timeseries = pd.DataFrame(
                columns=['state_of_charge', 'residual_load'],
            index=pd.date_range(start=start, end=end, freq=time_freq))

    for bus in vpp.buses_with_bev:

        vpp.add_component(BatteryElectricVehicle(unit=unit, identifier=(bus + '_BEV'),
                                                 environment=environment, user_profile=user_profile,
                                                 battery_max=battery_max, battery_min=battery_min,
                                                 battery_usage=battery_usage,
                                                 load_degradation_begin=0.8,
                                                 charging_power=charging_power,
                                                 charge_efficiency=charge_efficiency_bev))

        vpp.components[list(vpp.components.keys())[-1]].prepare_time_series()

    for bus in vpp.buses_with_hp:

        vpp.add_component(HeatPump(unit=unit, identifier=(bus + '_HP'),
                                   environment=environment,
                                   user_profile=user_profile,
                                   heat_pump_type=heatpump_type,
                                   heat_sys_temp=heat_sys_temp,
                                   el_power=el_power))

        vpp.components[list(vpp.components.keys())[-1]].prepare_time_series()

    for bus in vpp.buses_with_wind:

        vpp.add_component(WindPower(unit=unit, identifier=(bus + '_Wind'),
                                    environment=environment, user_profile=user_profile,
                                    turbine_type=turbine_type, hub_height=hub_height,
                                    rotor_diameter=rotor_diameter, fetch_curve=fetch_curve,
                                    data_source=data_source,
                                    wind_speed_model=wind_speed_model,
                                    density_model=density_model,
                                    temperature_model=temperature_model,
                                    power_output_model=power_output_model,
                                    density_correction=density_correction,
                                    obstacle_height=obstacle_height,
                                    hellman_exp=hellman_exp))

        vpp.components[list(vpp.components.keys())[-1]].prepare_time_series()

    # %% create elements in the pandapower.net

    for bus in vpp.buses_with_pv:

        pp.create_sgen(net, bus=net.bus[net.bus.name == bus].index[0],
                       p_mw=(vpp.components[bus+'_PV'].module.Impo *
                             vpp.components[bus+'_PV'].module.Vmpo/1000000),
                       name=(bus+'_PV'), type='PV')

    for bus in vpp.buses_with_storage:

        pp.create_storage(net, bus=net.bus[net.bus.name == bus].index[0],
                          p_mw=0, max_e_mwh=capacity, name=(bus+'_storage'), type='LiIon')

    for bus in vpp.buses_with_bev:

        pp.create_load(net, bus=net.bus[net.bus.name == bus].index[0],
                       p_mw=(vpp.components[bus+'_BEV'].charging_power/1000), name=(bus+'_BEV'), type='BEV')

    for bus in vpp.buses_with_hp:

        pp.create_load(net, bus=net.bus[net.bus.name == bus].index[0],
                       p_mw=(vpp.components[bus+'_HP'].el_power/1000), name=(bus+'_HP'), type='HP')

    for bus in vpp.buses_with_wind:

        pp.create_sgen(net, bus=net.bus[net.bus.name == bus].index[0],
                       p_mw=(
                           vpp.components[bus+'_Wind'].wind_turbine.nominal_power/1000000),
                       name=(bus+'_Wind'), type='WindPower')

    # %% initialize operator

    operator = Operator(virtual_power_plant=vpp, net=net, target_data=None)

    # %% run base_scenario without operation strategies

    net_dict, ppnet_dict = operator.run_base_scenario(baseload)

    # %% extract results from powerflow

    results = operator.extract_results(net_dict)
    single_result = operator.extract_single_result(
        net_dict, res='ext_grid', value='p_mw')

    'Hier endet das base scenario.'

    """
    Created on Wed Feb 17 14:59:32 2021

    @author: ageil
    """

    Registerkarten.select(8)  # Wechsel in zu Ergebnisregisterkarte

    vpp_key = vpp.components.keys()  # Erstellen einer Liste mit den Komponenten
    result_key = results.keys()  # Erstellen einer Liste mit den Netz-Elementen

    # Erstellen eines Dictionary, in dem jeder Komponente eine tkinter Variable zugewiesen wird.
    button_dict = {key: tk.IntVar() for key in vpp_key}
    # Erstellen eines Dictionary, in dem jedem Netzelement eine tkinter Variable zugewiesen wird.
    button_dict_2 = {key: tk.IntVar() for key in results.keys()}

    x = 0  # definieren einer Zählvariable

    for key in vpp_key:  # Erstellen einen Checkbuttons für jede Komponente
        var = key  # Benennen einer Variable nach der Komponente
        # Erstellen der Checkbox und zuweisen der Variable aus dem zuvor ertselltem Dictionary.
        var = tk.Checkbutton(loadprofiles, text=str(
            key), variable=button_dict[key], onvalue=1, offvalue=0)
        # Platzieren der Checkbox über ein Gridsystem in einem Frame
        var.grid(row=x, column=0, sticky=tk.W)
        x = x+1  # Hochzählen der Zählvariable

    for key in result_key:  # Erstellen einen Checkbuttons für jedes Netz-Element
        var = key  # Benennen einer Variable nach der Komponente
        # Erstellen der Checkbox und zuweisen der Variable aus dem zuvor ertselltem Dictionary.
        var = tk.Checkbutton(loadprofiles, text=str(
            key), variable=button_dict_2[key], onvalue=1, offvalue=0)
        # Platzieren der Checkbox über ein Gridsystem in einem Frame
        var.grid(row=x, column=0, sticky=tk.W)
        x = x+1  # Hochzählen der Zählvariable

    liste = []  # Erstellen einer leeren Liste
    for key in ppnet_dict:
        # Füllen der Liste mit den Zeitstempeln aus der pandapower-Netzsimulation
        liste.append(pd.to_datetime(key))

    # Aktivieren der Button, Schieberegler und der Combobox auf der Registerkarte Ergebnis

    dd_date.configure(value=liste, state='normal')
    sld_line_max.configure(state='normal')
    sld_line_min.configure(state='normal')
    sld_trafo_max.configure(state='normal')
    sld_trafo_min.configure(state='normal')
    sld_bus_max.configure(state='normal')
    sld_bus_min.configure(state='normal')
    btn_net.configure(state='normal')
    btn_load.configure(state='normal')
    btn_save.configure(state='normal')


Graph_number = 1  # Definieren einer Zählvariable für dass Hinzufügen von Registerkarten
"""
Die Funktion graph wird über den  Button Lastprofil aufgerufen und zeigt die Datensätze, die zuvor auf der Registerkarte Ergebnis mit einem Haken
in der Ckeckbox ausgewählt wurden. Für das Diagramm wird eine neue Registerkarte erstellt und Fortlaufed benannt.
"""


def graph():
    # Zählvariable wwir auch für die net_show Funktion verwendet und muss über die Funktion hinaus verfügbar sein.
    global Graph_number

    # Erstellen eines neuen Frames, dem das Diagramm zugeordnet wird.
    Grafik_Frame = tk.Frame(Registerkarten, width=1000, height=500)
    Grafik_Frame.pack()

    # Erstellen einer neuen Registerkarte
    Registerkarten.add(Grafik_Frame, text="Grafik "+str(Graph_number))
    Registerkarten.select(8+Graph_number)

    fig = Figure()  # Definieren der matplotlib-Grafil

    # Diese For-Schleife überprüft, welche Checkboxen für die Komponenten aktiviert wurden.
    for key in vpp_key:
        if button_dict[key].get() == 1:
            Rohdaten = pd.DataFrame(vpp.components[key].timeseries)
            for col_name in Rohdaten.columns:  # Diese For-Schleife fügt den ausgewählten Datensatz als Graph dem Diagramm hinzu
                fig.add_subplot().plot(
                    Rohdaten.index, Rohdaten[col_name], linewidth=1.5, label=col_name)

    # Diese For-Schleife überprüft, welche Checkboxen für die Netz-Elemente aktiviert wurden.
    for key in result_key:
        if button_dict_2[key].get() == 1:
            Rohdaten_2 = pd.DataFrame(results[key])
            # Diese For-Schleife fügt den ausgewählten Datensatz als Graph dem Diagramm hinzu
            for col_name in Rohdaten_2.columns:
                fig.add_subplot().plot(Rohdaten_2.index,
                                       Rohdaten_2[col_name], linewidth=1.5, label=col_name)

    # Setzen der Achsenbeschriftung
    fig.add_subplot().set_ylabel('Lesitung [MW]/Belastung [%]')
    fig.add_subplot().grid()  # Hinzufügen der Gitternetzlinien
    fig.add_subplot().legend()  # Hinzufügen einer Legende

    # matplotlib-Grafik in den Frame einbetten
    canvas = FigureCanvasTkAgg(fig, Grafik_Frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # matplotlib-toolbar hinzufügen
    toolbar = NavigationToolbar2Tk(canvas, Grafik_Frame)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def delete():  # Diese Funktion ermöglicht das Löschen einer Registerkarte
        global Graph_number
        # Löschen der ausgewählten Registerkarte
        Registerkarten.forget(Registerkarten.select())
        # Runterzählen der der Zählvariable für die Registerkarten
        Graph_number = Graph_number-1

    # Hinzufügen des Buttens, der die delete-Funktion aufruft
    btn_quit_graph = tk.Button(Grafik_Frame, text="Löschen", command=delete)
    btn_quit_graph.place(relx=0.6, rely=0.885, relwidth=0.1,
                         relheight=0.051, anchor='nw')

    Graph_number = Graph_number+1  # Hochzählen der Zählvariable


"""
Die net_show-Funktion ermöglicht es für einen bestimmten Zeitpunkt der Simulation ein Netz anzuzeigen. Die Farbe der Leitungen, Knoten und
Transformatoren ändert sich mit der Belastung von grün zu rot. Bei der Knotenspannung wird Unterspannung blau und Überspannung rot dargegstellt.
Die Grenzen lassen sich über Schieberegler einstellen.
"""


def net_show():
    global Graph_number

    # Erstellen eines neuen Frames, die Netzdarstellung zugeordnet wird.
    Grafik_Frame = tk.Frame(Registerkarten, width=1000, height=400)
    Grafik_Frame.pack()

    # Erstellen einer neuen Registerkarte
    Registerkarten.add(Grafik_Frame, text="Netz "+str(Graph_number))
    Registerkarten.select(8+Graph_number)

    # Definieren einer Variable für die maximale Leitungsbelastung
    line_max = sld_line_max.get()
    # Definieren einer Variable für die minimale Leitungsbelastung
    line_min = sld_line_min.get()
    # Definieren einer Variable für die maximale Trafobelastung
    trafo_max = sld_trafo_max.get()
    # Definieren einer Variable für die minimale Trafobelastung
    trafo_min = sld_trafo_min.get()
    # Definieren einer Variable für die maximale Knotenspannung
    bus_max = sld_bus_max.get()
    # Definieren einer Variable für die minimale Knotenspannung
    bus_min = sld_bus_min.get()

    # Definieren einer Varaible, welche die Ergebnisse der Netzsimulation enthält
    net = ppnet_dict[pd.to_datetime(dd_date.get())]

    # Definieren der Farbverteilung für die Leitungsbelastung
    cmap_list_line = [(line_min, "green"),
                      ((line_max-line_min)/2, "yellow"), (line_max, "red")]
    cmap, norm = pp_plot.cmap_continuous(cmap_list_line)
    # Erstellen einer collection mit den für die Leitungsbelastung
    lc = pp_plot.create_line_collection(
        net, net.line.index, zorder=2, cmap=cmap, norm=norm, linewidths=2)

    # Definieren der Farbverteilung für die Knotenspannung
    cmap_list_bus = [((bus_min/100), "blue"),
                     (1, "green"), ((bus_max/100), "red")]
    cmap, norm = pp_plot.cmap_continuous(cmap_list_bus)
    # Erstellen einer collection mit den für die Knotenspannung
    bc = pp_plot.create_bus_collection(
        net, net.bus.index, size=0.05, zorder=2, cmap=cmap, norm=norm)

    # Definieren der Farbverteilung für die Trafobelastung
    cmap_list_traf = [(trafo_min, "green"),
                      ((trafo_max-trafo_min)/2, "yellow"), (trafo_max, "red")]
    cmap, norm = pp_plot.cmap_continuous(cmap_list_traf)
    # Erstellen einer collection mit den für die Trafobelastung
    tc = pp_plot.create_trafo_collection(
        net, size=0.1, zorder=2, cmap=cmap, norm=norm,  linewidths=2)

    # erstellen eines matplotlib-Diagramms
    fig = plt.figure(facecolor="white", figsize=(8, 6))

    plt.subplots_adjust(left=0.01, right=0.99, top=0.95,
                        bottom=0.05, wspace=0.02, hspace=0.04)
    ax = plt.gca()
    # Hinzufügen der collections zum pandapower-plot
    pp_plot.collections.add_collections_to_axes(
        ax, [lc, bc, tc], plot_colorbars=True, copy_collections=True)
    ax.axis("off")
    ax.set_aspect('equal', 'datalim')
    ax.autoscale_view(True, True, True)
    ax.margins(.02)

    # Einebetten des Diagramms in den Frame
    canvas = FigureCanvasTkAgg(fig, Grafik_Frame)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    canvas.draw()

    toolbar = NavigationToolbar2Tk(
        canvas, Grafik_Frame)  # hinzufügen einer Toolbar
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def delete():  # Diese Funktion ermöglicht das Löschen einer Registerkarte
        global Graph_number
        # Löschen der ausgewählten Registerkarte
        Registerkarten.forget(Registerkarten.select())
        # Runterzählen der der Zählvariable für die Registerkarten
        Graph_number = Graph_number-1

    # Hinzufügen des Buttens, der die delete-Funktion aufruft
    btn_quit_graph = tk.Button(Grafik_Frame, text="Löschen", command=delete)
    btn_quit_graph.place(relx=0.6, rely=0.885, relwidth=0.1,
                         relheight=0.051, anchor='nw')

    Graph_number = Graph_number+1  # Hochzählen der Zählvariable


"""
Die Program_Exit-Funktion beendet das Programm
"""


def Program_Exit():
    root.quit()
    root.destroy()


"""
Die csv_export-Funktion ermöglich das Exportieren der Simulationsergebnisse der Komponenten
"""


def csv_export():
    CSV = pd.DataFrame()
    for key in vpp_key:
        key = pd.DataFrame(vpp.components[key].timeseries)
        df = key
        liste = []  # Erstellen einer leeren Liste
        for key in key:
            liste.append(key)
        for i in liste:
            print(i)
            CSV[i] = df[i]

    # Auswahl des Speicherortes, an dem die CSV-Datei abgelegt werden soll.
    file = filedialog.asksaveasfilename(title='CSV speichern')
    CSV.to_csv(path_or_buf=file)  # Umwan


"""
Die folgenden Zeilen fügen den einzelnen Registerkarten die entsprechneden Label, Button und Eiganbefelder hinzu.
Die einzelnen Registerkarten werden vorher angekündigt. LAbel, Button und Eingabefelder erklären sich durch ihre Variablenbezeichnung
und den Tesxt selbst.
"""
################################ Environment ####################################
#################################################################################

"""
Die Funktion date_Window öffnet ein Fenster mit einem Kalender. In diesm Kalender kann das Start- und End-Datum sowie die Zeit für
die Simulation ausgewählt werden.
"""


def date_window():

    def grab_start_date():  # Ändern des Startdatums
        global start
        start = str(datetime.strptime(cal.get_date()+' '+Stunden.get()+':'+Minuten.get(),
                                      '%m/%d/%y %H:%M'))  # Zusammensetzen des Strings für das Start-Datum

        lbl_Start = tk.Label(Environment_Frame, text='Start: ' +
                             start, anchor='nw')  # Ändern des Labels
        lbl_Start.place(relx=0.15, rely=0.05, relwidth=0.175,
                        relheight=0.05, anchor='nw')

    def grab_end_date():  # Ändern des Enddatums
        global end
        end = str(datetime.strptime(cal.get_date()+' '+Stunden.get()+':'+Minuten.get(),
                                    '%m/%d/%y %H:%M'))  # Zusammensetzen des Strings für das End-Datum

        lbl_Ende = tk.Label(Environment_Frame, text='Ende: ' +
                            end, anchor='nw')  # Ändern des Labels
        lbl_Ende.place(relx=0.15, rely=0.1, relwidth=0.175,
                       relheight=0.05, anchor='nw')

    top = tk.Toplevel()  # Erstellen des neuesn Fesnters
    top.geometry("250x300")
    # Erstellen eines Kalendder über die tkinter Kalender-Funktion
    cal = tkc.Calendar(top, selectmode="day", year=2020, month=1, day=1)
    cal.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.7, anchor='nw')
    top.title('Datum auswählen')
    tk.Label(top, text="Zeit:").place(relx=0.05, rely=0.8,
                                      relwidth=0.25, relheight=0.05, anchor='nw')

    default_wert_min = tk.StringVar()
    default_wert_min.set('00')

    default_wert_h = tk.StringVar()
    default_wert_h.set('00')

    tk.Label(top, text="h").place(relx=0.3, rely=0.8,
                                  relwidth=0.05, relheight=0.05, anchor='nw')

    Stunden = tk.Entry(top, textvariable=default_wert_h)
    Stunden.place(relx=0.35, rely=0.8, relwidth=0.1,
                  relheight=0.05, anchor='nw')

    tk.Label(top, text="m").place(relx=0.45, rely=0.8,
                                  relwidth=0.05, relheight=0.05, anchor='nw')

    Minuten = tk.Entry(top, textvariable=default_wert_min)
    Minuten.place(relx=0.5, rely=0.8, relwidth=0.1,
                  relheight=0.05, anchor='nw')

    tk.Button(top, text="Startdatum", command=grab_start_date).place(
        relx=0.05, rely=0.875, relwidth=0.267, relheight=0.1, anchor='nw')
    tk.Button(top, text="Enddatum", command=grab_end_date).place(
        relx=0.367, rely=0.875, relwidth=0.267, relheight=0.1, anchor='nw')
    tk.Button(top, text="OK", command=top.destroy).place(
        relx=0.684, rely=0.875, relwidth=0.267, relheight=0.1, anchor='nw')


start = '2015-03-01 00:00:00'
end = '2015-03-01 23:45:00'

lbl_Start = tk.Label(Environment_Frame, text="Start: "+start, anchor='nw')
lbl_Start.place(relx=0.15, rely=0.05, relwidth=0.175,
                relheight=0.05, anchor='nw')

lbl_Ende = tk.Label(Environment_Frame, text="Ende: "+end, anchor='nw')
lbl_Ende.place(relx=0.15, rely=0.1, relwidth=0.175,
               relheight=0.05, anchor='nw')

btn_date = tk.Button(Environment_Frame, text="Datum", command=date_window)
btn_date.place(relx=0.025, rely=0.05, relwidth=0.1,
               relheight=0.05, anchor='nw')


# Environment
# Zeitzone
default_wert = tk.StringVar()
default_wert.set('Europe/Berlin')

lbl_time_zone = tk.Label(Environment_Frame, text="Zeitzone", anchor='nw')
lbl_time_zone.place(relx=0.025, rely=0.15, relwidth=0.1,
                    relheight=0.05, anchor='nw')

ent_timezone = tk.Entry(Environment_Frame, textvariable=default_wert)
ent_timezone.place(relx=0.15, rely=0.15, relwidth=0.175,
                   relheight=0.05, anchor='nw')


# Environment
# Jahr
default_wert = tk.StringVar()
default_wert.set('2015')

lbl_time_zone = tk.Label(Environment_Frame, text="Jahr", anchor='nw')
lbl_time_zone.place(relx=0.025, rely=0.25, relwidth=0.1,
                    relheight=0.05, anchor='nw')

ent_year = tk.Entry(Environment_Frame, textvariable=default_wert)
ent_year.place(relx=0.15, rely=0.25, relwidth=0.175,
               relheight=0.05, anchor='nw')


# Environment
# time freq
default_wert = tk.StringVar()
default_wert.set('15 min')

lbl_time_freq = tk.Label(Environment_Frame, text="Zeitfrequenz", anchor='nw')
lbl_time_freq.place(relx=0.025, rely=0.35, relwidth=0.1,
                    relheight=0.05, anchor='nw')

ent_time_freq = tk.Entry(Environment_Frame, textvariable=default_wert)
ent_time_freq.place(relx=0.15, rely=0.35, relwidth=0.175,
                    relheight=0.05, anchor='nw')

time_freq = ent_time_freq.get()

default_wert = tk.IntVar()
default_wert.set(15)

lbl_time_freq = tk.Label(Environment_Frame, text="Zeitbasis", anchor='nw')
lbl_time_freq.place(relx=0.025, rely=0.45, relwidth=0.1,
                    relheight=0.05, anchor='nw')

ent_timebase = tk.Entry(Environment_Frame, textvariable=default_wert)
ent_timebase.place(relx=0.15, rely=0.45, relwidth=0.175,
                   relheight=0.05, anchor='nw')


# Environment
# weather data
"""
Funktionen für das Laden von Excel-Dateien
"""
temp_days_file = "./input/thermal/dwd_temp_days_2015.csv"


def temp_days_file_func():
    global temp_days_file

    temp_days_file = filedialog.askopenfilename(
        title="Select files", filetypes=(("csv files", "*.csv"), ("Excel", "*.xlsx")))

    lbl_temp_days_file = tk.Label(
        Environment_Frame, text=temp_days_file, anchor='nw')
    lbl_temp_days_file.place(relx=0.15, rely=0.55,
                             relwidth=0.85, relheight=0.05, anchor='nw')


btn_temp_days_file = tk.Button(
    Environment_Frame, text="Tagesdaten", command=temp_days_file_func)
btn_temp_days_file.place(relx=0.025, rely=0.55,
                         relwidth=0.1, relheight=0.05, anchor='nw')

lbl_temp_days_file = tk.Label(
    Environment_Frame, text=temp_days_file, anchor='nw')
lbl_temp_days_file.place(relx=0.15, rely=0.55, relwidth=0.85, relheight=0.05)

temp_hours_file = "./input/thermal/dwd_temp_hours_2015.csv"


def temp_hours_file_func():
    global temp_hours_file

    temp_hours_file = filedialog.askopenfilename(
        title="Select files", filetypes=(("csv files", "*.csv"), ("Excel", "*.xlsx")))

    lbl_temp_hours_file = tk.Label(
        Environment_Frame, text=temp_days_file, anchor='nw')
    lbl_temp_hours_file.place(relx=0.15, rely=0.65,
                              relwidth=0.85, relheight=0.05, anchor='nw')


btn_select_temp_hours_file = tk.Button(
    Environment_Frame, text="Stundendaten", command=temp_hours_file_func)
btn_select_temp_hours_file.place(
    relx=0.025, rely=0.65, relwidth=0.1, relheight=0.05, anchor='nw')

lbl_temp_hours_file = tk.Label(
    Environment_Frame, text=temp_hours_file, anchor='nw')
lbl_temp_hours_file.place(relx=0.15, rely=0.65, relwidth=0.65, relheight=0.05)


################################ User Profil ####################################
#################################################################################


# User Profil
# identifier

default_wert = tk.IntVar()
default_wert.set('bus 1')

lbl_identifier = tk.Label(User_Frame, text="identifier", anchor='nw')
lbl_identifier.place(relx=0.025, rely=0.05, relwidth=0.1,
                     relheight=0.05, anchor='nw')

ent_identifier = tk.Entry(User_Frame, textvariable=default_wert)
ent_identifier.place(relx=0.2, rely=0.05, relwidth=0.175,
                     relheight=0.05, anchor='nw')


# User Profil
#latitude and longitude

default_wert = tk.IntVar()
default_wert.set('50.941357')

lbl_latitude = tk.Label(User_Frame, text="latitude", anchor='nw')
lbl_latitude.place(relx=0.025, rely=0.15, relwidth=0.1,
                   relheight=0.05, anchor='nw')

ent_latitude = tk.Entry(User_Frame, textvariable=default_wert)
ent_latitude.place(relx=0.2, rely=0.15, relwidth=0.175,
                   relheight=0.05, anchor='nw')


default_wert = tk.IntVar()
default_wert.set('6.958307')

lbl_longitude = tk.Label(User_Frame, text="longitude", anchor='nw')
lbl_longitude.place(relx=0.4, rely=0.15, relwidth=0.1,
                    relheight=0.05, anchor='nw')

ent_longitude = tk.Entry(User_Frame, textvariable=default_wert)
ent_longitude.place(relx=0.5, rely=0.15, relwidth=0.175,
                    relheight=0.05, anchor='nw')


# User Profil
# yearly_thermal_energy_demand

default_wert = tk.IntVar()
default_wert.set(12500)

lbl_thermal_energy_demand = tk.Label(
    User_Frame, text="thermal energy demand", anchor='nw')
lbl_thermal_energy_demand.place(
    relx=0.025, rely=0.25, relwidth=0.2, relheight=0.05, anchor='nw')

ent_yearly_thermal_energy_demand = tk.Entry(
    User_Frame, textvariable=default_wert)
ent_yearly_thermal_energy_demand.place(
    relx=0.2, rely=0.25, relwidth=0.175, relheight=0.05, anchor='nw')

# User Profil
# comfort_factor

default_wert = tk.StringVar()
default_wert.set('None')

lbl_comfort_factor = tk.Label(User_Frame, text="comfort factor", anchor='nw')
lbl_comfort_factor.place(relx=0.025, rely=0.35,
                         relwidth=0.2, relheight=0.05, anchor='nw')

ent_comfort_factor = tk.Entry(User_Frame, textvariable=default_wert)
ent_comfort_factor.place(
    relx=0.2, rely=0.35, relwidth=0.175, relheight=0.05, anchor='nw')

# User Profil
# daily_vehicle_usage

default_wert = tk.StringVar()
default_wert.set('None')

lbl_daily_vehicle_usage = tk.Label(
    User_Frame, text="daily vehicle usage", anchor='nw')
lbl_daily_vehicle_usage.place(
    relx=0.025, rely=0.45, relwidth=0.2, relheight=0.05, anchor='nw')

ent_daily_vehicle_usage = tk.Entry(User_Frame, textvariable=default_wert)
ent_daily_vehicle_usage.place(
    relx=0.2, rely=0.45, relwidth=0.175, relheight=0.05, anchor='nw')

# User Profil
# building_type

default_wert = tk.StringVar()
default_wert.set('DE_HEF33')

lbl_building_type = tk.Label(User_Frame, text="building type", anchor='nw')
lbl_building_type.place(relx=0.025, rely=0.55,
                        relwidth=0.2, relheight=0.05, anchor='nw')

ent_building_type = tk.Entry(User_Frame, textvariable=default_wert)
ent_building_type.place(relx=0.2, rely=0.55,
                        relwidth=0.175, relheight=0.05, anchor='nw')

# User Profil
# t_0

default_wert = tk.StringVar()
default_wert.set(40)

lbl_t_0 = tk.Label(User_Frame, text="T0", anchor='nw')
lbl_t_0.place(relx=0.025, rely=0.65, relwidth=0.2, relheight=0.05, anchor='nw')

ent_t_0 = tk.Entry(User_Frame, textvariable=default_wert)
ent_t_0.place(relx=0.2, rely=0.65, relwidth=0.175, relheight=0.05, anchor='nw')

# User Profil
baseload_file = "./input/baseload/df_S_15min.csv"


def baseload_func():
    global baseload_file

    baseload_file = filedialog.askopenfilename(
        title="Select files", filetypes=(("csv files", "*.csv"), ("Excel", "*.xlsx")))

    lbl_baseload = tk.Label(User_Frame, text=baseload_file, anchor='nw')
    lbl_baseload.place(relx=0.2, rely=0.75, relwidth=0.65, relheight=0.05)


btn_wind_file = tk.Button(
    User_Frame, text="baseload file", command=baseload_func)
btn_wind_file.place(relx=0.025, rely=0.75, relwidth=0.1,
                    relheight=0.05, anchor='nw')

lbl_baseload = tk.Label(User_Frame, text=baseload_file, anchor='nw')
lbl_baseload.place(relx=0.2, rely=0.75, relwidth=0.65, relheight=0.05)


################################ Wind ###########################################
#################################################################################


Wind_turbine_Frame = tk.LabelFrame(Wind_Frame, text="Wind Turbine Data")
Wind_turbine_Frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N)

Wind_modelchain_Frame = tk.LabelFrame(
    Wind_Frame, text="WindPower ModelChain Data")
Wind_modelchain_Frame.grid(row=0, column=1, pady=5, sticky=tk.N)

# WindTurbine data
# turbine_type

default_wert = tk.StringVar()
default_wert.set('E-126/4200')

lbl_turbine_type = tk.Label(
    Wind_turbine_Frame, text="turbine type", anchor='nw')
lbl_turbine_type.grid(row=0, column=0, padx=50, pady=10, sticky=tk.W)

ent_turbine_type = tk.Entry(Wind_turbine_Frame, textvariable=default_wert)
ent_turbine_type.grid(row=0, column=1, padx=50, pady=10, ipady=4, sticky=tk.W)


# WindTurbine data
# hub_height

default_wert = tk.IntVar()
default_wert.set(135)

lbl_hub_height = tk.Label(Wind_turbine_Frame, text="hub heigth", anchor='nw')
lbl_hub_height.grid(row=1, column=0, padx=50, pady=10, sticky=tk.W)

ent_hub_height = tk.Entry(Wind_turbine_Frame, textvariable=default_wert)
ent_hub_height.grid(row=1, column=1, padx=50, pady=10, ipady=4, sticky=tk.W)


# WindTurbine data
# rotor diameter

default_wert = tk.IntVar()
default_wert.set(127)

lbl_rotor_diameter = tk.Label(
    Wind_turbine_Frame, text="rotor diameter", anchor='nw')
lbl_rotor_diameter.grid(row=2, column=0, padx=50, pady=10, sticky=tk.W)

ent_rotor_diameter = tk.Entry(Wind_turbine_Frame, textvariable=default_wert)
ent_rotor_diameter.grid(row=2, column=1, padx=50,
                        pady=10, ipady=4, sticky=tk.W)

# WindTurbine data
# fetch_curve

default_wert = tk.StringVar()
default_wert.set('power_curve')

lbl_fetch_curve = tk.Label(
    Wind_turbine_Frame, text="comfort factor", anchor='nw')
lbl_fetch_curve.grid(row=3, column=0, padx=50, pady=10, sticky=tk.W)

ent_fetch_curve = tk.Entry(Wind_turbine_Frame, textvariable=default_wert)
ent_fetch_curve.grid(row=3, column=1, padx=50, pady=10, ipady=4, sticky=tk.W)

# WindTurbine data
# data_source

default_wert = tk.StringVar()
default_wert.set('oedb')

lbl_data_source = tk.Label(Wind_turbine_Frame, text="data source", anchor='nw')
lbl_data_source.grid(row=4, column=0, padx=50, pady=10, sticky=tk.W)

ent_data_source = tk.Entry(Wind_turbine_Frame, textvariable=default_wert)
ent_data_source.grid(row=4, column=1, padx=50, pady=10, ipady=4, sticky=tk.W)

# WindPower ModelChain data
# wind_speed_model

default_wert = tk.StringVar()
default_wert.set('logarithmic')

lbl_wind_speed_model = tk.Label(
    Wind_modelchain_Frame, text="wind speed model", anchor='nw')
lbl_wind_speed_model.grid(row=0, column=0, padx=30, pady=10, sticky=tk.W)

ent_wind_speed_model = tk.Entry(
    Wind_modelchain_Frame, textvariable=default_wert)
ent_wind_speed_model.grid(row=0, column=1, padx=30,
                          pady=10, ipady=4, sticky=tk.W)

# WindPower ModelChain data
# density_model

default_wert = tk.StringVar()
default_wert.set('ideal_gas')

lbl_density_model = tk.Label(
    Wind_modelchain_Frame, text="density model", anchor='nw')
lbl_density_model.grid(row=1, column=0, padx=30, pady=10, sticky=tk.W)

ent_density_model = tk.Entry(Wind_modelchain_Frame, textvariable=default_wert)
ent_density_model.grid(row=1, column=1, padx=30, pady=10, ipady=4, sticky=tk.W)

# WindPower ModelChain data
#temperature_model = 'linear_gradient'

default_wert = tk.StringVar()
default_wert.set('linear_gradient')

lbl_temperature_model = tk.Label(
    Wind_modelchain_Frame, text="temperature model", anchor='nw')
lbl_temperature_model.grid(row=2, column=0, padx=30, pady=10, sticky=tk.W)

ent_temperature_model = tk.Entry(
    Wind_modelchain_Frame, textvariable=default_wert)
ent_temperature_model.grid(row=2, column=1, padx=30,
                           pady=10, ipady=4, sticky=tk.W)

# WindPower ModelChain data
#power_output_model = 'power_curve'

default_wert = tk.StringVar()
default_wert.set('power_curve')

lbl_power_output_model = tk.Label(
    Wind_modelchain_Frame, text="power output model", anchor='nw')
lbl_power_output_model.grid(row=3, column=0, padx=30, pady=10, sticky=tk.W)

ent_power_output_model = tk.Entry(
    Wind_modelchain_Frame, textvariable=default_wert)
ent_power_output_model.grid(
    row=3, column=1, padx=30, pady=10, ipady=4, sticky=tk.W)

# WindPower ModelChain data
# density_correction = True

default_wert = tk.StringVar()
default_wert.set('True')

lbl_density_correction = tk.Label(
    Wind_modelchain_Frame, text="density correction", anchor='nw')
lbl_density_correction.grid(row=4, column=0, padx=30, pady=10, sticky=tk.W)

ent_density_correction = tk.Entry(
    Wind_modelchain_Frame, textvariable=default_wert)
ent_density_correction.grid(
    row=4, column=1, padx=30, pady=10, ipady=4, sticky=tk.W)

# WindPower ModelChain data
#obstacle_height = 0

default_wert = tk.IntVar()
default_wert.set(0)

lbl_obstacle_height = tk.Label(
    Wind_modelchain_Frame, text="obstacle height", anchor='nw')
lbl_obstacle_height.grid(row=5, column=0, padx=30, pady=10, sticky=tk.W)

ent_obstacle_height = tk.Entry(
    Wind_modelchain_Frame, textvariable=default_wert)
ent_obstacle_height.grid(row=5, column=1, padx=30,
                         pady=10, ipady=4, sticky=tk.W)

# WindPower ModelChain data
#hellman_exp = None

default_wert = tk.StringVar()
default_wert.set('None')

lbl_hellman_exp = tk.Label(Wind_modelchain_Frame,
                           text="hellman exponent", anchor='nw')
lbl_hellman_exp.grid(row=6, column=0, padx=30, pady=10, sticky=tk.W)

ent_hellman_exp = tk.Entry(Wind_modelchain_Frame, textvariable=default_wert)
ent_hellman_exp.grid(row=6, column=1, padx=30, pady=10, ipady=4, sticky=tk.W)

# WindPower ModelChain data
# wind_file

wind_file = "./input/wind/dwd_wind_data_2015.csv"


def wind_func():
    global wind_file

    wind_file = filedialog.askopenfilename(
        title="Select files", filetypes=(("csv files", "*.csv"), ("Excel", "*.xlsx")))

    lbl_wind = tk.Label(Wind_modelchain_Frame, text=wind_file, anchor='nw')
    lbl_wind.grid(row=7, column=1, padx=30, pady=10, sticky=tk.W)


btn_wind_file = tk.Button(Wind_modelchain_Frame,
                          text="wind file", command=wind_func)
btn_wind_file.grid(row=7, column=0, padx=30, pady=10, ipadx=40, sticky=tk.W)

lbl_wind = tk.Label(Wind_modelchain_Frame, text=wind_file, anchor='nw')
lbl_wind.grid(row=7, column=1, padx=30, pady=10, sticky=tk.W)


################################ BEV ############################################
#################################################################################


# BEV
# battery_max
default_wert = tk.IntVar()
default_wert.set(16)

lbl_battery_max = tk.Label(BEV_Frame, text="battery max", anchor='nw')
lbl_battery_max.place(relx=0.025, rely=0.05, relwidth=0.1,
                      relheight=0.05, anchor='nw')

ent_battery_max = tk.Entry(BEV_Frame, textvariable=default_wert)
ent_battery_max.place(relx=0.2, rely=0.05, relwidth=0.175,
                      relheight=0.05, anchor='nw')


# BEV
# battery_min
default_wert = tk.IntVar()
default_wert.set(0)

lbl_battery_min = tk.Label(BEV_Frame, text="battery min", anchor='nw')
lbl_battery_min.place(relx=0.025, rely=0.15, relwidth=0.1,
                      relheight=0.05, anchor='nw')

ent_battery_min = tk.Entry(BEV_Frame, textvariable=default_wert)
ent_battery_min.place(relx=0.2, rely=0.15, relwidth=0.175,
                      relheight=0.05, anchor='nw')

# BEV
# battery_usage = 1
default_wert = tk.IntVar()
default_wert.set(1)

lbl_battery_usage = tk.Label(BEV_Frame, text="battery usage", anchor='nw')
lbl_battery_usage.place(relx=0.025, rely=0.25,
                        relwidth=0.2, relheight=0.05, anchor='nw')

ent_battery_usage = tk.Entry(BEV_Frame, textvariable=default_wert)
ent_battery_usage.place(relx=0.2, rely=0.25,
                        relwidth=0.175, relheight=0.05, anchor='nw')

# BEV
# charging_power = 11
default_wert = tk.IntVar()
default_wert.set(11)

lbl_charging_power = tk.Label(BEV_Frame, text="charging power", anchor='nw')
lbl_charging_power.place(relx=0.025, rely=0.35,
                         relwidth=0.2, relheight=0.05, anchor='nw')

ent_charging_power = tk.Entry(BEV_Frame, textvariable=default_wert)
ent_charging_power.place(
    relx=0.2, rely=0.35, relwidth=0.175, relheight=0.05, anchor='nw')

# BEV
# charge_efficiency_bev = 0.98
default_wert = tk.IntVar()
default_wert.set(0.98)

lbl_charge_efficiency_bev = tk.Label(
    BEV_Frame, text="charge efficiency bev", anchor='nw')
lbl_charge_efficiency_bev.place(
    relx=0.025, rely=0.45, relwidth=0.2, relheight=0.05, anchor='nw')

ent_charge_efficiency_bev = tk.Entry(BEV_Frame, textvariable=default_wert)
ent_charge_efficiency_bev.place(
    relx=0.2, rely=0.45, relwidth=0.175, relheight=0.05, anchor='nw')


################################ PV #############################################
#################################################################################


# PV data
# module_lib
default_wert = tk.StringVar()
default_wert.set('SandiaMod')

lbl_module_lib = tk.Label(PV_Frame, text="module lib", anchor='nw')
lbl_module_lib.place(relx=0.025, rely=0.05, relwidth=0.1,
                     relheight=0.05, anchor='nw')

ent_module_lib = tk.Entry(PV_Frame, textvariable=default_wert)
ent_module_lib.place(relx=0.2, rely=0.05, relwidth=0.175,
                     relheight=0.05, anchor='nw')


# PV data
# module
default_wert = tk.StringVar()
default_wert.set('Canadian_Solar_CS5P_220M___2009_')

lbl_module = tk.Label(PV_Frame, text="module", anchor='nw')
lbl_module.place(relx=0.025, rely=0.15, relwidth=0.1,
                 relheight=0.05, anchor='nw')

ent_module = tk.Entry(PV_Frame, textvariable=default_wert)
ent_module.place(relx=0.2, rely=0.15, relwidth=0.25,
                 relheight=0.05, anchor='nw')

# PV data
# inverter_lib
default_wert = tk.StringVar()
default_wert.set('cecinverter')

lbl_inverter_lib = tk.Label(PV_Frame, text="inverter lib", anchor='nw')
lbl_inverter_lib.place(relx=0.025, rely=0.25,
                       relwidth=0.2, relheight=0.05, anchor='nw')

ent_inverter_lib = tk.Entry(PV_Frame, textvariable=default_wert)
ent_inverter_lib.place(relx=0.2, rely=0.25, relwidth=0.175,
                       relheight=0.05, anchor='nw')

# PV data
# inverter
default_wert = tk.StringVar()
default_wert.set('ABB__MICRO_0_25_I_OUTD_US_208__208V_')

lbl_inverter = tk.Label(PV_Frame, text="inverter", anchor='nw')
lbl_inverter.place(relx=0.025, rely=0.35, relwidth=0.2,
                   relheight=0.05, anchor='nw')

ent_inverter = tk.Entry(PV_Frame, textvariable=default_wert)
ent_inverter.place(relx=0.2, rely=0.35, relwidth=0.25,
                   relheight=0.05, anchor='nw')

# PV data
# surface_tilt = 20
default_wert = tk.IntVar()
default_wert.set(20)

lbl_surface_tilt = tk.Label(PV_Frame, text="surface tilt", anchor='nw')
lbl_surface_tilt.place(relx=0.025, rely=0.45,
                       relwidth=0.2, relheight=0.05, anchor='nw')

ent_surface_tilt = tk.Entry(PV_Frame, textvariable=default_wert)
ent_surface_tilt.place(relx=0.2, rely=0.45, relwidth=0.175,
                       relheight=0.05, anchor='nw')

# PV data
# surface_azimuth = 200
default_wert = tk.IntVar()
default_wert.set(200)

lbl_surface_azimuth = tk.Label(PV_Frame, text="surface azimuth", anchor='nw')
lbl_surface_azimuth.place(relx=0.025, rely=0.55,
                          relwidth=0.2, relheight=0.05, anchor='nw')

ent_surface_azimuth = tk.Entry(PV_Frame, textvariable=default_wert)
ent_surface_azimuth.place(
    relx=0.2, rely=0.55, relwidth=0.175, relheight=0.05, anchor='nw')

# PV data
# modules_per_string = 4
default_wert = tk.IntVar()
default_wert.set(4)

lbl_modules_per_string = tk.Label(
    PV_Frame, text="modules per string", anchor='nw')
lbl_modules_per_string.place(
    relx=0.025, rely=0.65, relwidth=0.2, relheight=0.05, anchor='nw')

ent_modules_per_string = tk.Entry(PV_Frame, textvariable=default_wert)
ent_modules_per_string.place(
    relx=0.2, rely=0.65, relwidth=0.175, relheight=0.05, anchor='nw')

# PV data
# strings_per_inverter = 2
default_wert = tk.IntVar()
default_wert.set(2)

lbl_strings_per_inverter = tk.Label(
    PV_Frame, text="strings per inverter", anchor='nw')
lbl_strings_per_inverter.place(
    relx=0.025, rely=0.75, relwidth=0.2, relheight=0.05, anchor='nw')

ent_strings_per_inverter = tk.Entry(PV_Frame, textvariable=default_wert)
ent_strings_per_inverter.place(
    relx=0.2, rely=0.75, relwidth=0.175, relheight=0.05, anchor='nw')

# PV data
# pv_file
pv_file = "./input/pv/dwd_pv_data_2015.csv"


def pv_func():
    global pv_file

    pv_file = filedialog.askopenfilename(title="Select files", filetypes=(
        ("csv files", "*.csv"), ("Excel", "*.xlsx")))

    lbl_pv_file = tk.Label(PV_Frame, text=pv_file, anchor='nw')
    lbl_pv_file.place(relx=0.2, rely=0.85, relwidth=0.65, relheight=0.05)


btn_pv_file = tk.Button(PV_Frame, text="pv file", command=pv_func)
btn_pv_file.place(relx=0.025, rely=0.85, relwidth=0.1,
                  relheight=0.05, anchor='nw')

lbl_pv_file = tk.Label(PV_Frame, text=wind_file, anchor='nw')
lbl_pv_file.place(relx=0.2, rely=0.85, relwidth=0.65, relheight=0.05)


################################ Heat Pump ######################################
#################################################################################


# heat pump data
# heatpump_type
default_wert = tk.StringVar()
default_wert.set('Air')

lbl_heatpump_type = tk.Label(
    heat_pump_Frame, text="heatpump type", anchor='nw')
lbl_heatpump_type.place(relx=0.025, rely=0.05,
                        relwidth=0.1, relheight=0.05, anchor='nw')

ent_heatpump_type = tk.Entry(heat_pump_Frame, textvariable=default_wert)
ent_heatpump_type.place(relx=0.2, rely=0.05,
                        relwidth=0.175, relheight=0.05, anchor='nw')

# heat pump data
# heat_sys_temp
default_wert = tk.IntVar()
default_wert.set(60)

lbl_heat_sys_temp = tk.Label(
    heat_pump_Frame, text="heat system temp", anchor='nw')
lbl_heat_sys_temp.place(relx=0.025, rely=0.15,
                        relwidth=0.1, relheight=0.05, anchor='nw')

ent_heat_sys_temp = tk.Entry(heat_pump_Frame, textvariable=default_wert)
ent_heat_sys_temp.place(relx=0.2, rely=0.15,
                        relwidth=0.175, relheight=0.05, anchor='nw')

# heat pump data
# el_power
default_wert = tk.IntVar()
default_wert.set(5)

lbl_el_power = tk.Label(heat_pump_Frame, text="electrical power", anchor='nw')
lbl_el_power.place(relx=0.025, rely=0.25, relwidth=0.1,
                   relheight=0.05, anchor='nw')

ent_el_power = tk.Entry(heat_pump_Frame, textvariable=default_wert)
ent_el_power.place(relx=0.2, rely=0.25, relwidth=0.175,
                   relheight=0.05, anchor='nw')

# heat pump data
# building_type = 'DE_HEF33'

default_wert = tk.StringVar()
default_wert.set('DE_HEF33')

lbl_building_type = tk.Label(
    heat_pump_Frame, text="building type", anchor='nw')
lbl_building_type.place(relx=0.025, rely=0.35,
                        relwidth=0.1, relheight=0.05, anchor='nw')

ent_building_type = tk.Entry(heat_pump_Frame, textvariable=default_wert)
ent_building_type.place(relx=0.2, rely=0.35,
                        relwidth=0.175, relheight=0.05, anchor='nw')


################################ Storage ########################################
#################################################################################


# storage
# charge_efficiency_storage = 0.98
default_wert = tk.IntVar()
default_wert.set(0.98)

lbl_charge_efficiency_storage = tk.Label(
    storage_Frame, text="charge efficiency storage", anchor='nw')
lbl_charge_efficiency_storage.place(
    relx=0.025, rely=0.05, relwidth=0.175, relheight=0.05, anchor='nw')

ent_charge_efficiency_storage = tk.Entry(
    storage_Frame, textvariable=default_wert)
ent_charge_efficiency_storage.place(
    relx=0.2, rely=0.05, relwidth=0.175, relheight=0.05, anchor='nw')

# storage
# discharge_efficiency_storage = 0.98
default_wert = tk.IntVar()
default_wert.set(0.98)

lbl_discharge_efficiency_storage = tk.Label(
    storage_Frame, text="discharge efficiency storage", anchor='nw')
lbl_discharge_efficiency_storage.place(
    relx=0.025, rely=0.15, relwidth=0.175, relheight=0.05, anchor='nw')

ent_discharge_efficiency_storage = tk.Entry(
    storage_Frame, textvariable=default_wert)
ent_discharge_efficiency_storage.place(
    relx=0.2, rely=0.15, relwidth=0.175, relheight=0.05, anchor='nw')

# storage
# max_power = 4  # kW
default_wert = tk.IntVar()
default_wert.set(4)

lbl_max_power = tk.Label(storage_Frame, text="max power [kW]", anchor='nw')
lbl_max_power.place(relx=0.025, rely=0.25, relwidth=0.1,
                    relheight=0.05, anchor='nw')

ent_max_power = tk.Entry(storage_Frame, textvariable=default_wert)
ent_max_power.place(relx=0.2, rely=0.25, relwidth=0.175,
                    relheight=0.05, anchor='nw')

# storage
# capacity = 4  # kWh
default_wert = tk.IntVar()
default_wert.set(4)

lbl_capacity = tk.Label(storage_Frame, text="capacity [kWh]", anchor='nw')
lbl_capacity.place(relx=0.025, rely=0.35, relwidth=0.1,
                   relheight=0.05, anchor='nw')

ent_capacity = tk.Entry(storage_Frame, textvariable=default_wert)
ent_capacity.place(relx=0.2, rely=0.35, relwidth=0.175,
                   relheight=0.05, anchor='nw')

# storage
# max_c = 1  # factor between 0.5 and 1.2
default_wert = tk.IntVar()
default_wert.set(1)

lbl_max_c = tk.Label(
    storage_Frame, text="max C-rate (0.5 to 1.2)", anchor='nw')
lbl_max_c.place(relx=0.025, rely=0.45, relwidth=0.175,
                relheight=0.05, anchor='nw')

ent_max_c = tk.Entry(storage_Frame, textvariable=default_wert)
ent_max_c.place(relx=0.2, rely=0.45, relwidth=0.175,
                relheight=0.05, anchor='nw')

################################ Grundeinstellungen #############################
#################################################################################

default_wert = tk.IntVar()
default_wert.set(50)

lbl_pv_percentage = tk.Label(
    Grundeinstellungen_Frame, text="pv percentage", anchor='nw')
lbl_pv_percentage.place(relx=0.025, rely=0.05,
                        relwidth=0.1, relheight=0.05, anchor='nw')

ent_pv_percentage = tk.Entry(
    Grundeinstellungen_Frame, textvariable=default_wert)
ent_pv_percentage.place(relx=0.2, rely=0.05,
                        relwidth=0.175, relheight=0.05, anchor='nw')


default_wert = tk.IntVar()
default_wert.set(50)

lbl_storage_percentage = tk.Label(
    Grundeinstellungen_Frame, text="storage percentage", anchor='nw')
lbl_storage_percentage.place(
    relx=0.025, rely=0.15, relwidth=0.175, relheight=0.05, anchor='nw')

ent_storage_percentage = tk.Entry(
    Grundeinstellungen_Frame, textvariable=default_wert)
ent_storage_percentage.place(
    relx=0.2, rely=0.15, relwidth=0.175, relheight=0.05, anchor='nw')

default_wert = tk.IntVar()
default_wert.set(0)

lbl_bev_percentage = tk.Label(
    Grundeinstellungen_Frame, text="BEV percentage", anchor='nw')
lbl_bev_percentage.place(relx=0.025, rely=0.25,
                         relwidth=0.1, relheight=0.05, anchor='nw')

ent_bev_percentage = tk.Entry(
    Grundeinstellungen_Frame, textvariable=default_wert)
ent_bev_percentage.place(
    relx=0.2, rely=0.25, relwidth=0.175, relheight=0.05, anchor='nw')

default_wert = tk.IntVar()
default_wert.set(0)

lbl_hp_percentage = tk.Label(
    Grundeinstellungen_Frame, text="heat pump percentage", anchor='nw')
lbl_hp_percentage.place(relx=0.025, rely=0.35,
                        relwidth=0.175, relheight=0.05, anchor='nw')

ent_hp_percentage = tk.Entry(
    Grundeinstellungen_Frame, textvariable=default_wert)
ent_hp_percentage.place(relx=0.2, rely=0.35,
                        relwidth=0.175, relheight=0.05, anchor='nw')

default_wert = tk.IntVar()
default_wert.set(0)

lbl_wind_percentage = tk.Label(
    Grundeinstellungen_Frame, text="wind percentage", anchor='nw')
lbl_wind_percentage.place(relx=0.025, rely=0.45,
                          relwidth=0.1, relheight=0.05, anchor='nw')

ent_wind_percentage = tk.Entry(
    Grundeinstellungen_Frame, textvariable=default_wert)
ent_wind_percentage.place(
    relx=0.2, rely=0.45, relwidth=0.175, relheight=0.05, anchor='nw')

################################ Ergebnis #######################################
#################################################################################


loadprofiles = tk.LabelFrame(Ergebnis_Frame, text='Datenreihen')
loadprofiles.place(relx=0.05, rely=0.05, anchor='nw')

btn_load = tk.Button(Ergebnis_Frame, text='Lastprofil',
                     state=tk.DISABLED, command=graph)
btn_load.place(relx=0.6, rely=0.885, relwidth=0.1,
               relheight=0.051, anchor='nw')

btn_simulate = tk.Button(root, text="Simulieren", command=simulieren)
btn_simulate.place(relx=0.725, rely=0.8825, relwidth=0.1,
                   relheight=0.05, anchor='nw')

btn_quit = tk.Button(root, text="Beenden", command=Program_Exit)
btn_quit.place(relx=0.85, rely=0.8825, relwidth=0.1,
               relheight=0.05, anchor='nw')

lbl_date = tk.Label(
    Ergebnis_Frame, text="Zeitpunkt für  Netzdarstellung:",  anchor='nw')
lbl_date.place(relx=0.25, rely=0.05, relwidth=0.18,
               relheight=0.05, anchor='nw')

dd_date = ttk.Combobox(Ergebnis_Frame, state=tk.DISABLED)
dd_date.place(relx=0.25, rely=0.1, relwidth=0.18, relheight=0.05, anchor='nw')

"""
Schieberegler für die EEinstellung der maximalen Netzbelastung.
"""

sld_line_max = tk.Scale(Ergebnis_Frame, length=250,
                        label="max. Leitungsbelastung [%]", from_=1, to=130, orient=tk.HORIZONTAL, state=tk.DISABLED)
sld_line_max.place(relx=0.25, rely=0.2, relwidth=0.18,
                   relheight=0.125, anchor='nw')

sld_line_min = tk.Scale(Ergebnis_Frame, length=250,
                        label="min. Leitungsbelastung [%]", from_=0, to=130, orient=tk.HORIZONTAL, state=tk.DISABLED)
sld_line_min.place(relx=0.25, rely=0.35, relwidth=0.18,
                   relheight=0.125, anchor='nw')


sld_trafo_max = tk.Scale(Ergebnis_Frame, length=250,
                         label="max. Trafobelastung [%]", from_=1, to=130, orient=tk.HORIZONTAL, state=tk.DISABLED)
sld_trafo_max.place(relx=0.5, rely=0.2, relwidth=0.18,
                    relheight=0.125, anchor='nw')

sld_trafo_min = tk.Scale(Ergebnis_Frame, length=250,
                         label="min. Trafobelastung [%]", from_=0, to=130, orient=tk.HORIZONTAL, state=tk.DISABLED)
sld_trafo_min.place(relx=0.5, rely=0.35, relwidth=0.18,
                    relheight=0.125, anchor='nw')


sld_bus_max = tk.Scale(Ergebnis_Frame, length=250,
                       label="max. Knotenspannung [%]", from_=100, to=130, orient=tk.HORIZONTAL, state=tk.DISABLED)
sld_bus_max.place(relx=0.75, rely=0.2, relwidth=0.18,
                  relheight=0.125, anchor='nw')

sld_bus_min = tk.Scale(Ergebnis_Frame, length=250,
                       label="min. Knotenspannung [%]", from_=70, to=100, orient=tk.HORIZONTAL, state=tk.DISABLED)
sld_bus_min.place(relx=0.75, rely=0.35, relwidth=0.18,
                  relheight=0.125, anchor='nw')
"""
Button auf der Ergebnis-Seite.
"""
btn_load = tk.Button(Ergebnis_Frame, text='Lastprofil',
                     state=tk.DISABLED, command=graph)
btn_load.place(relx=0.6, rely=0.885, relwidth=0.1,
               relheight=0.051, anchor='nw')

btn_simulate = tk.Button(root, text="Simulieren", command=simulieren)
btn_simulate.place(relx=0.725, rely=0.8825, relwidth=0.1,
                   relheight=0.05, anchor='nw')

btn_quit = tk.Button(root, text="Beenden", command=Program_Exit)
btn_quit.place(relx=0.85, rely=0.8825, relwidth=0.1,
               relheight=0.05, anchor='nw')

btn_net = tk.Button(Ergebnis_Frame, text='Netz',
                    command=net_show, state=tk.DISABLED)
btn_net.place(relx=0.475, rely=0.885, relwidth=0.1,
              relheight=0.051, anchor='nw')

btn_save = tk.Button(Ergebnis_Frame, text='CSV exportieren',
                     command=csv_export, state=tk.DISABLED)
btn_save.place(relx=0.35, rely=0.885, relwidth=0.1,
               relheight=0.051, anchor='nw')

root.mainloop()
