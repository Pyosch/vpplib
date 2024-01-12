    
from dash import dash, html, dcc, Input, Output, State, callback, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate
import plotly.express as px


# df =pd.read_csv('GUI/df_timeseries.csv', index_col=0)
# df.index.name = 'time'

layout=dbc.Container([
            dbc.Row([
                    dcc.Dropdown(id='dropdown_plot',multi=True,
                                options=[{'label': y, 'value': y} for y in pd.read_csv('GUI/df_timeseries.csv', index_col=0).columns],
                                style={'width': '100%',
                                       'color':'black'},
                                       value=None)
                ]),
            dbc.Row([
                    dcc.Graph(id='graph_timeseries', figure = {}, clickData=None, hoverData=None, 
                            config={'staticPlot': False,
                                    'scrollZoom': True,
                                    'doubleClick': 'reset',
                                    'showTips': True,
                                    'displayModeBar': True,
                                    'watermark': True,
                                    'displaylogo': False,
                                    'toImageButtonOptions': {'format': 'png', 'filename': 'custom_image', 'height': 1080, 'width': 1920, 'scale': 1}})
                ])
    ])


@callback(
    Output('graph_timeseries', 'figure'),
    [Input('dropdown_plot', 'value')]
    )

def build_graph(dropdown_plot):
    fig = px.line(pd.read_csv('GUI/df_timeseries.csv', index_col=0), y=dropdown_plot)
    fig.update_layout(xaxis={'title': 'Time'}, yaxis={'title': 'Power [kW]'},
                      title={'text': 'Time Series'},
                      legend={'title': 'Component'})
    return fig