# -*- coding: utf-8 -*-
"""
Info
----
This module defines the layout and callbacks for the graphs tab in the GUI.
It contains a dropdown menu for the user to select the data to be plotted and a graph to display the selected data.

The layout is defined using the Dash Bootstrap Components library.
The submitted data is stored in store_graphs.

@author: sharth1
"""

from dash import dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

#Layout Section_________________________________________________________________________________________
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

#Callback Section_________________________________________________________________________________________
@callback(
    Output('graph_timeseries', 'figure'),
    [Input('dropdown_plot', 'value')]
    )

def build_graph(dropdown_plot):
    """
    Build a line graph based on the selected dropdown plot.

    Parameters:
    dropdown_plot (str): The selected dropdown plot.

    Returns:
    fig (plotly.graph_objs._figure.Figure): The generated line graph.
    """
    fig = px.line(pd.read_csv('GUI/df_timeseries.csv', index_col=0), y=dropdown_plot)
    fig.update_layout(xaxis={'title': 'Time'}, yaxis={'title': 'Power [kW]'},
                      title={'text': 'Time Series'},
                      legend={'title': 'Component'})
    return fig