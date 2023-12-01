from dash import dash, dcc, html, callback, Input, Output, State, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate

layout=dbc.Container([
dbc.Row([
                dbc.Col([
                    html.P('Type of Heat Pump')
                ], width=3),
                dbc.Col([
                    dcc.Dropdown(
                        ['Air', 'Ground'],
                        id='dropdown_heatpump_type',
                        style={'width': '100%',
                                'color': 'black',
                                'bgcolor': 'white',
                                },
                        placeholder='e.g. Air',
                        value='Air'
                    )
                ], width=2)
            ], style={'margin-top': '20px'}),
            dbc.Row([
                dbc.Col([
                    html.P('Heat System Temperature')
                ], width=3),
                dbc.Col([
                    dbc.InputGroup([
                        dbc.Input(
                            id='input_heatpump_system_temperature',
                            type='number',
                            placeholder='e.g. 20.5 °C',
                            value=60
                        ),
                        dbc.InputGroupText('°C')
                    ])
                ], width=2)
            ]),
            dbc.Row([
                dbc.Col([
                    html.P('Electrical Power')
                    ], width=3),
                dbc.Col([
                    dbc.InputGroup([
                        dbc.Input(
                            id='input_heatpump_electrical_power',
                            type='number',
                            placeholder='e.g. 5 kW',
                            value= 5
                        ),
                        dbc.InputGroupText('kW')
                    ])
                ], width=2)
            ]),
            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Submit Settings',
                                               id='submit_hp_settings',
                                               color='primary')
                                ])
                            ])
                
])

@callback(
    Output('store_heatpump', 'data'),
    [Input('submit_hp_settings', 'n_clicks')],
    [State('dropdown_heatpump_type', 'value'),
     State('input_heatpump_system_temperature', 'value'),
     State('input_heatpump_electrical_power', 'value')]
)
def update_basic_settings_store(n_clicks, type_hp, temp_hp, power_hp):
    if 'submit_hp_settings' ==ctx.triggered_id and n_clicks is not None:
        data_heatpump={'Type Heatpump': type_hp,
                 'Heat System Temperature': temp_hp,
                 'Power': power_hp,}
        return data_heatpump
    elif n_clicks is None:
        raise PreventUpdate
