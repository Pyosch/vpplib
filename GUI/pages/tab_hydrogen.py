# -*- coding: utf-8 -*-
"""
Info
----
This module defines the layout and callbacks for the hydrogen tab in the GUI.
It contains input fields for power and pressure settings of an electrolyzer,
buttons for submitting settings, simulating, and downloading results,
dropdowns for selecting power and quantity data, and graphs for displaying the data.

Functions:
- update_hydrogen_settings: Updates the hydrogen settings based on user input.
- simulate_button_hydrogen: Simulates the electrolyzer based on the hydrogen settings.
- download: Downloads the time series data for hydrogen.

The layout is defined using the Dash Bootstrap Components library.
The data for power and quantity dropdowns is read from a CSV file.
The graphs are created using Plotly Express.

@author: sharth1
"""

from dash import html, dcc, Input, Output, State, callback, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate
from Ausführen_Elektrolyseur_input import simulate_electrolyzer
import time
import plotly.express as px
import zipfile
import shutil
import os 

#Layout Section_______________________________________________________________________________________________________________________

layout=dbc.Container([
dbc.Row([
                    dbc.Col([
                        html.P('Power Electrolyzer')
                    ], width=3),
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id='input_electrolyzer_power',
                                type='number',
                                placeholder='e.g. 100 kW',
                                value=15000),
                            dbc.InputGroupText('kW')
                    ])
                    ], width=2),
                ], style={'margin-top': '20px'}),
                dbc.Row([
                    dbc.Col([
                        html.P('Pressure')
                    ], width=3),
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id='input_electrolyzer_pressure',
                                type='number',
                                placeholder='e.g. 150 bar',
                                value=30
                            ),
                            dbc.InputGroupText('bar')
                    ])
                    ], width=2),
                ]),
                dbc.Row([
                                dbc.Col([
                                    dbc.Button('Submit Settings',
                                               id='submit_hydrogen_settings',
                                               color='primary')
                                ], width=2),
                                # dbc.Col([
                                #     dbc.Button('Simulate', 
                                #                id='simulate_button_hydrogen',
                                #                color='primary',),
                                # ], width=2),
                                # dbc.Col([
                                #     dbc.Input(id='project_file_name_hydrogen', placeholder='Project File Name', type='text', value='project_file_name'),
                                # ], width=2),
                                # dbc.Col([
                                #     dbc.Button('Download Results',
                                #                id='download_button_hydrogen',
                                #                color='primary',),
                                # ], width=2),
                            
                                # dcc.Loading(id='is-loading-hydrogen', children=[html.Div(id='is-loading-output-hydrogen')], type='circle'),
                            # ],style={'margin-bottom': '20px'}),
#                 dbc.Row([
#                     dcc.Dropdown(id='dropdown_power_hydrogen',multi=True, 
#                                  options=[{'label':'P_ac', 
#                                            'value':'P_ac'},
#                                            {'label':'P_in without losses [KW]', 
#                                             'value':'P_in without losses [KW]'},
#                                            {'label':'surplus electricity [kW]', 
#                                             'value':'surplus electricity [kW]'},
#                                            {'label':'P_in [KW]', 
#                                             'value':'P_in [KW]'}
#                                  ],
#                                 style={'width': '100%',
#                                        'color':'black'},
#                                        value=None)
#                         ]),
#                 dbc.Row([
#                     dcc.Graph(id='graph_power_hydrogen', figure = {}, clickData=None, hoverData=None, 
#                             config={'staticPlot': False,
#                                     'scrollZoom': True,
#                                     'doubleClick': 'reset',
#                                     'showTips': True,
#                                     'displayModeBar': True,
#                                     'watermark': True,
#                                     'displaylogo': False,
#                                     'toImageButtonOptions': {'format': 'png', 'filename': 'custom_image', 'height': 1080, 'width': 1920, 'scale': 1}})
#                 ], style={'margin-bottom': '20px'}),

#                 dbc.Row([
#                     dcc.Dropdown(id='dropdown_quantities_hydrogen',multi=True, 
#                                  options=[{'label':'hydrogen production [Kg/dt]', 
#                                            'value':'hydrogen production [Kg/dt]'},
#                                            {'label':'H20 [kg/dt]', 
#                                             'value':'H20 [kg/dt]'},
#                                            {'label':'Oxygen [kg/dt]', 
#                                             'value':'Oxygen [kg/dt]'},
#                                            {'label':'cooling Water [kg/dt]', 
#                                             'value':'cooling Water [kg/dt]'}
#                                  ],
#                                 style={'width': '100%',
#                                        'color':'black'},
#                                        value=None)
#                         ]),

#                 dbc.Row([
#                     dcc.Graph(id='graph_quantities_hydrogen', figure = {}, clickData=None, hoverData=None, 
#                             config={'staticPlot': False,
#                                     'scrollZoom': True,
#                                     'doubleClick': 'reset',
#                                     'showTips': True,
#                                     'displayModeBar': True,
#                                     'watermark': True,
#                                     'displaylogo': False,
#                                     'toImageButtonOptions': {'format': 'png', 'filename': 'custom_image', 'height': 1080, 'width': 1920, 'scale': 1}})
#                 ], style={'margin-bottom': '20px'}),

#                 dbc.Row([
#                     dcc.Graph(id='graph_quantities_hydrogen_pie', figure = {}, clickData=None, hoverData=None, 
#                             config={'staticPlot': False,
#                                     'scrollZoom': True,
#                                     'doubleClick': 'reset',
#                                     'showTips': True,
#                                     'displayModeBar': True,
#                                     'watermark': True,
#                                     'displaylogo': False,
#                                     'toImageButtonOptions': {'format': 'png', 'filename': 'custom_image', 'height': 1080, 'width': 1920, 'scale': 1}})
#                 ], style={'margin-bottom': '20px'}),


#     dcc.Download(id="download-time-series-hydrogen"),
])])

#Callback Section_______________________________________________________________________________________________________________________
#Callback Structure:
#1. Update hydrogen settings
#2. Simulate button hydrogen
#3. Download
#4. Build graph 1
#5. Build graph 2
#6. Build graph 3

@callback(
    Output('store_hydrogen', 'data'),
    [Input('submit_hydrogen_settings', 'n_clicks')],
    [State('input_electrolyzer_power', 'value'),
     State('input_electrolyzer_pressure', 'value'),
    ],
)

def update_hydrogen_settings(n_clicks, power, pressure):
    """
    Updates the hydrogen settings based on user input.

    Parameters:
    - n_clicks (int): The number of times the submit button is clicked.
    - power (float): The power input value from the user.
    - pressure (float): The pressure input value from the user.

    Returns:
    - data_hydrogen_settings (dict): A dictionary containing the updated hydrogen settings.

    Raises:
    - PreventUpdate: If the submit button is not clicked.
    """
    if 'submit_hydrogen_settings' ==ctx.triggered_id:
        data_hydrogen_settings={'Power_Electrolyzer': power,
                            'Pressure_Hydrogen': pressure,}
        return data_hydrogen_settings
    
    elif n_clicks is None:
        raise PreventUpdate


# @callback(
#     Output('is-loading-hydrogen', 'children'),
#     [Input('simulate_button_hydrogen', 'n_clicks'),
#      Input('store_hydrogen', 'data'),
#      Input('store_environment', 'data'),
#      Input('store_basic_settings', 'data')],
    

# )
# def simulate_button_hydrogen(n_clicks, store_hydrogen, store_environment, store_basic_settings):
#     """
#     Simulates the hydrogen button click event.

#     Args:
#         n_clicks (int): The number of times the button has been clicked.
#         store_hydrogen (object): The hydrogen store object.
#         store_environment (object): The environment store object.
#         store_basic_settings (object): The basic settings store object.

#     Raises:
#         PreventUpdate: If `n_clicks` is None.

#     Returns:
#         None
#     """
#     if 'simulate_button_hydrogen' == ctx.triggered_id and n_clicks is not None:
#         print('simulating')
#         simulate_electrolyzer(store_hydrogen, store_environment, store_basic_settings)
#         print('done')
#         time.sleep(1)
    
#     elif n_clicks is None:
#         raise PreventUpdate

# @callback(
#     Output("download-time-series-hydrogen", "data"),
#     Input("download_button_hydrogen", "n_clicks"),
#     Input('project_file_name_hydrogen', 'value'),
#     Input('store_hydrogen', 'data')
# )

# def download(n_clicks, value, store_hydrogen):
#     """
#     Downloads a zip file containing CSV files based on the provided parameters.

#     Args:
#         n_clicks (int): The number of times the download button has been clicked.
#         value (str): The project name.
#         store_hydrogen (dict): A dictionary containing hydrogen settings.

#     Returns:
#         dash.dependencies.Download: A Dash Download component that sends the zip file to the client.

#     Raises:
#         dash.exceptions.PreventUpdate: If the download button was not triggered or if n_clicks is None.
#     """

#     if 'download_button_hydrogen' == ctx.triggered_id and n_clicks is not None:
#         print('downloading')
#         new_project_name = value
#          # Create a temporary directory to store the dataframes
#         temp_dir = 'temp'
#         os.makedirs(temp_dir, exist_ok=True)
#         new_project_df_hydrogen = pd.read_csv('GUI/csv-files/hydrogen_time_series.csv')
#         df_hydrogen_settings_hydrogen = pd.DataFrame([store_hydrogen])
        
#         new_project_df_hydrogen.to_csv(os.path.join(temp_dir, new_project_name+'_timeseries.csv'))
#         df_hydrogen_settings_hydrogen.to_csv(os.path.join(temp_dir, new_project_name+'_hydrogen_settings.csv'))

#         # Create a zip file
#         zip_file_name = new_project_name + '_data_hydrogen.zip'

#         with zipfile.ZipFile(zip_file_name, 'w') as zipf:

#             # Add the CSV files to the zip file
#             zipf.write(os.path.join(temp_dir, new_project_name+'_timeseries.csv'), arcname=new_project_name+'_timeseries.csv')
#             zipf.write(os.path.join(temp_dir, new_project_name+'_hydrogen_settings.csv'), arcname=new_project_name+'_hydrogen_settings.csv')

#           # Remove the temporary directory
#         shutil.rmtree(temp_dir)
        
#         # Return the zip file
#         return dcc.send_file(zip_file_name)
    
#     else:
#         raise PreventUpdate

# @callback(
#     Output('graph_power_hydrogen', 'figure'),
#     [Input('dropdown_power_hydrogen', 'value'),]
#     )

# def build_graph(dropdown_power_hydrogen):
#     """
#     Builds a line graph based on the selected power profile.

#     Parameters:
#     dropdown_power_hydrogen (str): The selected power profile.

#     Returns:
#     fig (plotly.graph_objs._figure.Figure): The line graph representing the power profile.
#     """
#     if dropdown_power_hydrogen is None:
#         raise PreventUpdate
#     df=pd.read_csv('GUI/csv-files/hydrogen_time_series.csv', index_col='time')
#     df_selected=df[dropdown_power_hydrogen]
#     fig = px.line(df_selected, y=dropdown_power_hydrogen)
#     fig.update_layout(xaxis={'title': 'Time'}, yaxis={'title': 'Power [kW]'},
#                       title={'text': 'Power profile'},
#                       legend={'title': 'Component'},
                    
#     )
#     return fig


# @callback(
#     Output('graph_quantities_hydrogen', 'figure'),
#     [Input('dropdown_quantities_hydrogen', 'value'),]
#     )

# def build_graph(dropdown_quantities_hydrogen):
#     """
#     Builds a line graph based on the selected dropdown quantity.

#     Parameters:
#     dropdown_quantities_hydrogen (str): The selected dropdown quantity.

#     Returns:
#     fig (plotly.graph_objs._figure.Figure): The line graph figure.
#     """

#     if dropdown_quantities_hydrogen is None:
#         raise PreventUpdate
#     df=pd.read_csv('GUI/csv-files/hydrogen_time_series.csv', index_col='time')
#     df_selected=df[dropdown_quantities_hydrogen]
#     fig = px.line(df_selected)
#     fig.update_layout(xaxis={'title': 'Time'}, yaxis={'title': 'Quantity [kg]'}, title={'text': 'Production profile'}, legend={'title': 'Component'})
#     return fig

# @callback(
#     Output('graph_quantities_hydrogen_pie', 'figure'),
#     Input('simulate_button', 'n_clicks')
    # )

# def build_graph(n_clicks):
#     """
#     Builds a pie chart graph based on the data from 'hydrogen_time_series.csv'.

#     Args:
#         n_clicks (int): The number of clicks.

#     Returns:
#         fig (plotly.graph_objects.Figure): The pie chart figure.

#     Raises:
#         PreventUpdate: If n_clicks is None.

#     """
#     if n_clicks is not None:
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
