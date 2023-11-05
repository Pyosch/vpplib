from dash import dash, dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd


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
                        ],align='center'),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button('Submit Settings',
                                           id='submit_basic_settings',
                                           color='primary')
                            ])
                        ])
                    
])

# @callback(
#     Output('submit_basic_settings', 'n_clicks'),
#     [Input('submit_basic_settings', 'n_clicks')],
#     [State('input_pv_plants', 'value'),
#      State('input_storage_units', 'value'),
#      State('input_bev_number', 'value'),
#      State('input_hp_number', 'value'),
#      State('input_wind_number', 'value')]
# )
# def update_df(n_clicks, pv_plants, storage_units, bev_number, hp_number, wind_number):
#     global df
#     if n_clicks is not None:
#         df = pd.concat([df, pd.DataFrame({'pv_plants': pv_plants,
#                         'storage_units': storage_units,
#                         'bev_number': bev_number,
#                         'hp_number': hp_number,
#                         'wind_number': wind_number}, index=[0])])
#         print(df)
    # return n_clicks





