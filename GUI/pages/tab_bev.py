from dash import dash, html, dcc, Input, Output, State, callback, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate

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
                                value=50),
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
                                value=10
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
                            value=1
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
                                value=11
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
                                value=90
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
@callback(
    Output('store_bev', 'data'),
    [Input('submit_bev_settings', 'n_clicks')],
    [State('input_bev_max_battery_capacity', 'value'),
     State('input_bev_min_battery_capacity', 'value'),
     State('input_bev_battery_usage', 'value'),
     State('input_bev_charging_power', 'value'),
     State('input_bev_charging_efficiency', 'value')],

)
def update_bev_settings_store(n_clicks, max_battery_capacity, 
                              min_battery_capacity, battery_usage, 
                              charging_power, charging_efficiency):
    if 'submit_bev_settings' ==ctx.triggered_id and n_clicks is not None:
        data_bev_settings={'max_battery_capacity': max_battery_capacity,
                            'min_battery_capacity': min_battery_capacity,
                            'battery_usage': battery_usage,
                            'charging_power': charging_power,
                            'charging_efficiency': charging_efficiency/100}
        return data_bev_settings
    
    elif n_clicks is None:
        raise PreventUpdate
