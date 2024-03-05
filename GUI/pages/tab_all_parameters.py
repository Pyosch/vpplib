# -*- coding: utf-8 -*-
"""
Info
----
This module defines the layout and callbacks for the data table settings tab in the GUI.
It contains tables to display the user inputs for the basic settings, environment, user profile, bev, pv, wind, heatpump, storage, and hydrogen.

Functions:
- update_tables: Update the tables with the given data.

The layout is defined using the Dash Bootstrap Components library.
The  data is taken from store_basic_settings, store_environment, store_user_profile, store_bev, store_pv, store_wind, store_heatpump, store_storage, and store_hydrogen.

@author: sharth1
"""

from dash import html, callback, Input, Output, State, dash_table, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd

#Layout Section_________________________________________________________________________________________
layout=dbc.Container(id='data_table_settings', children=[])

#Callback Section_________________________________________________________________________________________
@callback(
    Output('data_table_settings', 'children'),
    [Input('store_basic_settings', 'data'),
     Input('store_environment', 'data'),
     Input('store_user_profile', 'data'),
     Input('store_bev', 'data'),
     Input('store_pv', 'data'),
     Input('store_wind', 'data'),
     Input('store_heatpump', 'data'),
     Input('store_storage', 'data'),
     Input('store_hydrogen', 'data')]
)

def update_tables(store_basic_settings, store_environment, store_user_profile, store_bev,   
                  store_pv, store_wind, store_heatpump, store_storage, store_hydrogen):
    """
    Update the tables with the given data.

    Args:
        store_basic_settings (list): List of dictionaries containing data for basic settings.
        store_environment (list): List of dictionaries containing data for environment.
        store_user_profile (list): List of dictionaries containing data for user profile.
        store_bev (list): List of dictionaries containing data for BEV.
        store_pv (list): List of dictionaries containing data for Photovoltaic.
        store_wind (list): List of dictionaries containing data for Wind.
        store_heatpump (list): List of dictionaries containing data for Heatpump.
        store_storage (list): List of dictionaries containing data for Storage.
        store_hydrogen (list): List of dictionaries containing data for Hydrogen.

    Returns:
        tuple: A tuple containing the updated tables for basic settings, user profile, environment, BEV, Photovoltaic, Wind, Heatpump, Storage, and Hydrogen.
    """

    table_basic_settings=dbc.Container([html.Div(html.H3('Basic Settings')),
    dash_table.DataTable(data=pd.DataFrame(store_basic_settings, index=[0]).to_dict('records'), 
                        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                    'color': 'white', 'textAlign':'center'},
                        style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                    'color': 'white', 'width':'auto'},
                        style_cell={'font-family':'sans-serif'},
                        style_table={'margin-bottom': '20px'}
    )])
    table_environment=dbc.Container([html.Div(html.H3('Environment')),
                                     dash_table.DataTable(data=pd.DataFrame(store_environment, index=[0]).to_dict('records'),
                                        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                                    'color': 'white', 'textAlign':'center'},
                                        style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                                    'color': 'white', 'width':'auto'},
                                        style_cell={'font-family':'sans-serif'},
                                        style_table={'margin-bottom': '20px'}
)]) 
    table_user_profile=dbc.Container([html.Div(html.H3('User Profile')),
                                      dash_table.DataTable(data=pd.DataFrame(store_user_profile, index=[0]).to_dict('records'),
                                        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                                    'color': 'white', 'textAlign':'center'},
                                        style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                                    'color': 'white', 'width':'auto'},
                                        style_cell={'font-family':'sans-serif'},
                                        style_table={'margin-bottom': '20px'}
    )])
    
    table_bev=dbc.Container([html.Div(html.H3('BEV')),
                             dash_table.DataTable(data=pd.DataFrame(store_bev, index=[0]).to_dict('records'), 
                                style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                            'color': 'white', 'textAlign':'center'},
                                style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                            'color': 'white', 'width':'auto'},
                                style_cell={'font-family':'sans-serif'},
                                style_table={'margin-bottom': '20px'}
    )])
    table_pv=dbc.Container([html.Div(html.H3('Photovoltaic')),
                            dash_table.DataTable(data=pd.DataFrame(store_pv, index=[0]).to_dict('records'), 
                                style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                            'color': 'white', 'textAlign':'center'},
                                style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                            'color': 'white', 'width':'auto'},
                                style_cell={'font-family':'sans-serif'},
                                style_table={'margin-bottom': '20px'}
    )])
    table_wind=dbc.Container([html.Div(html.H3('Wind')),
                              dash_table.DataTable(data=pd.DataFrame(store_wind, index=[0]).to_dict('records'), 
                                style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                            'color': 'white', 'textAlign':'center'},
                                style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                            'color': 'white', 'width':'auto'},
                                style_cell={'font-family':'sans-serif'},
                                style_table={'margin-bottom': '20px'}
    )])
    table_heatpump=dbc.Container([html.Div(html.H3('Heatpump')),
                                  dash_table.DataTable(data=pd.DataFrame(store_heatpump, index=[0]).to_dict('records'), 
                                    style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                                'color': 'white', 'textAlign':'center'},
                                    style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                                'color': 'white', 'width':'auto'},
                                    style_cell={'font-family':'sans-serif'},
                                    style_table={'margin-bottom': '20px'}
    )])
    table_storage=dbc.Container([html.Div(html.H3('Storage')),
                                 dash_table.DataTable(data=pd.DataFrame(store_storage, index=[0]).to_dict('records'), 
                                    style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                                'color': 'white', 'textAlign':'center'},
                                    style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                                'color': 'white', 'width':'auto'},
                                    style_cell={'font-family':'sans-serif'},
                                    style_table={'margin-bottom': '20px'}
    )])
    table_hydrogen=dbc.Container([html.Div(html.H3('Hydrogen')),
                                  dash_table.DataTable(data=pd.DataFrame(store_hydrogen, index=[0]).to_dict('records'), 
                                    style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                                'color': 'white', 'textAlign':'center'},
                                    style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                                'color': 'white', 'width':'auto'},
                                    style_cell={'font-family':'sans-serif'},
                                    style_table={'margin-bottom': '20px'}
    )])

    return table_basic_settings, table_user_profile, table_environment, table_bev, table_pv, table_wind, table_heatpump, table_storage, table_hydrogen
