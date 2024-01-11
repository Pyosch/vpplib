from dash import dash, dcc, html, callback, Input, Output, State, dash_table, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate
import base64
import io
import datetime

layout=dbc.Container([
dbc.Row([
                    dbc.Col([
                            html.P('Identifier')
                            ], width=3),
                    dbc.Col([
                            dbc.Input(
                                    id='input_identifier',
                                    type='text',
                                    placeholder='bus_1',
                                    value='bus_1')
                            ], width=2)
                    ],style={'margin-top': '20px'}),      
                dbc.Row([
                    dbc.Col([
                            html.P('Latitude'),
                            ],width=3),
                    dbc.Col([
                        dbc.Input(
                                id='input_latitude',
                                type='number',
                                placeholder='e.g. 50.7498321',
                                value=50.941357)
                        ], width=2)
                    ]),
                dbc.Row([
                    dbc.Col([                 
                            html.P('Longitude')
                            ],width=3),
                    dbc.Col([
                                dbc.Input(
                                id='input_longitude',
                                type='number',
                                placeholder='e.g. 6.473982',
                                value=6.958307)
                            ], width=2)
                    ]),
                dbc.Row([
                    dbc.Col([
                            html.P('Max. radius to weather stations')
                            ], width=3),
                    dbc.Col([
                            dbc.InputGroup([
                                dbc.Input(
                                    id='input_radius_weather_stations',
                                    type='number',
                                    placeholder='e.g. 30',
                                    value=30),
                            dbc.InputGroupText('km')
                            ])
                        ], width=2)
                    ]),
                dbc.Row([
                    dbc.Col([
                            html.P('Thermal Energy Demand')
                            ], width=3),
                    dbc.Col([
                            dbc.InputGroup([
                                dbc.Input(id='input_thermal_energy_demand',
                                    type='number',
                                    placeholder='e.g. 10000 kWh',
                                    value=12500),
                                dbc.InputGroupText('kWh')
                            ])      
                            ], width=2)
                    ]),
                dbc.Row([
                    dbc.Col([
                            html.P('Comfort Factor')
                            ],width=3),
                    dbc.Col([
                            dbc.Input(
                                    id='input_comfort_factor',
                                    type='number',
                                    placeholder='e.g. ?',
                                    value=0)
                            ], width=2)
                    ]),
                dbc.Row([
                    dbc.Col([
                            html.P('Daily Vehicle Usage')
                            ],width=3),
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                    id='input_daily_vehicle_usage',
                                    type='number',
                                    placeholder='e.g. 100 km',
                                    value=0),
                            dbc.InputGroupText('km')
                        ])
                    ], width=2)
                    ]),
                dbc.Row([
                    dbc.Col([
                            html.P('Building Type')
                            ], width=3),
                    dbc.Col([
                            dcc.Dropdown( 
                                ['DE_HEF33', 'DE_HEFXYZ'],
                                id='dropwdown_building_type',
                                style={
                                        'color': 'black',
                                        'bgcolor': 'white',
                                        'width': '100%'
                                        },
                                placeholder='Choose a Building Type',
                                value='DE_HEF33')
                            ], width=2)
                    ]),
                dbc.Row([
                    dbc.Col([
                            html.P('T0'),
                            ], width=3),
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.Input(
                                id='input_t0',
                                type='number',
                                placeholder='e.g. 20 °C',
                                value=40),
                            dbc.InputGroupText('°C')])
                            ], width=2)
                    ], align='center'),
                dbc.Row([
                    dbc.Col([
                                html.P('Upload Base Load')   
                            ], width=3),
                    dbc.Col([
                        dcc.Upload(
                            id='upload_base_load',
                            children=dbc.Container([
                                'Drag and Drop or ',
                                html.A('Select Files')
                            ]),style={
                                'height': 'auto',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'textAlign': 'center',
                                'margin': '10px',
                            }, multiple=False)
                            
                        ], width=3)
                    ], align='center'),
                    dbc.Row([
                                dbc.Col([
                                    dbc.Button('Submit Settings',
                                               id='submit_user_profile',
                                               color='primary')
                                ])
                            ]),
        html.Div(id='output-data-upload'),                
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            # print(df)
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns],
                                    page_action='native',  page_current=0,
                        page_size=20, sort_action='native',
                        style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                    'color': 'white', 'textAlign':'center'},
                        style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                    'color': 'white', 'width':'auto'},
                        style_cell={'font-family':'sans-serif'},
                        style_table={'margin-bottom': '20px'}
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'})
    ])

@callback(Output('output-data-upload', 'children'),
          Output('store_base_load', 'data'),
              Input('upload_base_load', 'contents'),
              State('upload_base_load', 'filename'),
              State('upload_base_load', 'last_modified'))

def update_output(list_of_contents, list_of_names, list_of_dates):
   if list_of_contents is not None:
        children = [parse_contents(list_of_contents, list_of_names, list_of_dates)]
        return children, children
   else:
        raise PreventUpdate

@callback(
    Output('store_user_profile', 'data'),
    [Input('submit_user_profile', 'n_clicks')],
    [State('input_identifier', 'value'),
     State('input_latitude', 'value'),
     State('input_longitude', 'value'),
     State('input_radius_weather_stations', 'value'),
     State('input_thermal_energy_demand', 'value'),
     State('input_comfort_factor', 'value'),
     State('input_daily_vehicle_usage', 'value'),
     State('dropwdown_building_type', 'value'),
     State('input_t0', 'value')]
)
def update_user_profile(n_clicks, identifier, latitude, longitude, radius_weather_stations,
                                thermal_energy_demand, comfort_factor,
                                daily_vehicle_usage, building_type, t0):
    if 'submit_user_profile' ==ctx.triggered_id and n_clicks is not None:
        data_user_profile={'Identifier': identifier,
                                          'Latitude': latitude,
                                          'Longitude': longitude,
                                          'Radius Weather Stations': radius_weather_stations,
                                          'Thermal Energy Demand': thermal_energy_demand,
                                          'Comfort Factor': comfort_factor,
                                          'Daily Vehicle Usage': daily_vehicle_usage,
                                          'Building Type': building_type,
                                          'T0': t0
                                          }
        return data_user_profile
    elif n_clicks is None:
        raise PreventUpdate