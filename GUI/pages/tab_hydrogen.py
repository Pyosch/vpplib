from dash import html, dcc, Input, Output, State, callback, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate
from a_Ausführem_Elektrolyseur_input import simulate_electrolyzer
import time
import plotly.express as px
import zipfile
import shutil
import os 

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
                                dbc.Col([
                                    dbc.Button('Simulate', 
                                               id='simulate_button_hydrogen',
                                               color='primary',),
                                ], width=2),
                                dbc.Col([
                                    dbc.Input(id='project_file_name_hydrogen', placeholder='Project File Name', type='text', value='project_file_name'),
                                ], width=2),
                                dbc.Col([
                                    dbc.Button('Download Results',
                                               id='download_button_hydrogen',
                                               color='primary',),
                                ], width=2),
                            ],style={'margin-bottom': '20px'}),
                dbc.Row([
                    dcc.Dropdown(id='dropdown_power_hydrogen',multi=True, 
                                # options=[{'label': y, 'value': y} for y in pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns],
                                 options=[{'label':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[0], 
                                           'value':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[0]},
                                           {'label':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[1], 
                                            'value':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[1]},
                                           {'label':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[2], 
                                            'value':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[2]},
                                           {'label':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[3], 
                                            'value':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[3]},
                                 ],
                                style={'width': '100%',
                                       'color':'black'},
                                       value=None)
                        ]),
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
                ], style={'margin-bottom': '20px'}),
# ________________________________________________________________
# Dropdown for Quantities produced          
# ________________________________________________________________
                dbc.Row([
                    dcc.Dropdown(id='dropdown_quantities_hydrogen',multi=True, 
                                # options=[{'label': y, 'value': y} for y in pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns],
                                 options=[{'label':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[3], 
                                           'value':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[3]},
                                           {'label':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[7], 
                                            'value':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[7]},
                                           {'label':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[8], 
                                            'value':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[8]},
                                           {'label':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[9], 
                                            'value':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[9]},
                                 ],
                                style={'width': '100%',
                                       'color':'black'},
                                       value=None)
                        ]),
# ________________________________________________________________
# Graph for Quantities produced          
# ________________________________________________________________
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
# ________________________________________________________________
# Dropdown for percentages          
# ________________________________________________________________
                # dbc.Row([
                #     dcc.Dropdown(id='dropdown_percentages_hydrogen',multi=True, 
                #                 # options=[{'label': y, 'value': y} for y in pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns],
                #                  options=[{'label':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[10], 
                #                            'value':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[10]},
                #                            {'label':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[11], 
                #                             'value':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[11]},
                #                            {'label':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[12], 
                #                             'value':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[12]},
                #                            {'label':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[13], 
                #                             'value':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[13]},
                #                            {'label':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[14], 
                #                             'value':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[14]},
                #                            {'label':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[15], 
                #                             'value':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[15]},
                #                            {'label':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[16],
                #                             'value':pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[16]}
                #                  ],
                #                 style={'width': '100%',
                #                        'color':'black'},
                #                        value=None)
                #         ]),
# ________________________________________________________________
# Graph for percentages          
# ________________________________________________________________
                dbc.Row([
                    dcc.Graph(id='graph_percentages_hydrogen', figure = {}, clickData=None, hoverData=None, 
                            config={'staticPlot': False,
                                    'scrollZoom': True,
                                    'doubleClick': 'reset',
                                    'showTips': True,
                                    'displayModeBar': True,
                                    'watermark': True,
                                    'displaylogo': False,
                                    'toImageButtonOptions': {'format': 'png', 'filename': 'custom_image', 'height': 1080, 'width': 1920, 'scale': 1}})
                ]),
    

    dcc.Loading(id='is-loading-hydrogen', children=[html.Div(id='is-loading-output-hydrogen')], type='circle'),
    dcc.Download(id="download-time-series-hydrogen"),
])


# ______________________________________________________________________________________________
# Callback updating hydrogen settings
# ______________________________________________________________________________________________


@callback(
    Output('store_hydrogen', 'data'),
    [Input('submit_hydrogen_settings', 'n_clicks')],
    [State('input_electrolyzer_power', 'value'),
     State('input_electrolyzer_pressure', 'value'),
    #  State('input_electrolyzer_quantity', 'value')
    ],

)
def update_hydrogen_settings(n_clicks, power, 
                              pressure):
    if 'submit_hydrogen_settings' ==ctx.triggered_id and n_clicks is not None:
        data_hydrogen_settings={'Power_Electrolyzer': power,
                            'Pressure_Hydrogen': pressure,}
                            # 'Quantity_Hydrogen': quantity}
        return data_hydrogen_settings
    
    elif n_clicks is None:
        raise PreventUpdate

# ______________________________________________________________________________________________
# Callback initalizing loading icon and starting simulation
# ______________________________________________________________________________________________


@callback(
    Output('is-loading-hydrogen', 'children'),
    [Input('simulate_button_hydrogen', 'n_clicks'),
     Input('store_hydrogen', 'data'),
     Input('store_environment', 'data'),
     Input('store_basic_settings', 'data')],
    

)
def simulate_button_hydrogen(n_clicks, store_hydrogen, store_environment, store_basic_settings):
    if 'simulate_button_hydrogen' ==ctx.triggered_id and n_clicks is not None:
        print('simulating')
        simulate_electrolyzer(store_hydrogen, store_environment, store_basic_settings)
        print('done')
        time.sleep(1)
    
    elif n_clicks is None:
        raise PreventUpdate


# ______________________________________________________________________________________________
# Callback for Download
# ______________________________________________________________________________________________


@callback(
    Output("download-time-series-hydrogen", "data"),
    Input("download_button_hydrogen", "n_clicks"),
    Input('project_file_name_hydrogen', 'value'),
    Input('store_hydrogen', 'data')
)
def download(n_clicks, value, store_hydrogen):
    if 'download_button_hydrogen' == ctx.triggered_id and n_clicks is not None:
        print('downloading')
        new_project_name = value
         # Create a temporary directory to store the dataframes
        temp_dir = 'temp'
        os.makedirs(temp_dir, exist_ok=True)
        new_project_df = pd.read_csv('GUI/a_hydrogen_time_series.csv')
        df_hydrogen_settings = pd.DataFrame([store_hydrogen])

        new_project_df.to_csv(os.path.join(temp_dir, new_project_name+'_timeseries.csv'))
        df_hydrogen_settings.to_csv(os.path.join(temp_dir, new_project_name+'_hydrogen_settings.csv'))

        # Create a zip file
        zip_file_name = new_project_name + '_data_hydrogen.zip'

        with zipfile.ZipFile(zip_file_name, 'w') as zipf:

            # Add the CSV files to the zip file
            zipf.write(os.path.join(temp_dir, new_project_name+'_timeseries.csv'), arcname=new_project_name+'_timeseries.csv')
            zipf.write(os.path.join(temp_dir, new_project_name+'_hydrogen_settings.csv'), arcname=new_project_name+'_hydrogen_settings.csv')

          # Remove the temporary directory
        shutil.rmtree(temp_dir)
        
        # Return the zip file
        return dcc.send_file(zip_file_name)
    
    else:
        raise PreventUpdate

# ______________________________________________________________________________________________
# Callback for Graph Power
# ______________________________________________________________________________________________

@callback(
    Output('graph_power_hydrogen', 'figure'),
    [Input('dropdown_power_hydrogen', 'value'),]
    )

def build_graph(dropdown_power_hydrogen):
    if dropdown_power_hydrogen is None:
        raise PreventUpdate
    df=pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0)
    df_selected=df[dropdown_power_hydrogen]
    fig = px.line(df_selected, y=dropdown_power_hydrogen)
    fig.update_layout(xaxis={'title': 'Time'}, yaxis={'title': 'Power [kW]'},
                      title={'text': 'Time Series'},
                      legend={'title': 'Component'})
    return fig


# ______________________________________________________________________________________________
# Callback for Graph Quantities
# ______________________________________________________________________________________________

@callback(
    Output('graph_quantities_hydrogen', 'figure'),
    [Input('dropdown_quantities_hydrogen', 'value'),]
    )

def build_graph(dropdown_quantities_hydrogen):
    if dropdown_quantities_hydrogen is None:
        raise PreventUpdate
    df=pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0)
    df_selected=df[dropdown_quantities_hydrogen]
    fig = px.line(df_selected, y=dropdown_quantities_hydrogen)
    fig.update_layout(xaxis={'title': 'Time'}, yaxis={'title': 'Power [kW]'},
                      title={'text': 'Time Series'},
                      legend={'title': 'Component'})
    return fig

# ______________________________________________________________________________________________
# Callback for Graph percentages
# ______________________________________________________________________________________________

@callback(
    Output('graph_percentages_hydrogen', 'figure'),
    [Input('simulate_button_hydrogen', 'n_clicks'),]
    )

def build_graph(n_clicks):
    if n_clicks == ctx.triggered_id and n_clicks is not None:
        
        df_selected=pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns[10:16]
        fig = px.bar(color=df_selected)
        fig.update_layout(title={'text': 'Time Series'},
                        legend={'title': 'Component'})
        return fig
    else:
        raise PreventUpdate