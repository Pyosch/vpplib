import pandas as pd
from dash import dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc


layout=dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Button('Submit Settings', 
                       id='store_button', 
                       color='primary',)
        ])
    ]),
    dbc.Container(id='store_button')
])

# @callback(
#     Output('store_button', 'children'),
#     [Input('store_button', 'n_clicks')],
#     [State('input_pv_plants', 'value'),
#      State('input_storage_units', 'value'),
#      State('input_bev_number', 'value'),
#      State('input_hp_number', 'value'),
#      State('input_wind_number', 'value')]
# )

# def store_settings(n_clicks, pv_plants, storage_units, bev_number, hp_number, wind_number):
#     if n_clicks is None:
#         raise dash.exceptions.PreventUpdate
#     else:
#         df=pd.DataFrame()
#         df['PV Plants']=[pv_plants]
#         df['Storage Units']=[storage_units]
#         df['BEV Number']=[bev_number]
#         df['Heat Pump Number']=[hp_number]
#         df['Wind Number']=[wind_number]
#         print(df)
#         return df.to_json(date_format='iso', orient='split')
