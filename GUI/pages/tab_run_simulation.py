from dash import dash, dcc, html, callback, Input, Output, State, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate
from basic_simulation import simulation
import os
import time


parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

layout=dbc.Container([
    dbc.Row([
             dbc.Button('Simulate',
                        id='simulate_button',
                        color='primary',
                        size='sm',),
            html.Div(id='output_simulate_button', children=[])
    ], style={'margin-top': '20px'}),
    dbc.Row([
             dbc.Button('Download Results',
                        id='download_button',
                        color='primary',
                        size='sm',),
            
    ], style={'margin-top': '20px'}),
    dbc.Row([
        dcc.Loading(id='is-loading', children=[html.Div(id='is-loading-output')], type='circle')
        
    ]),
    dcc.Download(id="download-time-series"),
])

@callback(
    Output('is-loading-output', 'children'),
    [Input('simulate_button', 'n_clicks'),
     Input('store_basic_settings', 'data'),
     Input('store_environment', 'data'),
     Input('store_user_profile', 'data'),
     Input('store_bev', 'data'),
     Input('store_pv', 'data'),
     Input('store_wind', 'data'),
     Input('store_heatpump', 'data'),
     Input('store_storage', 'data')],

)
def simulate(n_clicks, store_basic_settings, store_environment, store_user_profile, store_bev,
               store_pv, store_wind, store_heatpump, store_storage):
    if 'simulate_button' == ctx.triggered_id and n_clicks is not None:
        print('simulating')
        simulation(store_basic_settings, store_environment, store_user_profile, store_bev,
               store_pv, store_wind, store_heatpump, store_storage)
        print('done')
        time.sleep(1)
    else:
        raise PreventUpdate



@callback(
    Output("download-time-series", "data"),
    Input("download_button", "n_clicks"),
)
def download(n_clicks):
    if 'download_button' == ctx.triggered_id and n_clicks is not None:
        print('downloading')
        return dcc.send_file("df_timeseries.csv")
    else:
        raise PreventUpdate