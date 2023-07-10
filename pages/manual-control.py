from dash import Dash, html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import dash


dash.register_page(__name__, "/manual-control")

layout = html.Div(
    [
        html.H1("Manual Control", className="mb-3"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="manual-control-device-dropdown",
                            options=[],
                            value=None,
                        )
                    ]
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="manual-control-command-dropdown",
                            options=[],
                            value=None,
                        )
                    ]
                ),
            ], 
        ),
    ],
    className="container",
)
