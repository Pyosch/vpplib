# -*- coding: utf-8 -*-
"""
Info
----
This module defines the layout and callbacks for the hydrogen tab in the GUI.
It contains input fields for power and pressure settings of an electrolyzer,
buttons for submitting settings, simulating, and downloading results,
dropdowns for selecting power and quantity data, and graphs for displaying the data.

Functions:
- update_hydrogen_settings: Updates the hydrogen settings based on user input.
- simulate_button_hydrogen: Simulates the electrolyzer based on the hydrogen settings.
- download: Downloads the time series data for hydrogen.

The layout is defined using the Dash Bootstrap Components library.
The data for power and quantity dropdowns is read from a CSV file.
The graphs are created using Plotly Express.

@author: sharth1
"""

from dash import html, Input, Output, State, callback, callback_context as ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

#Layout Section_______________________________________________________________________________________________________________________

layout=dbc.Container([
dbc.Row([
                    dbc.Col([
                        html.P('Power Electrolyzer')
                    ], width=3),
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id='input_electrolyzer_power',
                                type='number',
                                placeholder='e.g. 100 kW',
                                value=15000),
                            dbc.InputGroupText('kW')
                    ])
                    ], width=2),
                ], style={'margin-top': '20px'}),
                dbc.Row([
                    dbc.Col([
                        html.P('Pressure')
                    ], width=3),
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id='input_electrolyzer_pressure',
                                type='number',
                                placeholder='e.g. 150 bar',
                                value=30
                            ),
                            dbc.InputGroupText('bar')
                    ])
                    ], width=2),
                ]),
                dbc.Row([
                                dbc.Col([
                                    dbc.Button('Submit Settings',
                                               id='submit_hydrogen_settings',
                                               color='primary')
                                ], width=2),
                                
])])

#Callback Section_______________________________________________________________________________________________________________________
#Callback Structure:
#1. Update hydrogen settings
#2. Simulate button hydrogen
#3. Download
#4. Build graph 1
#5. Build graph 2
#6. Build graph 3

@callback(
    Output('store_hydrogen', 'data'),
    [Input('submit_hydrogen_settings', 'n_clicks')],
    [State('input_electrolyzer_power', 'value'),
     State('input_electrolyzer_pressure', 'value'),
    ],
)

def update_hydrogen_settings(n_clicks, power, pressure):
    """
    Updates the hydrogen settings based on user input.

    Parameters:
    - n_clicks (int): The number of times the submit button is clicked.
    - power (float): The power input value from the user.
    - pressure (float): The pressure input value from the user.

    Returns:
    - data_hydrogen_settings (dict): A dictionary containing the updated hydrogen settings.

    Raises:
    - PreventUpdate: If the submit button is not clicked.
    """
    if 'submit_hydrogen_settings' ==ctx.triggered_id:
        data_hydrogen_settings={'Power_Electrolyzer': power,
                            'Pressure_Hydrogen': pressure,}
        return data_hydrogen_settings
    
    elif n_clicks is None:
        raise PreventUpdate


