from dash import dash, html, dcc
import dash_bootstrap_components as dbc

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
                                placeholder='e.g. 90%'),
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
                                placeholder='e.g. 90%'),
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
                                    placeholder='e.g. 10 kW'),
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
                                    placeholder='e.g. 10 kWh'),
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