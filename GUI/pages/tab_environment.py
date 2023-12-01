from dash import dash, dcc, html, callback, Input, Output, State, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate

layout=dbc.Container([
dbc.Row([
                            dbc.Col([
                                    html.P('Date Start'),
                                ], width=3),
                            dbc.Col([
                                dbc.Input(
                                        id='input_date_start',
                                        type='date',
                                        style={'width': 'auto'},
                                        value='2015-03-01'
                                        ),
                                ], width= 3)
                            ],align='center', style={'width':'auto', 'margin-top': '20px'}),
                            dbc.Row([
                                dbc.Col([
                                        html.P('Date End')
                                    ],width=3),
                                dbc.Col([
                                    dbc.Input(
                                        id='input_date_end',
                                        type='date',
                                        style={'width': 'auto'},
                                        value='2015-03-01'
                                        )
                                    ], width='auto')
                                ],align='center'),
                            dbc.Row([
                                dbc.Col([
                                        html.P('Time Zone')
                                    ],width=3),
                                dbc.Col([
                                    dcc.Dropdown(
                                        [   'Pacific/Kwajalein UTC-12',
                                            'Pacific/Samo UTC-11',
                                            'Pacific/Honolulu UTC-10',
                                            'America/Anchorage UTC-9',
                                            'America/Los_Angeles UTC-8',
                                            'America/Denver UTC-7',
                                            'America/Chicago UTC-6',
                                            'America/New_York UTC-5',
                                            'America/Caracas UTC-4',
                                            'America/St_Johns UTC-3.5',
                                            'America/Argentina/Buenos_Aires UTC-3s',
                                            'Atlantic/Azores UTC-2',
                                            'Atlantic/Cape_Verde UTC-1',
                                            'Europe/London UTC+0',
                                            'Europe/Berlin UTC+1',
                                            'Europe/Helsinki UTC+2 ',
                                            'Europe/Moscow UTC+3',
                                            'Asia/Dubai UTC+4',
                                            'Asia/Kabul UTC+4.5',
                                            'Asia/Karachi UTC+5',
                                            'Asia/Kathmandu UTC+5.75',
                                            'Asia/Dhaka UTC+6',
                                            'Asia/Jakarta UTC+7',
                                            'Asia/Shanghai UTC+8',
                                            'Asia/Tokyo UTC+9 ',
                                            'Australia/Brisbane UTC+10 ',
                                            'Australia/Sydney UTC+11',
                                            'Pacific/Auckland UTC+12'
                                            ],
                                        id='dropdown_timezone',
                                        style={'width': 'auto', 
                                                'color': 'black',
                                                'bgcolor': 'white',
                                                'width': '2'
                                                },
                                        placeholder='Choose a Timezone',
                                        value='Europe/Berlin UTC+1',
                                        clearable=False
                                        )
                                    ], width='3')
                                ],align='center'),
                            dbc.Row([
                                dbc.Col([
                                        html.P('Time Step')
                                    ],width='3'),
                                dbc.Col([
                                        dcc.Dropdown(
                                            [   '1 min',
                                                '15 min',
                                                '60 min',
                                                '1 day'
                                                ],
                                            id='dropdown_time_step',
                                            style={'width': 'auto', 
                                                    'color': 'black',
                                                    'bgcolor': 'white',
                                                    'width': '3'
                                                    },
                                            placeholder='Choose a Time Step',
                                            value='15 min',
                                            clearable=False
                                            )
                                    ], width=2)
                                ],align='center'),
                           dbc.Row([
                                dbc.Col([
                                    dbc.Button('Submit Settings',
                                               id='submit_environment_settings',
                                               color='primary')
                                ])
                            ])

])                       

@callback(
    Output('store_environment', 'data'),
    [Input('submit_environment_settings', 'n_clicks')],
    [State('input_date_start', 'value'),
     State('input_date_end', 'value'),
     State('dropdown_timezone', 'value'),
     State('dropdown_time_step', 'value')]
)
def update_environment(n_clicks, start_date, end_date, 
                          timezone, timestep):
    if 'submit_environment_settings' == ctx.triggered_id and n_clicks is not None:
        data_environment={'Start Date': start_date,
                            'End Date': end_date,
                            'Time Zone': timezone,
                            'Time Step': timestep
                            }
        return data_environment
    elif n_clicks is None:
        raise PreventUpdate