# -*- coding: utf-8 -*-
"""
Info
----
This module defines the layout and callbacks for the pv tab in the GUI.
It contains inputfields for the user to select the PV module and inverter, and to input the surface tilt, 
surface azimuth, modules per string, and strings per inverter.

Functions:
- update_pv_settings: Update PV settings based on user inputs.


The layout is defined using the Dash Bootstrap Components library.
The submitted data is stored in store_pv.

@author: sharth1
"""
from dash import dcc, html, callback, Input, Output, State, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate

#Layout Section_________________________________________________________________________________________
layout=dbc.Container([
    dbc.Row([
        dbc.Col([
            html.P('Module Library')
        ], width=3),
        dbc.Col([
            dcc.Dropdown(
                id='dropdown_pv_module_library',
                clearable=True,
                style={'color': 'black',
                        'bg-color':'white' 
                        },
                placeholder='e.g. SandiaMod',
                value='SandiaMod',
                options=[
                    {'label': 'SandiaMod', 'value': 'SandiaMod'},
                    {'label': 'CECMod', 'value': 'CECMod'}
                ]
            )
        ], width=2)
    ], style={'margin-top': '20px'}),
    dbc.Row([
        dbc.Col([
            html.P('Module')
        ], width=3),
        dbc.Col([
            dcc.Dropdown(
                id='dropdown_pv_module',
                clearable=True,
                style={'color': 'black'},
                placeholder='e.g. Canadian_Solar_CS5P_220M___2009_',
                value='Canadian_Solar_CS5P_220M___2009_',
                options=[
                    {'label': 'Canadian_Solar_CS5P_220M___2009_', 'value': 'Canadian_Solar_CS5P_220M___2009_'}
                ]
            )
        ], width=2)

    ]),
    dbc.Row([
        dbc.Col([
            html.P('Inverter Library')
        ], width=3),
        dbc.Col([
            dcc.Dropdown(
                id='dropdown_pv_inverter_library',
                clearable=True,
                style={'color': 'black'},
                placeholder='e.g. cecinverter',
                value='cecinverter',
                options=[
                    {'label': 'cecinverter', 'value': 'cecinverter'}
                ]
            )
        ], width=2)
    ]),
    dbc.Row([
        dbc.Col([
            html.P('Inverter')
        ], width=3),
        dbc.Col([
            dcc.Dropdown(
                id='dropdown_pv_inverter',
                clearable=True,
                style={'color': 'black'},
                placeholder='e.g. ABB__MICRO_0_25_I_OUTD_US_208__208V_',
                value='ABB__MICRO_0_25_I_OUTD_US_208__208V_',
                options=[
                    {'label': 'ABB__MICRO_0_25_I_OUTD_US_208__208V_', 'value': 'ABB__MICRO_0_25_I_OUTD_US_208__208V_'}
                ]
            )
        ], width=2)
    ]),
    dbc.Row([
        dbc.Col([
            html.P('Surface Tilt')
        ], width=3),
        dbc.Col([
            dbc.InputGroup([
                dbc.Input(
                    id='input_pv_surface_tilt',
                    type='number',
                    placeholder='e.g. 20°',
                    value=0
                ),
                dbc.InputGroupText('°')
            ])
        ], width=2)
    ]),
    dbc.Row([
        dbc.Col([
            html.P('Surface Azimuth')
        ], width=3),
        dbc.Col([
            dbc.InputGroup([
                dbc.Input(
                    id='input_pv_surface_azimuth',
                    type='number',
                    placeholder='e.g. 200°',
                    value=0
                ),
                dbc.InputGroupText('°')
            ])
        ], width=2)
    ]),
    dbc.Row([
        dbc.Col([
            html.P('Modules per String')
        ], width=3),
        dbc.Col([
            dbc.Input(
                id='input_pv_modules_per_string',
                type='number',
                placeholder='e.g. 6',
                value=0
            )
        ], width=2)
    ]),
    dbc.Row([
        dbc.Col([
            html.P('Strings per Inverter')
        ], width=3),
        dbc.Col([
            dbc.Input(
                id='input_pv_strings_per_inverter',
                type='number',
                placeholder='e.g. 2',
                value=0
            )
        ], width=2)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button('Submit Settings',
                       id='submit_pv_settings',
                       color='primary')
        ])
    ])
])

#Callbacks Section_______________________________________________________________________________________
@callback(
    Output('store_pv', 'data'),
    [Input('submit_pv_settings', 'n_clicks')],
    [State('dropdown_pv_module_library', 'value'),
     State('dropdown_pv_module', 'value'),
     State('dropdown_pv_inverter_library', 'value'),
     State('dropdown_pv_inverter', 'value'),
     State('input_pv_surface_tilt', 'value'),
     State('input_pv_surface_azimuth', 'value'),
     State('input_pv_modules_per_string', 'value'),
     State('input_pv_strings_per_inverter', 'value')]
)
def update_pv_settings(n_clicks, pv_mod_lib, pv_mod, pv_inv_lib, 
                      pv_inv, pv_tilt, pv_azimuth, pv_mod_per_string, 
                      pv_string_per_inv):
    """
    Update PV settings based on user inputs.

    Parameters:
    - n_clicks (int): The number of times the submit button has been clicked.
    - pv_mod_lib (str): The selected PV module library.
    - pv_mod (str): The selected PV module.
    - pv_inv_lib (str): The selected inverter library.
    - pv_inv (str): The selected inverter.
    - pv_tilt (int): The surface tilt angle in degrees.
    - pv_azimuth (int): The surface azimuth angle in degrees.
    - pv_mod_per_string (int): The number of modules per string.
    - pv_string_per_inv (int): The number of strings per inverter.

    Returns:
    - data_pv_settings (dict): A dictionary containing the updated PV settings.
    """
    if 'submit_pv_settings' == ctx.triggered_id and n_clicks is not None:
        data_pv_settings = {
            'PV Module Library': pv_mod_lib,
            'PV Module': pv_mod,
            'PV Inverter Library': pv_inv_lib,
            'PV Inverter': pv_inv,
            'PV Surface Tilt': pv_tilt,
            'PV Surface Azimuth': pv_azimuth,
            'PV Modules per String': pv_mod_per_string,
            'PV Strings per Inverter': pv_string_per_inv
        }
        return data_pv_settings
    elif n_clicks is None:
        raise PreventUpdate