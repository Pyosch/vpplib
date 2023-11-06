from dash import dash, html, dcc
import dash_bootstrap_components as dbc
layout=dbc.Container([
dbc.Row([
                    dbc.Col([
                            html.P('Identifier')
                            ], width=3),
                    dbc.Col([
                            dbc.Input(
                                    id='input_identifier',
                                    type='text',
                                    placeholder='bus 1')
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
                                placeholder='e.g. 50.7498321')
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
                                placeholder='e.g. 6.473982')
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
                                    placeholder='e.g. 10000 kWh'),
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
                                    placeholder='e.g. ?')
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
                                    placeholder='e.g. 100 km'),
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
                                placeholder='Choose a Building Type')
                            ], width=3)
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
                                placeholder='e.g. 20 °C'),
                            dbc.InputGroupText('°C')])
                            ], width=2)
                    ], align='center'),
                dbc.Row([
                    dbc.Col([
                                html.P('Upload Base Load')   
                            ], width=3),
                    dbc.Col([
                        dcc.Upload(
                            id='upload_base_load',
                            children=dbc.Container([
                                'Drag and Drop or ',
                                html.A('Select Files')
                            ]),style={
                                'height': 'auto',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'textAlign': 'center',
                                'margin': '10px',
                            })
                        ], width=3)
                    ], align='center'),
                    dbc.Row([
                                dbc.Col([
                                    dbc.Button('Submit Settings',
                                               id='submit_user_profile',
                                               color='primary')
                                ])
                            ])
                
])