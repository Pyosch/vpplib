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

# from vpplib.environment import Environment
# from vpplib.user_profile import UserProfile
# from vpplib.photovoltaic import Photovoltaic
# from vpplib.battery_electric_vehicle import BatteryElectricVehicle
# from vpplib.heat_pump import HeatPump
# from vpplib.electrical_energy_storage import ElectricalEnergyStorage
# from vpplib.wind_power import WindPower
# from vpplib.virtual_power_plant import VirtualPowerPlant
# from vpplib.operator import Operator

from pages import tab_basic_settings, tab_environment, tab_user_profile, tab_bev, tab_pv, tab_wind, tab_heatpump, tab_storage, tab_results, tab_test



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)  


app.layout = dbc.Container([

dbc.Row([
    dbc.Col([
        html.H1('VPPlib Simulation')
    ],align='middle')
    
    ],style={'margin-top': '20px', 
             'margin-bottom': '20px',
             }),
    dbc.Tabs(id='tabs', children=[
        dbc.Tab(label='Basic Settings', 
                tab_id='tab_basic_settings',
                active_label_style={'color': 'grey'}),
        dbc.Tab(label='Environment', 
                tab_id= 'tab_environment',
                active_label_style={'color': 'grey'}),
        dbc.Tab(label='User Profile', 
                tab_id='tab_user_profile',
                active_label_style={'color': 'grey'}),
        dbc.Tab(label='BEV', 
                tab_id='tab_bev',
                active_label_style={'color': 'grey'}),
        dbc.Tab(label='Photovoltaic', 
                tab_id='tab_pv',
                active_label_style={'color': 'grey'}),
        dbc.Tab(label='Wind', 
                tab_id='tab_wind',
                active_label_style={'color': 'grey'}),
        dbc.Tab(label='Heat Pump', 
                tab_id='tab_heatpump',
                active_label_style={'color': 'grey'}),
        dbc.Tab(label='Storage', 
                tab_id='tab_storage',
                active_label_style={'color': 'grey'}),
        dbc.Tab(label='Results', 
                tab_id='tab_results',
                active_label_style={'color': 'grey'}),
        dbc.Tab(label='tab_test',
                tab_id='tab_test',
                active_label_style={'color': 'grey'})
        
]),
dbc.Container(id='tab-content'),
dcc.Store(id='store_basic_settings', data={}, storage_type='session'),
dcc.Store(id='store_environment', data={}, storage_type='session'),
dcc.Store(id='store_user_profile', data={}, storage_type='session'),
dcc.Store(id='store_bev', data={}, storage_type='session'),
dcc.Store(id='store_pv', data={}, storage_type='session'),
dcc.Store(id='store_wind', data={}, storage_type='session'),
dcc.Store(id='store_heatpump', data={}, storage_type='session'),
dcc.Store(id='store_storage', data={}, storage_type='session'),
dcc.Store(id='store_results', data={}, storage_type='session'),
])


# Define the callback to switch between tabs
@app.callback(Output('tab-content', 'children'),
            [Input('tabs', 'active_tab')]
            )
def render_content(active_tab):
    if active_tab == 'tab_basic_settings':
        return tab_basic_settings.layout
    elif active_tab == 'tab_environment':
        return tab_environment.layout
    elif active_tab == 'tab_user_profile':
        return tab_user_profile.layout
    elif active_tab == 'tab_bev':
        return tab_bev.layout
    elif active_tab == 'tab_pv':
        return tab_pv.layout
    elif active_tab == 'tab_wind':
        return tab_wind.layout
    elif active_tab == 'tab_heatpump':
        return tab_heatpump.layout
    elif active_tab == 'tab_storage':
        return tab_storage.layout
    elif active_tab == 'tab_results':
        return tab_results.layout
    elif active_tab == 'tab_test':
        return tab_test.layout

if __name__ == '__main__':
    app.run_server(debug=True)

