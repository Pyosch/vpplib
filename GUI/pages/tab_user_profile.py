# -*- coding: utf-8 -*-
"""
Info
----
This module defines the layout and callbacks for the user profile tab in the GUI.
It contains inputfields for the user to input the identifier, latitude, longitude, max. radius to weather stations,
thermal energy demand, comfort factor, daily vehicle usage, building type, and T0.

Functions:
- update_user_profile: Update user profile based on user inputs.

The layout is defined using the Dash Bootstrap Components library.
The submitted data is stored in store_user_profile.

@author: sharth1
"""

from dash import dcc, html, callback, Input, Output, State, dash_table, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate
import base64
import io
import datetime

#Layout Section_________________________________________________________________________________________
layout=dbc.Container([
dbc.Row([
                    dbc.Col([
                            html.P('Identifier')
                            ], width=3),
                    dbc.Col([
                            dbc.Input(
                                    id='input_identifier',
                                    type='text',
                                    placeholder='bus_1',
                                    value='bus_1')
                            ], width=2)
                    ],style={'margin-top': '20px'}),      
                dbc.Row([
                    dbc.Col([
                            html.P('Latitude'),
                            ],width=3),
                    dbc.Col([
                        dbc.Input(
                                id='input_latitude',
                                type='number',
                                placeholder='e.g. 51.090674',
                                value=51.090674)
                        ], width=2)
                    ]),
                dbc.Row([
                    dbc.Col([                 
                            html.P('Longitude')
                            ],width=3),
                    dbc.Col([
                                dbc.Input(
                                id='input_longitude',
                                type='number',
                                placeholder='e.g. 6.496420',
                                value=6.496420)
                            ], width=2)
                    ]),
                dbc.Row([
                    dbc.Col([
                            html.P('Max. radius to weather stations')
                            ], width=3),
                    dbc.Col([
                            dbc.InputGroup([
                                dbc.Input(
                                    id='input_radius_weather_stations',
                                    type='number',
                                    placeholder='e.g. 30',
                                    value=30),
                            dbc.InputGroupText('km')
                            ])
                        ], width=2)
                    ]),
                dbc.Row([
                    dbc.Col([
                            html.P('Thermal Energy Demand')
                            ], width=3),
                    dbc.Col([
                            dbc.InputGroup([
                                dbc.Input(id='input_thermal_energy_demand',
                                    type='number',
                                    placeholder='e.g. 10000 kWh',
                                    value=0),
                                dbc.InputGroupText('kWh')
                            ])      
                            ], width=2)
                    ]),
                dbc.Row([
                    dbc.Col([
                            html.P('Comfort Factor')
                            ],width=3),
                    dbc.Col([
                            dbc.Input(
                                    id='input_comfort_factor',
                                    type='number',
                                    placeholder='e.g. ?',
                                    value=0)
                            ], width=2)
                    ]),
                dbc.Row([
                    dbc.Col([
                            html.P('Daily Vehicle Usage')
                            ],width=3),
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                    id='input_daily_vehicle_usage',
                                    type='number',
                                    placeholder='e.g. 100 km',
                                    value=0),
                            dbc.InputGroupText('km')
                        ])
                    ], width=2)
                    ]),
                dbc.Row([
                    dbc.Col([
                            html.P('Building Type')
                            ], width=3),
                    dbc.Col([
                            dcc.Dropdown( 
                                ['DE_HEF33', 'DE_HEFXYZ'],
                                id='dropwdown_building_type',
                                style={
                                        'color': 'black',
                                        'bgcolor': 'white',
                                        'width': '100%'
                                        },
                                placeholder='Choose a Building Type',
                                value='DE_HEF33')
                            ], width=2)
                    ]),
                dbc.Row([
                    dbc.Col([
                            html.P('T0'),
                            ], width=3),
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id='input_t0',
                                type='number',
                                placeholder='e.g. 20 °C',
                                value=40),
                            dbc.InputGroupText('°C')])
                            ], width=2)
                    ], align='center'),
                    dbc.Row([
                                dbc.Col([
                                    dbc.Button('Submit Settings',
                                               id='submit_user_profile',
                                               color='primary')
                                ])
                            ]),
])



#Callback Section_________________________________________________________________________________________

@callback(
    Output('store_user_profile', 'data'),
    [Input('submit_user_profile', 'n_clicks')],
    [State('input_identifier', 'value'),
     State('input_latitude', 'value'),
     State('input_longitude', 'value'),
     State('input_radius_weather_stations', 'value'),
     State('input_thermal_energy_demand', 'value'),
     State('input_comfort_factor', 'value'),
     State('input_daily_vehicle_usage', 'value'),
     State('dropwdown_building_type', 'value'),
     State('input_t0', 'value')]
)
def update_user_profile(n_clicks, identifier, latitude, longitude, radius_weather_stations,
                        thermal_energy_demand, comfort_factor,
                        daily_vehicle_usage, building_type, t0):
    """
    Update the user profile with the provided information.

    Args:
        n_clicks (int): The number of times the update button is clicked.
        identifier (str): The identifier of the user.
        latitude (float): The latitude of the user's location.
        longitude (float): The longitude of the user's location.
        radius_weather_stations (float): The radius for searching weather stations.
        thermal_energy_demand (float): The thermal energy demand of the user.
        comfort_factor (float): The comfort factor of the user.
        daily_vehicle_usage (float): The daily vehicle usage of the user.
        building_type (str): The type of building the user is in.
        t0 (float): The initial temperature of the user's location.

    Returns:
        dict: A dictionary containing the updated user profile information.

    Raises:
        PreventUpdate: If the update button is clicked but no changes are made.

    """
    if 'submit_user_profile' == ctx.triggered_id and n_clicks is not None:
        data_user_profile = {
            'Identifier': identifier,
            'Latitude': latitude,
            'Longitude': longitude,
            'Radius Weather Stations': radius_weather_stations,
            'Thermal Energy Demand': thermal_energy_demand,
            'Comfort Factor': comfort_factor,
            'Daily Vehicle Usage': daily_vehicle_usage,
            'Building Type': building_type,
            'T0': t0
        }
        return data_user_profile
    elif n_clicks is None:
        raise PreventUpdate