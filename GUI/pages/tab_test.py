from dash import dash, dcc, html, callback, Input, Output, State, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate
import basebase__scenario

layout=dbc.Container([
    dbc.Row([
             dbc.Button('Simulate',
                        id='simulate_button',
                        color='primary'),
            html.Div(id='output_simulate_button', children=[])
    ])
])

@callback(
    Output('output_simulate_button', 'children'),
    [Input('simulate_button', 'n_clicks'),
     Input('store_basic_settings', 'data'),
     Input('store_environment', 'data'),
     Input('store_user_profile', 'data'),
     Input('store_bev', 'data'),
     Input('store_pv', 'data'),
     Input('store_wind', 'data'),
     Input('store_heatpump', 'data'),
     Input('store_storage', 'data'),
     ]
)
def simulate(n_clicks, store_basic_settings, store_environment, store_user_profile, store_bev, 
                    store_pv, store_wind, store_heatpump, store_storage):
    if 'simulate_button' == ctx.triggered_id and n_clicks is not None:
        start_date=store_environment['Start Date']
        end_date=store_environment['End Date']
        time_zone=store_environment['Time Zone']
        time_freq=store_environment['Time Step']
        basebase__scenario.simulation(start_date, end_date, time_zone, time_freq)
        df=pd.read_csv('input/df_timeseries.csv')
        print(df)
    else:
        raise PreventUpdate