from dash import Dash, html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import dash


dash.register_page(__name__, path="/manual-control", title="Manual Control", name="Manual Control")

layout = html.Div(
    [
        html.H1("Manual Control", className="mb-3"),
        dcc.Interval(id="interval-manual-control", interval=500000, n_intervals=0),
        dbc.ButtonGroup(
            [
                dbc.Button(
                    "Open Execute Window",
                    id="manual-control-open-execute-modal-button",
                    n_clicks=0,
                    disabled=True,
                ),
                dbc.Button("Clear", id="manual-control-clear-button", n_clicks=0, disabled=True),
            ],
            className="mb-3",
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Execute")),
                dbc.ModalBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            "Execute",
                                            id="manual-control-execute-button",
                                            n_clicks=0,
                                            style={"width": "100%"},
                                        )
                                    ],
                                    width=2,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Alert(
                                            "Alert",
                                            id="manual-control-alert",
                                            is_open=False,
                                            duration=500,
                                        )
                                    ]
                                ),
                            ]
                        ),
                        html.Div(
                            id="manual-control-execute-modal-body-code",
                            className="log-container",
                            style={
                                "height": "160px",
                                "overflow-y": "scroll",
                                "padding": "10px",
                                "border": "2px solid",
                                "margin-bottom": "10px",
                            },
                        ),
                        html.Div(
                            id="manual-control-execute-modal-body",
                            className="log-container",
                            style={
                                "height": "300px",
                                "overflow-y": "scroll",
                                "padding": "10px",
                                "border": "2px solid",
                            },
                        ),
                    ]
                ),
            ],
            id="manual-control-execute-modal",
            size="xl",
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("COM Port Information")),
                dbc.ModalBody([html.Div(id="manual-control-serial-ports-info")]),
            ],
            id="manual-control-port-modal",
        ),
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
                        dbc.Col(
                            [
                                dbc.NavLink(
                                    id="manual-control-port-field",
                                    style={"display": "none"},
                                ),
                            ],
                            id="manual-control-device-form",
                        ),
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
