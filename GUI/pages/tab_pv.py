from dash import dash, html, dcc
import dash_bootstrap_components as dbc

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
                            placeholder='e.g. Canadian_Solar_CS5P_220M___2009_'
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
                        placeholder='e.g. cecinverter'
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
                            placeholder='e.g. ABB__MICRO_0_25_I_OUTD_US_208__208V_'
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
                                placeholder='e.g. 20°'
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
                                placeholder='e.g. 200°'
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
                            placeholder='e.g. 6'
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
                            placeholder='e.g. 2'
                        )
                    ], width=2)
                ])
               
])

