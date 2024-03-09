# -*- coding: utf-8 -*-
"""
Info
----
This module defines the layout and callbacks for the run simulation tab in the GUI.
It contains a button to start the simulation and a button to download the results.

Functions:
- simulate: Simulate the energy system based on the user inputs.
- download: Download the results of the simulation.

The layout is defined using the Dash Bootstrap Components library.
The used data is taken from in store_basic_settings, store_environment, store_user_profile, store_bev, store_pv, store_wind, store_heatpump, and store_storage.
The results of the simulation are stored in the df_timeseries.csv file.

@author: sharth1
"""

from dash import  dcc, html, callback, Input, Output, State, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate
from basic_simulation import simulation
import os
import time
import zipfile
import shutil
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#Layout Section_________________________________________________________________________________________
layout=dbc.Container([
    dbc.Row([
             dbc.Button('Simulate',
                        id='simulate_button',
                        color='primary',
                        size='sm'),
            html.Div(id='output_simulate_button', children=[])
    ], style={'margin-top': '20px'}),
    dbc.Row([
         dbc.Input(id='project_file_name', placeholder='Project File Name', type='text', value='project_file_name'),
     ],style={'margin-top': '20px'}),
    dbc.Row([
             dbc.Button('Download Results',
                        id='download_button',
                        color='primary',
                        size='sm',),
            
    ], style={'margin-top': '20px'}),
    dcc.Loading(id='is-loading', children=[html.Div(id='is-loading-output')], type='circle'),
    dcc.Download(id="download-time-series"),
    dcc.Download(id="download-basic-settings"),
    
])
#Callback Section_________________________________________________________________________________________
@callback(
    Output('is-loading-output', 'children'),
    [Input('simulate_button', 'n_clicks'),
     Input('store_basic_settings', 'data'),
     Input('store_environment', 'data'),
     Input('store_user_profile', 'data'),
     Input('store_bev', 'data'),
     Input('store_pv', 'data'),
     Input('store_wind', 'data'),
     Input('store_heatpump', 'data'),
     Input('store_storage', 'data')],

)
def simulate(n_clicks, store_basic_settings, store_environment, store_user_profile, store_bev,
               store_pv, store_wind, store_heatpump, store_storage):
    """
    Simulates the scenario based on the provided settings and data.

    Parameters:
    - n_clicks (int): The number of times the simulate button has been clicked.
    - store_basic_settings (dict): The basic settings for the simulation.
    - store_environment (dict): The environmental data for the simulation.
    - store_user_profile (dict): The user profile data for the simulation.
    - store_bev (dict): The battery electric vehicle data for the simulation.
    - store_pv (dict): The photovoltaic data for the simulation.
    - store_wind (dict): The wind turbine data for the simulation.
    - store_heatpump (dict): The heat pump data for the simulation.
    - store_storage (dict): The energy storage data for the simulation.

    Raises:
    - PreventUpdate: If the simulate button was not triggered or if n_clicks is None.

    Returns:
    - None
    """
    if 'simulate_button' == ctx.triggered_id and n_clicks is not None:
        print('simulating')
        simulation(store_basic_settings, store_environment, store_user_profile, store_bev,
               store_pv, store_wind, store_heatpump, store_storage)
        print('done')
        time.sleep(1)
    else:
        raise PreventUpdate



@callback(
    Output("download-time-series", "data"),
    Input("download_button", "n_clicks"),
    Input('project_file_name', 'value'),
    Input('store_basic_settings', 'data'),
    Input('store_environment', 'data'),
    Input('store_user_profile', 'data'),
    Input('store_bev', 'data'),
    Input('store_pv', 'data'),
    Input('store_wind', 'data'),
    Input('store_heatpump', 'data'),
    Input('store_storage', 'data'),



)
def download(n_clicks, value, store_basic_settings, store_environment, store_user_profile, store_bev, store_pv, store_wind, store_heatpump, store_storage):
    """
    Downloads the dataframes as CSV files and creates a zip file containing them.

    Args:
        n_clicks (int): The number of times the download button has been clicked.
        value (str): The name of the new project.
        store_basic_settings (dict): The basic settings dataframe.
        store_environment (dict): The environment dataframe.
        store_user_profile (dict): The user profile dataframe.
        store_bev (dict): The BEV dataframe.
        store_pv (dict): The PV dataframe.
        store_wind (dict): The wind dataframe.
        store_heatpump (dict): The heat pump dataframe.
        store_storage (dict): The storage dataframe.

    Returns:
        dash.dependencies.send_file: The zip file containing the CSV files.

    Raises:
        PreventUpdate: If the download button was not triggered or if n_clicks is None.
    """
    if 'download_button' == ctx.triggered_id and n_clicks is not None:
        print('downloading')
        new_project_name = value
        new_project_df = pd.read_csv('GUI/df_timeseries.csv')
        df_basic_settings = pd.DataFrame([store_basic_settings])
        df_environment = pd.DataFrame([store_environment]) 
        df_user_profile = pd.DataFrame([store_user_profile])
        df_bev = pd.DataFrame([store_bev])
        df_pv = pd.DataFrame([store_pv])
        df_wind = pd.DataFrame([store_wind])
        df_heatpump = pd.DataFrame([store_heatpump])
        df_storage = pd.DataFrame([store_storage])

        # Create a temporary directory to store the dataframes
        temp_dir = 'temp'
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save the dataframes as CSV files in the temporary directory
        new_project_df.to_csv(os.path.join(temp_dir, new_project_name+'_timeseries.csv'), index=False)
        df_basic_settings.to_csv(os.path.join(temp_dir, new_project_name+'_basic_settings.csv'), index=False)
        df_environment.to_csv(os.path.join(temp_dir, new_project_name+'_environment.csv'), index=False)
        df_user_profile.to_csv(os.path.join(temp_dir, new_project_name+'_user_profile.csv'), index=False)
        df_bev.to_csv(os.path.join(temp_dir, new_project_name+'_bev.csv'), index=False)
        df_pv.to_csv(os.path.join(temp_dir, new_project_name+'_pv.csv'), index=False)
        df_wind.to_csv(os.path.join(temp_dir, new_project_name+'_wind.csv'), index=False)
        df_heatpump.to_csv(os.path.join(temp_dir, new_project_name+'_heatpump.csv'), index=False)
        df_storage.to_csv(os.path.join(temp_dir, new_project_name+'_storage.csv'), index=False)

        
        # Create a zip file
        zip_file_name = new_project_name + '_data.zip'
        with zipfile.ZipFile(zip_file_name, 'w') as zipf:
            # Add the CSV files to the zip file
            zipf.write(os.path.join(temp_dir, new_project_name+'_timeseries.csv'), arcname=new_project_name+'_timeseries.csv')
            zipf.write(os.path.join(temp_dir, new_project_name+'_basic_settings.csv'), arcname=new_project_name+'_basic_settings.csv')
            zipf.write(os.path.join(temp_dir, new_project_name+'_environment.csv'), arcname=new_project_name+'_environment.csv')
            zipf.write(os.path.join(temp_dir, new_project_name+'_user_profile.csv'), arcname=new_project_name+'_user_profile.csv')
            zipf.write(os.path.join(temp_dir, new_project_name+'_bev.csv'), arcname=new_project_name+'_bev.csv')
            zipf.write(os.path.join(temp_dir, new_project_name+'_pv.csv'), arcname=new_project_name+'_pv.csv')
            zipf.write(os.path.join(temp_dir, new_project_name+'_wind.csv'), arcname=new_project_name+'_wind.csv')
            zipf.write(os.path.join(temp_dir, new_project_name+'_heatpump.csv'), arcname=new_project_name+'_heatpump.csv')
            zipf.write(os.path.join(temp_dir, new_project_name+'_storage.csv'), arcname=new_project_name+'_storage.csv')
            
        
        # Remove the temporary directory
        shutil.rmtree(temp_dir)
        
        # Return the zip file
        return dcc.send_file(zip_file_name)

    else:
        raise PreventUpdate
    
