# -*- coding: utf-8 -*-
"""
Info
----
This module defines the layout and callbacks for the bev tab in the GUI.
It contains inputfields for the user to input the max. battery capacity, min. battery capacity, battery usage, charging power, and charging efficiency of the bev.

Functions:
- update_bev_settings: Update bev settings based on user inputs.

The layout is defined using the Dash Bootstrap Components library.
The submitted data is stored in store_bev.

@author: sharth1
"""

from dash import html, Input, Output, State, callback, callback_context as ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

#Layout Section_________________________________________________________________________________________
layout=dbc.Container([
dbc.Row([
                    dbc.Col([
                        html.P('Max. Battery Capacity')
                    ], width=3),
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id='input_bev_max_battery_capacity',
                                type='number',
                                placeholder='e.g. 100 kWh',
                                value=0),
                            dbc.InputGroupText('kWh')
                    ])
                    ], width=2),
                ], style={'margin-top': '20px'}),
                dbc.Row([
                    dbc.Col([
                        html.P('Min. Battery Capacity')
                    ], width=3),
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id='input_bev_min_battery_capacity',
                                type='number',
                                placeholder='e.g. 15 kWh',
                                value=0
                            ),
                            dbc.InputGroupText('kWh')
                    ])
                    ], width=2),
                ]),
                dbc.Row([
                    dbc.Col([
                        html.P('Battery Usage') #TODO: What is this?
                    ], width=3),
                    dbc.Col([
                        dbc.Input(
                            id='input_bev_battery_usage',
                            type='number',
                            placeholder='e.g. ???',
                            value=0
                        )
                    ], width=2),
                ]),
                dbc.Row([
                    dbc.Col([
                        html.P('Charging Power') 
                    ], width=3),
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id='input_bev_charging_power',
                                type='number',
                                placeholder='e.g. 11 kW',
                                value=0
                            ),
                            dbc.InputGroupText('kW')
                           ])
                    ], width=2),
                ]),
                dbc.Row([
                    dbc.Col([
                        html.P('Charging Efficiency') 
                    ], width=3),
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id='input_bev_charging_efficiency',
                                type='number',
                                placeholder='e.g. 90%',
                                value=0
                            ),
                            dbc.InputGroupText('%')
                        ])
                    ], width=2),
                ]),
                dbc.Row([
                                dbc.Col([
                                    dbc.Button('Submit Settings',
                                               id='submit_bev_settings',
                                               color='primary')
                                ])
                            ])

            
])

#Callback Section_________________________________________________________________________________________
@callback(
    Output('store_bev', 'data'),
    [Input('submit_bev_settings', 'n_clicks')],
    [State('input_bev_max_battery_capacity', 'value'),
     State('input_bev_min_battery_capacity', 'value'),
     State('input_bev_battery_usage', 'value'),
     State('input_bev_charging_power', 'value'),
     State('input_bev_charging_efficiency', 'value')],

)
def update_bev_settings(n_clicks, max_battery_capacity, 
                              min_battery_capacity, battery_usage, 
                              charging_power, charging_efficiency):
    """
    Update the BEV (Battery Electric Vehicle) settings based on user inputs.

    Parameters:
    - n_clicks (int): The number of times the submit button is clicked.
    - max_battery_capacity (float): The maximum battery capacity of the BEV.
    - min_battery_capacity (float): The minimum battery capacity of the BEV.
    - battery_usage (float): The battery usage of the BEV.
    - charging_power (float): The charging power of the BEV.
    - charging_efficiency (float): The charging efficiency of the BEV (in percentage).

    Returns:
    - data_bev_settings (dict): A dictionary containing the updated BEV settings.

    Raises:
    - PreventUpdate: If the submit button is not clicked.

    """
    if 'submit_bev_settings' == ctx.triggered_id and n_clicks is not None:
        data_bev_settings = {
            'max_battery_capacity': max_battery_capacity,
            'min_battery_capacity': min_battery_capacity,
            'battery_usage': battery_usage,
            'charging_power': charging_power,
            'charging_efficiency': charging_efficiency / 100
        }
        return data_bev_settings
    
    elif n_clicks is None:
        raise PreventUpdate
