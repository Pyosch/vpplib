from dash import dash, dcc, html, callback, Input, Output, State, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate
import dash_daq as daq

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
                            ],style={'margin-top': '20px'}),
                            dbc.Row([
                                dbc.Col([
                                        html.P('Date End')
                                    ],width=3),
                                dbc.Col([
                                    dbc.Input(
                                        id='input_date_end',
                                        type='date',
                                        style={'width': 'auto'},
                                        value='2015-03-02'
                                        )
                                    ], width='auto')
                                ]),
                            dbc.Row([
                                        dbc.Col([
                                            html.P('Force End Time')
                                        ], width=3),
                                        dbc.Col([
                                            daq.BooleanSwitch(
                                                id='force_end_time',
                                                style={'width': 'auto'},
                                                on=True
                                            )
                                        ], style={'margin-top': '5px'}, width=1)
                                    ]),
                            dbc.Row([
                                dbc.Col([
                                        html.P('Time Zone')
                                    ],width=3),
                                dbc.Col([
                                    dcc.Dropdown([   
                                            {'label':'Pacific/Kwajalein', 'value':'Pacific/Kwajalein'},
                                            {'label':'Pacific/Samoan', 'value':'Pacific/Samoan', 'disabled':True},
                                            {'label':'Pacific/Honolulu', 'value':'Pacific/Honolulu', 'disabled':True},
                                            {'label':'America/Anchorage', 'value':'America/Anchorage', 'disabled':True},
                                            {'label':'America/Los_Angeles', 'value':'America/Los_Angeles', 'disabled':True},
                                            {'label':'America/Phoenix', 'value':'America/Phoenix', 'disabled':True},
                                            {'label':'America/Chicago', 'value':'America/Chicago', 'disabled':True},
                                            {'label':'America/New_York', 'value':'America/New_York', 'disabled':True},
                                            {'label':'America/Argentina/Buenos_Aires', 'value':'America/Argentina/Buenos_Aires', 'disabled':True},                                      
                                            {'label':'Atlantic/Cape_Verde', 'value':'Atlantic/Cape_Verde', 'disabled':True},
                                            {'label':'Europe/London', 'value':'Europe/London', 'disabled':True},
                                            {'label':'Europe/Berlin', 'value':'Europe/Berlin', 'disabled':False},
                                            {'label':'Europe/Helsinki', 'value':'Europe/Helsinki', 'disabled':True},
                                            {'label':'Europe/Moscow', 'value':'Europe/Moscow', 'disabled':True},
                                            {'label':'Asia/Dubai', 'value':'Asia/Dubai', 'disabled':True},
                                            {'label':'Asia/Kabul', 'value':'Asia/Kabul', 'disabled':True},
                                            {'label':'Asia/Karachi', 'value':'Asia/Karachi', 'disabled':True},
                                            {'label':'Asia/Kathmandu', 'value':'Asia/Kathmandu', 'disabled':True},
                                            {'label':'Asia/Dhaka', 'value':'Asia/Dhaka', 'disabled':True},
                                            {'label':'Asia/Jakarta', 'value':'Asia/Jakarta', 'disabled':True},
                                            {'label':'Asia/Shanghai', 'value':'Asia/Shanghai', 'disabled':True},
                                            {'label':'Asia/Tokyo', 'value':'Asia/Tokyo', 'disabled':True},
                                            {'label':'Australia/Brisbane', 'value':'Australia/Brisbane', 'disabled':True},
                                            {'label':'Australia/Sydney', 'value':'Australia/Sydney', 'disabled':True},
                                            {'label':'Pacific/Auckland', 'value':'Pacific/Auckland', 'disabled':True}
                                            ],
                                        id='dropdown_timezone',
                                        style={'width': 'auto', 
                                                'color': 'black',
                                                'bgcolor': 'white',
                                                'width': '2'
                                                },
                                        placeholder='Choose a Timezone',
                                        value='Europe/Berlin',
                                        clearable=False
                                        )
                                    ], width=3)
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
                            ]),
                            html.Div(id='force_end_time_output')

])                       

@callback(
        Output('force_end_time_output', 'children'),
        [Input('force_end_time', 'on')]
        )

def switch_force_end_time(on):
    return on

    
@callback(
    Output('store_environment', 'data'),
    [Input('submit_environment_settings', 'n_clicks')],
    [State('input_date_start', 'value'),
     State('input_date_end', 'value'),
     State('dropdown_timezone', 'value'),
     State('dropdown_time_step', 'value'),
     State('force_end_time', 'on')]
)
def update_environment_settings(n_clicks, start_date, end_date, 
                          timezone, timestep, on):
    if 'submit_environment_settings' == ctx.triggered_id and n_clicks is not None:
        data_environment={'Start Date': start_date + ' 00:00:00',
                            'End Date': end_date + ' 00:00:00',
                            'Time Zone': timezone,
                            'Time Step': timestep,
                            'Force End Time': on

                            }
        return data_environment
    elif n_clicks is None:
        raise PreventUpdate