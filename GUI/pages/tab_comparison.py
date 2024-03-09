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

from dash import  dcc, Input, Output, callback, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate

import plotly.express as px


#create new dfs
    # df_hydrogen_forecast = pd.read_csv('GUI/03.03_13.03_Simu_Hydrogen_forecast.csv', index_col=0)

df_vpp_forecast = pd.read_csv('GUI/03.03-13.03_Simu_VPP_forecast.csv', index_col=0).sum(axis=1)
# df_hydrogen_historical = pd.read_csv('GUI/03.03_08.03_Simu_Hydrogen_historical_timeseries.csv', index_col=0)
df_vpp_historical = pd.read_csv('GUI/03.03-08.03_Simu_VPP_historical_timeseries.csv', index_col=0).sum(axis=1)

df_vpp_diff = df_vpp_forecast - df_vpp_historical
# df_hydrogen_diff = df_hydrogen_forecast - df_hydrogen_historical
df_combined = pd.concat([df_vpp_forecast, df_vpp_historical, df_vpp_diff], axis=1)
df_combined.columns = ['VPP Forecast', 'VPP Historical', 'VPP Difference']





#Layout Section_________________________________________________________________________________________
layout=dbc.Container([
            dbc.Row([
                dcc.Dropdown(id='dropdown_plot',multi=True,
                                options=[{'label': y, 'value': y} for y in df_combined],
                                style={'width': '100%',
                                       'color':'black'},
                                       value=None),
                    dcc.Graph(id='graph_timeseries_compare', figure = {}, clickData=None, hoverData=None, 
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
    Output('graph_timeseries_compare', 'figure'),
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

    if dropdown_plot is None:
        raise PreventUpdate

    fig = px.line(df_combined, y=dropdown_plot)
    if dropdown_plot == 'VPP Difference':
            fig.add_trace(px.area(df_combined, y='VPP Difference'))
    fig.update_layout(xaxis={'title': 'Time'}, yaxis={'title': 'Power [kW]'},
                      title={'text': 'Power profile'},
                      legend={'title': 'Component'})
    return fig
