from dash import dash, dcc, html, callback, Input, Output, State, dash_table, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate


layout=dbc.Container(id='data_table_basic_settings', children=[])

@callback(
    Output('data_table_basic_settings', 'children'),
    [Input('store_basic_settings', 'data'),
     Input('store_environment', 'data'),
     Input('store_user_profile', 'data'),
     Input('store_bev', 'data'),
     Input('store_pv', 'data'),
     Input('store_wind', 'data'),
     Input('store_heatpump', 'data'),
     Input('store_storage', 'data')]
)
def update_tables(store_basic_settings, store_environment, store_user_profile, store_bev,   
                  store_pv, store_wind, store_heatpump, store_storage):

    table_basic_settings=dbc.Container([html.Div(html.H3('Basic Settings')),
    dash_table.DataTable(data=pd.DataFrame(store_basic_settings, index=[0]).to_dict('records'), 
                        page_action='native',  page_current=0,
                        page_size=20, sort_action='native',
                        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                    'color': 'white', 'textAlign':'center'},
                        style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                    'color': 'white', 'width':'auto'},
                        style_cell={'font-family':'sans-serif'},
                        style_table={'margin-bottom': '20px'}
    )])
    table_environment=dbc.Container([html.Div(html.H3('Environment')),
                                     dash_table.DataTable(data=pd.DataFrame(store_environment, index=[0]).to_dict('records'),
                                        page_action='native',  page_current=0,
                                        page_size=20, sort_action='native',
                                        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                                    'color': 'white', 'textAlign':'center'},
                                        style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                                    'color': 'white', 'width':'auto'},
                                        style_cell={'font-family':'sans-serif'},
                                        style_table={'margin-bottom': '20px'}
)]) 
    table_user_profile=dbc.Container([html.Div(html.H3('User Profile')),
                                      dash_table.DataTable(data=pd.DataFrame(store_user_profile, index=[0]).to_dict('records'),
                                        page_action='native',  page_current=0,
                                        page_size=20, sort_action='native',
                                        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                                    'color': 'white', 'textAlign':'center'},
                                        style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                                    'color': 'white', 'width':'auto'},
                                        style_cell={'font-family':'sans-serif'},
                                        style_table={'margin-bottom': '20px'}
    )])
    
    table_bev=dbc.Container([html.Div(html.H3('BEV')),
                             dash_table.DataTable(data=pd.DataFrame(store_bev, index=[0]).to_dict('records'), 
                                page_action='native',  page_current=0,
                                page_size=20, sort_action='native',
                                style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                            'color': 'white', 'textAlign':'center'},
                                style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                            'color': 'white', 'width':'auto'},
                                style_cell={'font-family':'sans-serif'},
                                style_table={'margin-bottom': '20px'}
    )])
    table_pv=dbc.Container([html.Div(html.H3('Photovoltaic')),
                            dash_table.DataTable(data=pd.DataFrame(store_pv, index=[0]).to_dict('records'), 
                                page_action='native',  page_current=0,
                                page_size=20, sort_action='native',
                                style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                            'color': 'white', 'textAlign':'center'},
                                style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                            'color': 'white', 'width':'auto'},
                                style_cell={'font-family':'sans-serif'},
                                style_table={'margin-bottom': '20px'}
    )])
    table_wind=dbc.Container([html.Div(html.H3('Wind')),
                              dash_table.DataTable(data=pd.DataFrame(store_wind, index=[0]).to_dict('records'), 
                                page_action='native',  page_current=0,
                                page_size=20, sort_action='native',
                                style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                            'color': 'white', 'textAlign':'center'},
                                style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                            'color': 'white', 'width':'auto'},
                                style_cell={'font-family':'sans-serif'},
                                style_table={'margin-bottom': '20px'}
    )])
    table_heatpump=dbc.Container([html.Div(html.H3('Heatpump')),
                                  dash_table.DataTable(data=pd.DataFrame(store_heatpump, index=[0]).to_dict('records'), 
                                    page_action='native',  page_current=0,
                                    page_size=20, sort_action='native',
                                    style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                                'color': 'white', 'textAlign':'center'},
                                    style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                                'color': 'white', 'width':'auto'},
                                    style_cell={'font-family':'sans-serif'},
                                    style_table={'margin-bottom': '20px'}
    )])
    table_storage=dbc.Container([html.Div(html.H3('Storage')),
                                 dash_table.DataTable(data=pd.DataFrame(store_storage, index=[0]).to_dict('records'), 
                                    page_action='native',  page_current=0,
                                    page_size=20, sort_action='native',
                                    style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                                'color': 'white', 'textAlign':'center'},
                                    style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                                'color': 'white', 'width':'auto'},
                                    style_cell={'font-family':'sans-serif'},
                                    style_table={'margin-bottom': '20px'}
    )])

    return table_basic_settings, table_user_profile, table_environment, table_bev, table_pv, table_wind, table_heatpump, table_storage
