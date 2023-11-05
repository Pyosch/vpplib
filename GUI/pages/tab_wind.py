from dash import dash, html, dcc
import dash_bootstrap_components as dbc

layout=dbc.Container([
        dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader('Wind Turbine Data', 
                                               style={'font-weight': 'bold'}),
                                dbc.CardBody([
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Turbine Type')
                                        ], width=3),
                                        dbc.Col([
                                            dbc.Input(
                                                id='input_wind_turbine_type',
                                                type='text',
                                                placeholder='e.g. E-126/4200',
                                            )
                                        ], width=4),
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Hub Height')
                                        ], width=3),
                                        dbc.Col([
                                            dbc.InputGroup([
                                                dbc.Input(
                                                    id='input_wind_hub_height',
                                                    type='number',
                                                    placeholder='e.g. 135 m'
                                                ),
                                                dbc.InputGroupText('m')
                                            ])
                                        ],width=4)                                    
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Rotor Diameter')
                                        ], width=3),
                                        dbc.Col([
                                            dbc.InputGroup([
                                                dbc.Input(
                                                    id='input_wind_rotor_diameter',
                                                    type='number',
                                                    placeholder='e.g. 127 m'
                                                ),
                                                dbc.InputGroupText('m')
                                            ])
                                        ], width=4)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Comfort Factor')
                                        ], width=3),
                                        dbc.Col([
                                            dbc.Input( #TODO: What is this? Compare with Screeenshot
                                                id='input_wind_comfort_factor',
                                                type='number',
                                                placeholder='e.g. 0.9'
                                            )
                                        ], width=4)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Data source')
                                        ], width=3),
                                        dbc.Col([
                                            dcc.Dropdown(
                                                ['oedb', 'xyz'],
                                                id='dropdown_wind_data_source',
                                                clearable=True,
                                                style={
                                                       'color': 'black',
                                                       'bgcolor': 'white',
                                                       },
                                                placeholder='e.g. WindTurbines',
                                            )
                                        ], width =4)
                                    ])
                                ])
                            ])
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader('Wind Power Model Chain Data',
                                               style={'font-weight': 'bold'}),
                                dbc.CardBody([
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Wind Speed Model')
                                        ], width = 4),
                                        dbc.Col([
                                            dcc.Dropdown(
                                                ['logarithmic', 'hellman', 'interpolation_extrapolation'],
                                                id='dropdown_wind_speed_model',
                                                clearable=True,
                                                style={'color': 'black',
                                                       'bgcolor': 'white',
                                                       },
                                                placeholder='e.g. logarithmic',
                                            )
                                        ], width=4)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Density Model')
                                        ], width=4),
                                        dbc.Col([
                                            dcc.Dropdown(
                                                ['barometric', 'ideal gas', 'interpolation_extrapolation'],
                                                id='dropdown_wind_density_model',
                                                clearable=True,
                                                style={'color': 'black',
                                                       'bgcolor': 'white',
                                                       },
                                                placeholder='e.g. barometric',
                                            )
                                        ], width=4)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Temperature Model')
                                        ], width=4),
                                        dbc.Col([
                                            dcc.Dropdown(
                                                ['linear gradient', 'interpolation extrapolation'],
                                                id='dropdown_wind_temperature_model',
                                                clearable=True,
                                                style={'color': 'black',
                                                       'bgcolor': 'white',
                                                       },
                                                placeholder='e.g. linear gradient',
                                            )
                                        ], width=4)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Power Output Model')
                                        ], width=4),
                                        dbc.Col([
                                            dcc.Dropdown(
                                                ['power curve', 'power coefficient curve'],
                                                id='dropdown_wind_power_output_model',
                                                clearable=True,
                                                style={'color': 'black',
                                                       'bgcolor': 'white',
                                                       },
                                                placeholder='power curve',
                                            )
                                        ], width=4)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Density Correction', style={'margin-top': '10%'})
                                        ], width=4),
                                        dbc.Col([
                                            dbc.Switch(
                                                id='switch_wind_density_correction',
                                                style={'width': 'auto', 'margin-top': '5%'},
                                            )
                                        ])
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Obstacle Height')
                                        ], width=4),
                                        dbc.Col([
                                            dbc.InputGroup([
                                                dbc.Input(
                                                    id='input_wind_obstacle_height',
                                                    type='number',
                                                    placeholder='e.g. 0 m'
                                                ),
                                                dbc.InputGroupText('m')
                                            ])
                                        ], width=4)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Hellmann Exponent')
                                        ], width=4),
                                        dbc.Col([
                                            dbc.Input( 
                                                id='input_hellmann_exponent',
                                                type='text',
                                                placeholder='e.g. 0.2'
                                            )
                                        ], width=4)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Upload Wind Data', style={'margin-top': '15%'})
                                        ], width=4),
                                        dbc.Col([
                                            dcc.Upload(
                                                id='upload_wind_data',
                                                style={'width': 'auto',
                                                    'height': 'auto',
                                                    'lineHeight': '60px',
                                                    'borderWidth': '1px',
                                                    'borderStyle': 'dashed',
                                                    'textAlign': 'center',
                                                    'margin': '10px'
                                                },
                                                children=dbc.Container([
                                                    'Drag and Drop or ',
                                                    html.A('Select Files')
                                                ]),
                                            )
                                        ])
                                    ])
                                ])
                            ])
                        ])
                    ], style={'margin-top': '20px'}),
               
])