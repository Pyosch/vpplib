# -*- coding: utf-8 -*-
"""
Info
----
This script creates a Dash application for the VPPlib Simulation GUI.

The application consists of a tabbed layout with various tabs for different settings and functionalities.
Each tab is associated with a specific layout defined in separate modules.

The main layout of the application is a container with a row containing a heading, and a tab component.
The tab component contains multiple tabs, each representing a different aspect of the simulation.
These tabs include basic settings, environment, user profile, BEV, photovoltaic, wind, heat pump, storage, hydrogen, simulation and results, and graphs.
Those tabs are defined in separate modules saved in the pages folder.

The application uses Dash Bootstrap Components for styling.

Functions:
- render_content: Renders the content of the active tab based on user selection.

To run the application, execute this script.

Note: This script assumes that the necessary modules and packages are imported and available.

@author: sharth1
"""

import dash 
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc  
import sys
import os
from pages import tab_basic_settings, tab_environment, tab_user_profile, tab_bev, tab_pv, tab_wind, tab_heatpump, tab_storage, tab_hydrogen, tab_run_simulation, tab_all_parameters, tab_graphs, tab_comparison
sys.path.append(os.path.abspath(os.path.join('')))

#Layout Section_________________________________________________________________________________________
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)  

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('VPPlib Simulation')
        ],align='middle')
    ],style={'margin-top': '20px', 
             'margin-bottom': '20px'}),
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
        dbc.Tab(label='Summary Parameters', 
                tab_id='tab_results',
                active_label_style={'color': 'grey'}),
        dbc.Tab(label='Simulation and Results',
                tab_id='tab_run_simulation',
                active_label_style={'color': 'grey'}),
        dbc.Tab(label='Graphs',
                tab_id='tab_graphs',
                active_label_style={'color': 'grey'}),
        dbc.Tab(label='Hydrogen',
                tab_id='tab_hydrogen',
                active_label_style={'color': 'grey'}),
        dbc.Tab(label='Comparison',
                tab_id='tab_comparison',
                active_label_style={'color': 'grey'}),
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
    dcc.Store(id='store_simulation', data={}, storage_type='session'),
    dcc.Store(id='store_hydrogen', data={}, storage_type='session'),
])

#Callback Section_______________________________________________________________________________________
@app.callback(Output('tab-content', 'children'),
            [Input('tabs', 'active_tab')]
            )
def render_content(active_tab):
    """
    Callback function to render the content of the active tab.

    Parameters:
    - active_tab (str): The ID of the active tab.

    Returns:
    - The layout of the active tab.
    """
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
        return tab_all_parameters.layout
    elif active_tab == 'tab_run_simulation':
        return tab_run_simulation.layout
    elif active_tab == 'tab_hydrogen':
        return tab_hydrogen.layout
    elif active_tab == 'tab_graphs':
        return tab_graphs.layout
    elif active_tab == 'tab_comparison':
        return tab_comparison.layout

if __name__ == '__main__':
    app.run_server(debug=True)

