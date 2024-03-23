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

from dash import dcc, Input, Output, callback, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import time
from dash.exceptions import PreventUpdate

#Layout Section_________________________________________________________________________________________
layout=dbc.Container([
            dbc.Row([
                html.H2('Generation Time Series'),
                    dcc.Dropdown(id='dropdown_plot',multi=True,
                                options=[{'label': y, 'value': y} for y in pd.read_csv('GUI/csv-files/df_timeseries.csv', index_col=0).columns],
                                style={'width': '100%',
                                       'color':'black'},
                                       value=None)
                ], style={'margin-bottom': '20px',
                          'margin-top': '10px'}),
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
                ], style={'margin-bottom': '30px'}),
            dbc.Row([
                html.H2('Power curve of electrolyzer'),
                    dcc.Dropdown(id='dropdown_power_hydrogen',multi=True, 
                                 options=[{'label':'P_ac', 
                                           'value':'P_ac'},
                                           {'label':'P_in without losses [KW]', 
                                            'value':'P_in without losses [KW]'},
                                           {'label':'surplus electricity [kW]', 
                                            'value':'surplus electricity [kW]'},
                                           {'label':'P_in [KW]', 
                                            'value':'P_in [KW]'}
                                 ],
                                style={'width': '100%',
                                       'color':'black'},
                                       value=None)
                        ], style={'margin-bottom': '20px',
                                  'margin-top': '10px'}),
                dbc.Row([
                    dcc.Graph(id='graph_power_hydrogen', figure = {}, clickData=None, hoverData=None, 
                            config={'staticPlot': False,
                                    'scrollZoom': True,
                                    'doubleClick': 'reset',
                                    'showTips': True,
                                    'displayModeBar': True,
                                    'watermark': True,
                                    'displaylogo': False,
                                    'toImageButtonOptions': {'format': 'png', 'filename': 'custom_image', 'height': 1080, 'width': 1920, 'scale': 1}})
                ], style={'margin-bottom': '30px',}),

                dbc.Row([
                    html.H2('Quantities of products of elctrolysis'),
                    dcc.Dropdown(id='dropdown_quantities_hydrogen',multi=True, 
                                 options=[{'label':'hydrogen production [Kg/dt]', 
                                           'value':'hydrogen production [Kg/dt]'},
                                           {'label':'H20 [kg/dt]', 
                                            'value':'H20 [kg/dt]'},
                                           {'label':'Oxygen [kg/dt]', 
                                            'value':'Oxygen [kg/dt]'},
                                           {'label':'cooling Water [kg/dt]', 
                                            'value':'cooling Water [kg/dt]'}
                                 ],
                                style={'width': '100%',
                                       'color':'black'},
                                       value=None)
                        ], style={'margin-bottom': '20px',
                                  'margin-top': '10px'}),

                dbc.Row([
                    dcc.Graph(id='graph_quantities_hydrogen', figure = {}, clickData=None, hoverData=None, 
                            config={'staticPlot': False,
                                    'scrollZoom': True,
                                    'doubleClick': 'reset',
                                    'showTips': True,
                                    'displayModeBar': True,
                                    'watermark': True,
                                    'displaylogo': False,
                                    'toImageButtonOptions': {'format': 'png', 'filename': 'custom_image', 'height': 1080, 'width': 1920, 'scale': 1}})
                ], style={'margin-bottom': '20px'}),
# TODO: # Graph not visible until availability resolved
                # dbc.Row([
                #     dcc.Graph(id='graph_quantities_hydrogen_pie', figure = {}, clickData=None, hoverData=None, 
                #             config={'staticPlot': False,
                #                     'scrollZoom': True,
                #                     'doubleClick': 'reset',
                #                     'showTips': True,
                #                     'displayModeBar': True,
                #                     'watermark': True,
                #                     'displaylogo': False,
                #                     'toImageButtonOptions': {'format': 'png', 'filename': 'custom_image', 'height': 1080, 'width': 1920, 'scale': 1}})
                # ], style={'margin-bottom': '20px'}),


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

    fig = px.line(pd.read_csv('GUI/csv-files/df_timeseries.csv', index_col=0), y=dropdown_plot)
    fig.update_layout(xaxis={'title': 'Time'}, yaxis={'title': 'Power [kW]'},
                      title={'text': 'Time Series'},
                      legend={'title': 'Component'})
    return fig

@callback(
    Output('graph_power_hydrogen', 'figure'),
    [Input('dropdown_power_hydrogen', 'value'),]
    )

def build_graph(dropdown_power_hydrogen):
    """
    Builds a line graph based on the selected power profile.

    Parameters:
    dropdown_power_hydrogen (str): The selected power profile.

    Returns:
    fig (plotly.graph_objs._figure.Figure): The line graph representing the power profile.
    """
    if dropdown_power_hydrogen is None:
        raise PreventUpdate
    df=pd.read_csv('GUI/csv-files/hydrogen_time_series.csv', index_col='time')
    df_selected=df[dropdown_power_hydrogen]
    fig = px.line(df_selected, y=dropdown_power_hydrogen)
    fig.update_layout(xaxis={'title': 'Time'}, yaxis={'title': 'Power [kW]'},
                      title={'text': 'Power profile'},
                      legend={'title': 'Component'},
                    
    )
    return fig


@callback(
    Output('graph_quantities_hydrogen', 'figure'),
    [Input('dropdown_quantities_hydrogen', 'value'),]
    )

def build_graph(dropdown_quantities_hydrogen):
    """
    Builds a line graph based on the selected dropdown quantity.

    Parameters:
    dropdown_quantities_hydrogen (str): The selected dropdown quantity.

    Returns:
    fig (plotly.graph_objs._figure.Figure): The line graph figure.
    """

    if dropdown_quantities_hydrogen is None:
        raise PreventUpdate
    df=pd.read_csv('GUI/csv-files/hydrogen_time_series.csv', index_col='time')
    df_selected=df[dropdown_quantities_hydrogen]
    fig = px.line(df_selected)
    fig.update_layout(xaxis={'title': 'Time'}, yaxis={'title': 'Quantity [kg]'}, title={'text': 'Production profile'}, legend={'title': 'Component'})
    return fig

# @callback(
#     Output('graph_quantities_hydrogen_pie', 'figure'),
#     Input('simulate_button', 'n_clicks')
#     )

# def build_graph(n_clicks):
    """
    Builds a pie chart graph based on the data from 'hydrogen_time_series.csv'.

    Args:
        n_clicks (int): The number of clicks.

    Returns:
        fig (plotly.graph_objects.Figure): The pie chart figure.

    Raises:
        PreventUpdate: If n_clicks is None.

    """
    # if n_clicks is not None:
    #     time.sleep(5)
    #     df = pd.read_csv('GUI/csv-files/hydrogen_time_series.csv')
    #     sum_H2 = df['hydrogen production [Kg/dt]'].sum()
    #     sum_O2 = df['Oxygen [kg/dt]'].sum()
    #     sum_H2O = df['H20 [kg/dt]'].sum()
    #     df_pie = pd.DataFrame({'H2': sum_H2, 'O2': sum_O2, 'H2O': sum_H2O}, index=[0])
    #     fig = px.pie(df_pie, values=[sum_H2, sum_O2, sum_H2O], names=['H2', 'O2', 'H2O'], color_discrete_sequence=['darkblue', 'lightcyan','cyan'], title='Quantities produced')
    #     fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
    #                   plot_bgcolor='rgba(0,0,0,0)',
    #                     font=dict(color='white'))
    # else:
    #     raise PreventUpdate
    # return fig
