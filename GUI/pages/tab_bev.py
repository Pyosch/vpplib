from dash import dash, html, dcc
import dash_bootstrap_components as dbc

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
                                placeholder='e.g. 100 kWh'),
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
                                placeholder='e.g. 15 kWh'
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
                            placeholder='e.g. ???'
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
                                placeholder='e.g. 11 kW'
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
                                placeholder='e.g. 90%'
                            ),
                            dbc.InputGroupText('%')
                        ])
                    ], width=2),
                ])
            
])