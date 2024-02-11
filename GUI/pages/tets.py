import pandas as pd
import pandapower as pp
import pandapower.networks as pn
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash 
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc  
import sys
import os


sys.path.append(os.path.abspath(os.path.join('')))
from vpplib.environment import Environment
from vpplib.user_profile import UserProfile
from vpplib.photovoltaic import Photovoltaic
from vpplib.battery_electric_vehicle import BatteryElectricVehicle
from vpplib.heat_pump import HeatPump
from vpplib.electrical_energy_storage import ElectricalEnergyStorage
from vpplib.wind_power import WindPower
from vpplib.virtual_power_plant import VirtualPowerPlant
from vpplib.operator import Operator

print(WindPower.get_turbine_types())