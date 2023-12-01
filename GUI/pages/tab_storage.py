from dash import dash, dcc, html, callback, Input, Output, State, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate

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
                                placeholder='e.g. 90%',
                                value=90),
                                
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
                                placeholder='e.g. 90%',
                                value=90),
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
                                    placeholder='e.g. 10 kW',
                                    value=10),
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
                                    placeholder='e.g. 10 kWh',
                                    value=10),
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

@callback(
    Output('store_storage', 'data'),
    [Input('submit_storage_settings', 'n_clicks')],
    [State('input_storage_charge_efficiency', 'value'),
     State('input_storage_discharge_efficiency', 'value'),
     State('input_storage_max_power', 'value'),
     State('input_storage_max_capacity', 'value')]
)
def update_storage(n_clicks, storage_charge_effciency, storage_discharge_efficiency, 
                                storage_max_power, storage_max_capacity):
    
    if 'submit_storage_settings' ==ctx.triggered_id and n_clicks is not None:

        data_storage_settings={'Charging Efficiency': storage_charge_effciency,
                 'Discharging Efficiency': storage_discharge_efficiency/100,
                 'Max. Power': storage_max_power/100,
                 'Max. Capacity': storage_max_capacity}
        
        return data_storage_settings
    
    elif n_clicks is None:
        raise PreventUpdate