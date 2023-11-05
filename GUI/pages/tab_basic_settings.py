from dash import dash, dcc, html
import dash_bootstrap_components as dbc
layout=dbc.Container([ 
     dbc.Row([
                        dbc.Col([
                                html.P('PV Plants')
                            ], width=3),
                        dbc.Col([
                            dbc.Input(
                                id='input_pv_plants',
                                type='number',
                                placeholder='5')
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
                                    placeholder='2'),
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
                                    placeholder='3')
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
                                    placeholder='1'),
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
                                    placeholder='3'),
                                ], width=1)    
                        ],align='center')
                    
])