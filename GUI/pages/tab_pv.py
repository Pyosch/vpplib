from dash import dash, dcc, html, callback, Input, Output, State, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate
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
                                value=20
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
                                value=200
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
                            value=6
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
                            value=2
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
def update_pv_settings_store(n_clicks, pv_mod_lib, pv_mod, pv_inv_lib, 
                                pv_inv, pv_tilt, pv_azimuth, pv_mod_per_string, 
                                pv_string_per_inv):
    if 'submit_pv_settings' ==ctx.triggered_id and n_clicks is not None:
        data_pv_settings={'PV Module Library':pv_mod_lib,
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