# -*- coding: utf-8 -*-
"""
Info
----
This module defines the layout and callbacks for the heatpump tab in the GUI.
It contains inputfields for the user to input the type of heatpump, the heat system temperature, and the electrical power of the heatpump.

Functions:
- update_heatpump_settings: Update heatpump settings based on user inputs.

The layout is defined using the Dash Bootstrap Components library.
The submitted data is stored in store_heatpump.

@author: sharth1
"""

from dash import  dcc, html, callback, Input, Output, State, callback_context as ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

#Layout Section_________________________________________________________________________________________
layout=dbc.Container([
dbc.Row([
                dbc.Col([
                    html.P('Type of Heat Pump')
                ], width=3),
                dbc.Col([
                    dcc.Dropdown(
                        ['Air', 'Ground'],
                        id='dropdown_heatpump_type',
                        style={'width': '100%',
                                'color': 'black',
                                'bgcolor': 'white',
                                },
                        placeholder='e.g. Air',
                        value='Air'
                    )
                ], width=2)
            ], style={'margin-top': '20px'}),
            dbc.Row([
                dbc.Col([
                    html.P('Heat System Temperature')
                ], width=3),
                dbc.Col([
                    dbc.InputGroup([
                        dbc.Input(
                            id='input_heatpump_system_temperature',
                            type='number',
                            placeholder='e.g. 20.5 °C',
                            value=0
                        ),
                        dbc.InputGroupText('°C')
                    ])
                ], width=2)
            ]),
            dbc.Row([
                dbc.Col([
                    html.P('Electrical Power')
                    ], width=3),
                dbc.Col([
                    dbc.InputGroup([
                        dbc.Input(
                            id='input_heatpump_electrical_power',
                            type='number',
                            placeholder='e.g. 5 kW',
                            value= 0
                        ),
                        dbc.InputGroupText('kW')
                    ])
                ], width=2)
            ]),
            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Submit Settings',
                                               id='submit_hp_settings',
                                               color='primary')
                                ])
                            ])
                
])

#Callback Section_________________________________________________________________________________________
@callback(
    Output('store_heatpump', 'data'),
    [Input('submit_hp_settings', 'n_clicks')],
    [State('dropdown_heatpump_type', 'value'),
     State('input_heatpump_system_temperature', 'value'),
     State('input_heatpump_electrical_power', 'value')]
)
def update_heatpump_settings(n_clicks, type_hp, temp_hp, power_hp):
    """
    Update the heat pump settings based on the user inputs.

    Parameters:
    - n_clicks (int): The number of times the submit button is clicked.
    - type_hp (str): The type of heat pump.
    - temp_hp (float): The desired heat system temperature.
    - power_hp (float): The power of the heat pump.

    Returns:
    - data_heatpump (dict): A dictionary containing the updated heat pump settings.
    """
    if 'submit_hp_settings' == ctx.triggered_id and n_clicks is not None:
        data_heatpump = {
            'Type Heatpump': type_hp,
            'Heat System Temperature': temp_hp,
            'Power': power_hp,
        }
        return data_heatpump
    elif n_clicks is None:
        raise PreventUpdate
