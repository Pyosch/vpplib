# -*- coding: utf-8 -*-
"""
Info
----
This module defines the layout and callbacks for the basic settings tab in the GUI.
It contains inputfields for the user to input the number of pv plants, storage units, battery electric vehicles, heat pumps, and wind turbines.

Functions:
- update_basic_settings: Update basic settings based on user inputs.

The layout is defined using the Dash Bootstrap Components library.
The submitted data is stored in store_basic_settings.
"""

from dash import html, callback, Input, Output, State, callback_context as ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

#Layout Section_________________________________________________________________________________________
layout=dbc.Container([
    
     dbc.Row([
                        dbc.Col([
                                html.P('PV Plants')
                            ], width=3),
                        dbc.Col([
                            dbc.Input(
                                id='input_pv_plants',
                                type='number',
                                placeholder='5',
                                value=0)
                        ],width=1)
                        ],style={'margin-top': '20px'}, align='center'),
                        dbc.Row([
                            dbc.Col([
                                    html.P('Storage Units')
                                ],width=3),
                            dbc.Col([
                                dbc.Input(
                                    id='input_storage_units',
                                    type='number',
                                    placeholder='2',
                                    value=0),
                                ], width=1)
                            ],align='center'),
                        dbc.Row([
                            dbc.Col([
                                    html.P('Battery Electric Vehicles')
                                ],width=3),
                            dbc.Col([
                                dbc.Input(
                                    id='input_bev_number',
                                    type='number',
                                    placeholder='3',
                                    value=0)
                                ], width=1)
                            ],align='center'),
                        dbc.Row([
                            dbc.Col([
                                    html.P('Heat Pumps')
                                ],width=3),
                            dbc.Col([
                                dbc.Input(
                                    id='input_hp_number',
                                    type='number',
                                    placeholder='1',
                                    value=0),
                                ], width=1)
                            ],align='center'),
                        dbc.Row([
                            dbc.Col([
                                    html.P('Wind Turbines')
                                ],width=3),
                            dbc.Col([
                                dbc.Input(
                                    id='input_wind_number',
                                    type='number',
                                    placeholder='3',
                                    value=6),
                                ], width=1)    
                        ],align='center'),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button('Submit Settings',
                                           id='submit_basic_settings',
                                           color='primary')
                            ])
                        ])
                    
])

#Callback Section_________________________________________________________________________________________
@callback(
    Output('store_basic_settings', 'data'),
    [Input('submit_basic_settings', 'n_clicks')],
    [State('input_pv_plants', 'value'),
     State('input_storage_units', 'value'),
     State('input_bev_number', 'value'),
     State('input_hp_number', 'value'),
     State('input_wind_number', 'value')]
)
def update_basic_settings(n_clicks, pv_plants, storage_units, 
                          bev_number, hp_number, wind_number):
    """
    Update the basic settings based on user input.

    Parameters:
    - n_clicks (int): The number of times the submit button is clicked.
    - pv_plants (int): The number of PV plants.
    - storage_units (int): The number of storage units.
    - bev_number (int): The number of battery electric vehicles.
    - hp_number (int): The number of heat pumps.
    - wind_number (int): The number of wind turbines.

    Returns:
    - data_basic_settings (dict): A dictionary containing the updated basic settings.

    Raises:
    - PreventUpdate: If the submit button is not clicked.

    """
    if 'submit_basic_settings' == ctx.triggered_id and n_clicks is not None:
        data_basic_settings = {
            'pv_plants': pv_plants,
            'storage_units': storage_units,
            'bev_number': bev_number,
            'hp_number': hp_number,
            'wind_number': wind_number
        }
        return data_basic_settings
    elif n_clicks is None:
        raise PreventUpdate





