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
     Input('store_storage', 'data')]
)
def update_tables(store_basic_settings, store_environment,store_user_profile, store_bev,   
                  store_pv, store_wind, store_storage):
    df_basic_settings= pd.DataFrame(store_basic_settings)
    df_environment=pd.DataFrame(store_environment)
    df_user_profile=pd.DataFrame(store_user_profile)
    df_bev=pd.DataFrame(store_bev)
    df_pv=pd.DataFrame(store_pv)
    df_wind=pd.DataFrame(store_wind)
    df_storage=pd.DataFrame(store_storage)


    table_basic_settings=dash_table.DataTable(data=df_basic_settings.to_dict('records'), 
                        page_action='native',  page_current=0,
                        page_size=20, sort_action='native',
                        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                    'color': 'white', 'textAlign':'center'},
                        style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                    'color': 'white', 'width':'auto'},
                        style_cell={'font-family':'sans-serif'},
                        style_table={'margin-bottom': '20px'}
    )

    table_environment=dash_table.DataTable(data=df_environment.to_dict('records'), 
                        page_action='native',  page_current=0,
                        page_size=20, sort_action='native',
                        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                    'color': 'white', 'textAlign':'center'},
                        style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                    'color': 'white', 'width':'auto'},
                        style_cell={'font-family':'sans-serif'},
                        style_table={'margin-bottom': '20px'}
    )
    
    table_user_profile=dash_table.DataTable(data=df_user_profile.to_dict('records'),
                        page_action='native',  page_current=0,
                        page_size=20, sort_action='native',
                        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                    'color': 'white', 'textAlign':'center'},
                        style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                    'color': 'white', 'width':'auto'},
                        style_cell={'font-family':'sans-serif'}
    )

    table_bev=dash_table.DataTable(data=df_bev.to_dict('records'), 
                        page_action='native',  page_current=0,
                        page_size=20, sort_action='native',
                        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                    'color': 'white', 'textAlign':'center'},
                        style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                    'color': 'white', 'width':'auto'},
                        style_cell={'font-family':'sans-serif'}
    )
    table_pv=dash_table.DataTable(data=df_pv.to_dict('records'), 
                        page_action='native',  page_current=0,
                        page_size=20, sort_action='native',
                        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                    'color': 'white', 'textAlign':'center'},
                        style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                    'color': 'white', 'width':'auto'},
                        style_cell={'font-family':'sans-serif'}
    )
    table_wind=dash_table.DataTable(data=df_wind.to_dict('records'), 
                        page_action='native',  page_current=0,
                        page_size=20, sort_action='native',
                        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                    'color': 'white', 'textAlign':'center'},
                        style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                    'color': 'white', 'width':'auto'},
                        style_cell={'font-family':'sans-serif'}
    )
    table_storage=dash_table.DataTable(data=df_storage.to_dict('records'), 
                        page_action='native',  page_current=0,
                        page_size=20, sort_action='native',
                        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                    'color': 'white', 'textAlign':'center'},
                        style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                    'color': 'white', 'width':'auto'},
                        style_cell={'font-family':'sans-serif'}
    )

    return table_basic_settings, table_user_profile, table_environment, table_environment, table_bev, table_pv, table_wind, table_storage
