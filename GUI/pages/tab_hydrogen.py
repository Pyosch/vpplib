from dash import dash, html, dcc, Input, Output, State, callback, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate
from a_Ausführem_Elektrolyseur_input import simulate_electrolyzer
import time
import plotly.express as px

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
                                value=500),
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
                        html.P('Quantity') 
                    ], width=3),
                    dbc.Col([
                        dbc.Input(
                            id='input_electrolyzer_quantity',
                            type='number',
                            placeholder='e.g. 100 kg',
                            value=10
                        )
                    ], width=2),
                ]),
                dbc.Row([
                    dbc.Col([
                        html.P('Number of Time Steps') 
                    ], width=3),
                    dbc.Col([
                        dbc.Input(
                            id='input_electrolyzer_number_of_time_steps',
                            type='number',
                            placeholder='e.g. 100',
                            value=10
                        )
                    ], width=2, style={'margin-bottom': '20px'}),
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
                    dcc.Dropdown(id='dropdown_plot_hydrogen',multi=True, 
                                options=[{'label': y, 'value': y} for y in pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0).columns],
                                style={'width': '100%',
                                       'color':'black'},
                                       value=None)
                        ]),
                dbc.Row([
                    dcc.Graph(id='graph_timeseries_hydrogen', figure = {}, clickData=None, hoverData=None, 
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

@callback(
    Output('store_hydrogen', 'data'),
    [Input('submit_hydrogen_settings', 'n_clicks')],
    [State('input_electrolyzer_power', 'value'),
     State('input_electrolyzer_pressure', 'value'),
     State('input_electrolyzer_quantity', 'value'),
     State('input_electrolyzer_number_of_time_steps', 'value')],

)
def update_hydrogen_settings(n_clicks, power, 
                              pressure, quantity, times_steps):
    if 'submit_hydrogen_settings' ==ctx.triggered_id and n_clicks is not None:
        data_hydrogen_settings={'Power_Electrolyzer': power,
                            'Pressure_Hydrogen': pressure,
                            'Quantity_Hydrogen': quantity,
                            'Number of Time Steps': times_steps,}
        return data_hydrogen_settings
    
    elif n_clicks is None:
        raise PreventUpdate
    
@callback(
    Output('is-loading-hydrogen', 'children'),
    [Input('simulate_button_hydrogen', 'n_clicks'),
     Input('store_hydrogen', 'data'),
     Input('store_environment', 'data'),],
    

)
def simulate_button_hydrogen(n_clicks, store_hydrogen, store_environment):
    if 'simulate_button_hydrogen' ==ctx.triggered_id and n_clicks is not None:
        print('simulating')
        simulate_electrolyzer(store_hydrogen, store_environment)
        print('done')
        time.sleep(1)
    
    elif n_clicks is None:
        raise PreventUpdate
    
@callback(
    Output("download-time-series-hydrogen", "data"),
    Input("download_button_hydrogen", "n_clicks"),
    Input('project_file_name_hydrogen', 'value')
)
def download(n_clicks, value):
    if 'download_button_hydrogen' == ctx.triggered_id and n_clicks is not None:
        print('downloading')
        new_project_name = value
        new_project_df = pd.read_csv('GUI/a_hydrogen_time_series.csv')
        return dcc.send_data_frame(new_project_df.to_csv, new_project_name+'_timeseries.csv')
    
    else:
        raise PreventUpdate

@callback(
    Output('graph_timeseries_hydrogen', 'figure'),
    [Input('dropdown_plot_hydrogen', 'value'),]
    )

def build_graph(dropdown_plot_hydrogen):
    if dropdown_plot_hydrogen is None:
        raise PreventUpdate
    df=pd.read_csv('GUI/a_hydrogen_time_series.csv', index_col=0)
    df_selected=df[dropdown_plot_hydrogen]
    fig = px.line(df_selected, y=dropdown_plot_hydrogen)
    fig.update_layout(xaxis={'title': 'Time'}, yaxis={'title': 'Power [kW]'},
                      title={'text': 'Time Series'},
                      legend={'title': 'Component'})
    return fig