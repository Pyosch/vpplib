import pandas as pd
from dash import dash, html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc


layout=dbc.Container(id='data_table_basic_settings', children=[])

@callback(
    Output('data_table_basic_settings', 'children'),
    [Input('store_basic_settings', 'data'),
     Input('store_bev', 'data')]
)
def update_table_basic_settings(store_basic_settings, store_bev):
    df_basic_settings= pd.DataFrame(store_basic_settings)
    print(df_basic_settings)

    df_bev=pd.DataFrame(store_bev)
    print(df_bev)
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
    

    table_bev=dash_table.DataTable(data=df_bev.to_dict('records'), 
                        page_action='native',  page_current=0,
                        page_size=20, sort_action='native',
                        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                    'color': 'white', 'textAlign':'center'},
                        style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                    'color': 'white', 'width':'auto'},
                        style_cell={'font-family':'sans-serif'}
    )

    return table_basic_settings, table_bev
