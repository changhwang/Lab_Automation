from dash import Dash, html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import dash
import logging
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML


dash.register_page(__name__, "/execute-recipe")

layout = html.Div(
    [
        html.H1("Execute Recipe"),
        dbc.ButtonGroup(
            [
                dbc.Button("Execute", id="execute-button", n_clicks=0),
                dbc.Button("Clear Log", id="reset-button", n_clicks=0),
                dbc.Button(
                    "Emergency Stop", id="stop-button", n_clicks=0, color="danger"
                ),
            ],
            className="mb-3",
        ),
        # html.Div(
        #     [
        #         dbc.Switch(
        #             id='show-log-switch',
        #             label='Show log',
        #             value = False,
        #             style={'display': 'none'}
        #         )
        #     ],
        #     className="d-flex align-items-center mt-3",
        # ),
        html.Div(
            id="execute-recipe-output", className="mt-3", style={"display": "none"}
        ),
        dcc.Interval(id="update-interval", interval=500, n_intervals=0),
        dcc.Interval(id="interval1", interval=50, n_intervals=0),
        html.Div(id="hidden-div", style={"display": "none"}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("Recipe Data"),
                        dbc.Textarea(
                            id="execute-recipe-upload-document",
                            className="log-container mb-3",
                            readOnly=True,
                            style={"height": "200px"},
                        ),
                    ]
                ),
            ]
        ),
        html.H4("Log"),
        html.Div(
            id="console-out2",
            className="log-container mb-3",
            style={
                "height": "500px",
                "overflow-y": "scroll",
                "padding": "10px",
                "border": "2px solid",
            },
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("Description"),
                        dbc.Textarea(
                            id="execute-recipe-upload-description",
                            className="log-container mb-3",
                            style={"height": "200px"},
                        ),
                    ]
                ),
            ]
        ),
    ],
    className="container",
)
