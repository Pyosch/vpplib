from dash import dash, html, dcc, Input, Output, State, callback, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate

layout=dbc.Container([
dbc.Row([
                    dbc.Col([
                        html.P('Power Electrolyzer')
                    ], width=3),
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id='input_electrolyzer_power',
                                type='number',
                                placeholder='e.g. 100 kW',
                                value=50),
                            dbc.InputGroupText('kW')
                    ])
                    ], width=2),
                ], style={'margin-top': '20px'}),
                dbc.Row([
                    dbc.Col([
                        html.P('Pressure')
                    ], width=3),
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id='input_electrolyzer_pressure',
                                type='number',
                                placeholder='e.g. 150 bar',
                                value=10
                            ),
                            dbc.InputGroupText('bar')
                    ])
                    ], width=2),
                ]),
                dbc.Row([
                    dbc.Col([
                        html.P('Quantity') 
                    ], width=3),
                    dbc.Col([
                        dbc.Input(
                            id='input_electrolyzer_quantity',
                            type='number',
                            placeholder='e.g. 100 kg',
                            value=5
                        )
                    ], width=2),
                ]),
                dbc.Row([
                                dbc.Col([
                                    dbc.Button('Submit Settings',
                                               id='submit_hydrogen_settings',
                                               color='primary')
                                ])
                            ])

            
])
@callback(
    Output('store_hydrogen', 'data'),
    [Input('submit_hydrogen_settings', 'n_clicks')],
    [State('input_electrolyzer_power', 'value'),
     State('input_electrolyzer_pressure', 'value'),
     State('input_electrolyzer_quantity', 'value')],

)
def update_hydrogen_settings(n_clicks, power, 
                              pressure, quantity):
    if 'submit_hydrogen_settings' ==ctx.triggered_id and n_clicks is not None:
        data_hydrogen_settings={'max_battery_capacity': power,
                            'min_battery_capacity': pressure,
                            'battery_usage': quantity}
        return data_hydrogen_settings
    
    elif n_clicks is None:
        raise PreventUpdate
