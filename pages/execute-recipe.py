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
                dbc.Button("Stop", id="stop-button", n_clicks=0),
                dbc.Button("Reset", id="reset-button", n_clicks=0),
            ],
            className="mb-2",
        ),
        html.Div(
            id="execute-recipe-output", className="mt-3", style={"display": "none"}
        ),
        dcc.Interval(id="update-interval", interval=500, n_intervals=0),
        dcc.Interval(id="interval1", interval=500, n_intervals=0),
        html.Div(id="hidden-div", style={"display": "none"}),
        html.H4("Log"),
        html.Div(
            id="console-out2",
            className="log-container",
            style={
                "height": "500px",
                "overflow-y": "scroll",
                "padding": "10px",
                "border": "2px solid",
            },
        ),
    ],
    className="container",
)

@callback(
    Output("console-out2", "style"),
    [Input("console-out2", "children"), Input("interval1", "n_intervals")],
)
def scroll_to_bottom(children, n):
    return {"height": "500px", "overflowY": "scroll", "padding": "10px", "border": "2px solid", "scrollTop": "99999999"}
