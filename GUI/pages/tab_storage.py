# -*- coding: utf-8 -*-
"""
Info
----
This module defines the layout and callbacks for the storage tab in the GUI.
It contains inputfields for the user to input the charge efficiency, discharge efficiency, max power, and max capacity of the storage system.

Functions:
- update_storage_settings: Update storage settings based on user inputs.


The layout is defined using the Dash Bootstrap Components library.
The submitted data is stored in store_storage.

@author: sharth1
"""

from dash import html, callback, Input, Output, State, callback_context as ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

#Layout Section_________________________________________________________________________________________
layout=dbc.Container([
    dbc.Row([
                        dbc.Col([
                            html.P('Charge Efficiency')
                        ], width=3),
                        dbc.Col([
                            dbc.InputGroup([
                            dbc.Input(
                                id='input_storage_charge_efficiency',
                                type='number',
                                placeholder='e.g. 90%',
                                value=0),
                                
                            dbc.InputGroupText('%')
                        ])
                        ], width=2)
                    ],style={'margin-top':'20px'}),
                    dbc.Row([
                        dbc.Col([
                            html.P('Discharge Efficiency')
                        ], width=3),
                        dbc.Col([
                            dbc.InputGroup([
                            dbc.Input(
                                id='input_storage_discharge_efficiency',
                                type='number',
                                placeholder='e.g. 90%',
                                value=0),
                            dbc.InputGroupText('%')
                            ])
                        ], width=2)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.P('Max. Power')
                        ], width=3),
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.Input(
                                    id='input_storage_max_power',
                                    type='number',
                                    placeholder='e.g. 10 kW',
                                    value=0),
                                dbc.InputGroupText('kW')
                            ])
                        ], width=2)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.P('Max. Capacity')
                        ], width=3),
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.Input(
                                    id='input_storage_max_capacity',
                                    type='number',
                                    placeholder='e.g. 10 kWh',
                                    value=0),
                                dbc.InputGroupText('kWh')
                            ])
                        ], width=2)
                    ]),
                    dbc.Row([
                                dbc.Col([
                                    dbc.Button('Submit Settings',
                                               id='submit_storage_settings',
                                               color='primary')
                                ])
                            ])
                
])

#Callbacks Section_______________________________________________________________________________________
@callback(
    Output('store_storage', 'data'),
    [Input('submit_storage_settings', 'n_clicks')],
    [State('input_storage_charge_efficiency', 'value'),
     State('input_storage_discharge_efficiency', 'value'),
     State('input_storage_max_power', 'value'),
     State('input_storage_max_capacity', 'value')]
)
def update_storage_settings(n_clicks, storage_charge_efficiency, storage_discharge_efficiency, 
                                storage_max_power, storage_max_capacity):
    """
    Update the storage settings based on user inputs.

    Parameters:
    - n_clicks (int): The number of times the submit button has been clicked.
    - storage_charge_efficiency (float): The charging efficiency of the storage system (in percentage).
    - storage_discharge_efficiency (float): The discharging efficiency of the storage system (in percentage).
    - storage_max_power (float): The maximum power of the storage system.
    - storage_max_capacity (float): The maximum capacity of the storage system.

    Returns:
    - data_storage_settings (dict): A dictionary containing the updated storage settings.

    Raises:
    - PreventUpdate: If the submit button has not been clicked.

    """
    
    if 'submit_storage_settings' == ctx.triggered_id and n_clicks is not None:

        data_storage_settings = {
            'Charging Efficiency': storage_charge_efficiency / 100,
            'Discharging Efficiency': storage_discharge_efficiency / 100,
            'Max. Power': storage_max_power,
            'Max. Capacity': storage_max_capacity
        }
        
        return data_storage_settings
    
    elif n_clicks is None:
        raise PreventUpdate