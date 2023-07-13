from dash import Dash, html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import dash


dash.register_page(
    __name__, path="/manual-control", title="Manual Control", name="Manual Control"
)

layout = html.Div(
    [
        html.H1("Manual Control", className="mb-3"),
        dcc.Interval(id="interval-manual-control", interval=500000, n_intervals=0),
        dbc.ButtonGroup(
            [
                dbc.Button(
                    "Execute",
                    id="manual-control-execute-button",
                    n_clicks=0,
                    disabled=True,
                ),
                dbc.Button(
                    "Clear", id="manual-control-clear-button", n_clicks=0, disabled=True
                ),
            ],
            className="mb-3",
        ),
        dbc.Alert("Alert", id="manual-control-alert", is_open=False, duration=500),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="manual-control-device-dropdown",
                            options=[],
                            value=None,
                            className="mb-3",
                        ),
                        dbc.Col([], id="manual-control-device-form"),
                    ]
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="manual-control-command-dropdown",
                            options=[],
                            value=None,
                            disabled=True,
                            className="mb-3",
                        ),
                        dbc.Col([], id="manual-control-command-form"),
                    ]
                ),
            ],
        ),
    ],
    className="container",
)
