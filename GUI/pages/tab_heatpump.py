from dash import dash, html, dcc
import dash_bootstrap_components as dbc

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
                        placeholder='e.g. Air'
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
                            placeholder='e.g. 20.5 °C'
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
                            placeholder='e.g. 5 kW'
                        ),
                        dbc.InputGroupText('kW')
                    ])
                ], width=2)
            ])
                
])