# -*- coding: utf-8 -*-
"""
Info
----
This module defines the layout and callbacks for the wind tab in the GUI.
It contains inputfields for the user to select the wind turbine type, hub height, rotor diameter, comfort factor, data source, wind speed model, density model, temperature model, power output model, density correction, obstacle height, and hellmann exponent.

Functions:
- update_wind_settings: Update wind settings based on user inputs.


The layout is defined using the Dash Bootstrap Components library.
The submitted data is stored in store_wind.

@author: sharth1
"""

from dash import dcc, html, callback, Input, Output, State, callback_context as ctx
import dash_bootstrap_components as dbc
import pandas as pd
from dash.exceptions import PreventUpdate

#Layout Section_________________________________________________________________________________________    

layout=dbc.Container([
        dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader('Wind Turbine Data', 
                                               style={'font-weight': 'bold'}),
                                dbc.CardBody([
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Turbine Type')
                                        ], width=3),
                                        dbc.Col([
                                            dbc.Input(
                                                id='input_wind_turbine_type',
                                                type='text',
                                                placeholder='e.g. E-141/4200',
                                                value='E-141/4200'
                                            )
                                        ], width=4),
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Hub Height')
                                        ], width=3),
                                        dbc.Col([
                                            dbc.InputGroup([
                                                dbc.Input(
                                                    id='input_wind_hub_height',
                                                    type='number',
                                                    placeholder='e.g. 135 m',
                                                    value=159
                                                ),
                                                dbc.InputGroupText('m')
                                            ])
                                        ],width=4)                                    
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Rotor Diameter')
                                        ], width=3),
                                        dbc.Col([
                                            dbc.InputGroup([
                                                dbc.Input(
                                                    id='input_wind_rotor_diameter',
                                                    type='number',
                                                    placeholder='e.g. 127 m',
                                                    value=141
                                                ),
                                                dbc.InputGroupText('m')
                                            ])
                                        ], width=4)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Comfort Factor')
                                        ], width=3),
                                        dbc.Col([
                                            dbc.Input( #TODO: What is this? Compare with Screeenshot
                                                id='input_wind_comfort_factor',
                                                type='number',
                                                placeholder='e.g. 0.9',
                                                value=0
                                            )
                                        ], width=4)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Data source')
                                        ], width=3),
                                        dbc.Col([
                                            dcc.Dropdown(
                                                ['oedb', 'xyz'],
                                                id='dropdown_wind_data_source',
                                                clearable=True,
                                                style={
                                                       'color': 'black',
                                                       'bgcolor': 'white',
                                                       },
                                                placeholder='e.g. WindTurbines',
                                                value='oedb'
                                            )
                                        ], width =4)
                                    ])
                                ])
                            ])
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader('Wind Power Model Chain Data',
                                               style={'font-weight': 'bold'}),
                                dbc.CardBody([
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Wind Speed Model')
                                        ], width = 4),
                                        dbc.Col([
                                            dcc.Dropdown(
                                                ['logarithmic', 'hellman', 'interpolation_extrapolation'],
                                                id='dropdown_wind_speed_model',
                                                clearable=True,
                                                style={'color': 'black',
                                                       'bgcolor': 'white',
                                                       },
                                                placeholder='e.g. logarithmic',
                                                value='logarithmic'
                                            )
                                        ], width=4)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Density Model')
                                        ], width=4),
                                        dbc.Col([
                                            dcc.Dropdown(
                                                ['barometric', 'ideal_gas', 'interpolation_extrapolation'],
                                                id='dropdown_wind_density_model',
                                                clearable=True,
                                                style={'color': 'black',
                                                       'bgcolor': 'white',
                                                       },
                                                placeholder='e.g. barometric',
                                                value='ideal_gas'
                                            )
                                        ], width=4)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Temperature Model')
                                        ], width=4),
                                        dbc.Col([
                                            dcc.Dropdown(
                                                ['linear_gradient', 'interpolation_extrapolation'],
                                                id='dropdown_wind_temperature_model',
                                                clearable=True,
                                                style={'color': 'black',
                                                       'bgcolor': 'white',
                                                       },
                                                placeholder='e.g. linear gradient',
                                                value='linear_gradient'
                                            )
                                        ], width=4)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Power Output Model')
                                        ], width=4),
                                        dbc.Col([
                                            dcc.Dropdown(
                                                ['power_curve', 'power_coefficient_curve'],
                                                id='dropdown_wind_power_output_model',
                                                clearable=True,
                                                style={'color': 'black',
                                                       'bgcolor': 'white',
                                                       },
                                                placeholder='power curve',
                                                value='power_curve'
                                            )
                                        ], width=4)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Density Correction', style={'margin-top': '10%'})
                                        ], width=4),
                                        dbc.Col([
                                            dbc.Switch(
                                                id='switch_wind_density_correction',
                                                style={'width': 'auto', 'margin-top': '5%'},
                                                value=False
                                            )
                                        ])
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Obstacle Height')
                                        ], width=4),
                                        dbc.Col([
                                            dbc.InputGroup([
                                                dbc.Input(
                                                    id='input_wind_obstacle_height',
                                                    type='number',
                                                    placeholder='e.g. 0 m',
                                                    value=0
                                                ),
                                                dbc.InputGroupText('m')
                                            ])
                                        ], width=4)
                                    ]),
                                    dbc.Row([
                                        dbc.Col([
                                            html.P('Hellmann Exponent')
                                        ], width=4),
                                        dbc.Col([
                                            dbc.Input( 
                                                id='input_hellmann_exponent',
                                                type='text',
                                                placeholder='e.g. 0.2',
                                                value=0
                                            )
                                        ], width=4)
                                    ]),
                                ])
                            ])
                        ])
                    ], style={'margin-top': '20px'}),
                    dbc.Row([
                                dbc.Col([
                                    dbc.Button('Submit Settings',
                                               id='submit_wind_settings',
                                               color='primary')
                                ])
                            ])
               
])

#Callback Section_______________________________________________________________________________________

@callback(
    Output('store_wind', 'data'),
    [Input('submit_wind_settings', 'n_clicks')],
    [State('input_wind_turbine_type', 'value'),
     State('input_wind_hub_height', 'value'),
     State('input_wind_rotor_diameter', 'value'),
     State('input_wind_comfort_factor', 'value'),
     State('dropdown_wind_data_source', 'value'),
     State('dropdown_wind_speed_model', 'value'),
     State('dropdown_wind_density_model', 'value'),
     State('dropdown_wind_temperature_model', 'value'),
     State('dropdown_wind_power_output_model', 'value'),
     State('switch_wind_density_correction', 'on'),
     State('input_wind_obstacle_height', 'value'),
     State('input_hellmann_exponent', 'value')]
)
def update_wind_settings(n_clicks, turbine_type, hub_height, rotor_diameter,
                                comfort_factor, data_source, speed_model, density_model,
                                temperature_model, power_output_model, density_correction,
                                obstacle_height, hellmann_exponent):
    """
    Update wind settings based on user inputs.

    Args:
        n_clicks (int): Number of times the submit button is clicked.
        turbine_type (str): Type of turbine.
        hub_height (float): Height of the turbine hub.
        rotor_diameter (float): Diameter of the turbine rotor.
        comfort_factor (float): Comfort factor for wind calculations.
        data_source (str): Source of wind data.
        speed_model (str): Model for wind speed calculations.
        density_model (str): Model for air density calculations.
        temperature_model (str): Model for temperature calculations.
        power_output_model (str): Model for power output calculations.
        density_correction (float): Density correction factor.
        obstacle_height (float): Height of obstacles in the wind flow.
        hellmann_exponent (float): Hellmann exponent for wind speed measurements.

    Returns:
        dict: A dictionary containing the updated wind settings.

    Raises:
        PreventUpdate: If the submit button is not clicked.

    """
    if 'submit_wind_settings' == ctx.triggered_id and n_clicks is not None:
        data_wind_settings = {
            'Turbine Type': turbine_type,
            'Hub Height': hub_height,
            'Rotor Diameter': rotor_diameter,
            'Comfort Factor': comfort_factor,
            'Data Source': data_source,
            'Speed Model': speed_model,
            'Density Model': density_model,
            'Temperature Model': temperature_model,
            'Power Output Model': power_output_model,
            'Density Correction': density_correction,
            'Obstacle Height': obstacle_height,
            'Hellmann Exponent': hellmann_exponent
        }
        return data_wind_settings
    elif n_clicks is None:
        raise PreventUpdate