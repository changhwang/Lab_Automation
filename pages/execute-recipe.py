from dash import Dash, html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import dash
import logging
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML


dash.register_page(__name__, "/execute-recipe")

layout = html.Div(
    [
        html.H1("Execute Recipe"),
        dbc.Button("Execute", id="execute-button", n_clicks=0),
        dbc.Button("Stop", id="stop-button", n_clicks=0),
        dbc.Button("Reset", id="reset-button", n_clicks=0),
        html.Div(id="execute-recipe-output"),
        dcc.Interval(id="update-interval", interval=1000, n_intervals=0),
        # dcc.Textarea(
        #     id="console-output", readOnly=True, style={"width": "100%", "height": 0}
        # ),
        dcc.Interval(id="interval1", interval=500, n_intervals=0),
        html.Div(id="hidden-div", style={"display": "none"}),
        html.H4(id="div-out", children="Log"),
        # html.Iframe(id='console-out',srcDoc='',style={'width': '100%','height':400}),
        html.Div(id="console-out2"),
    ]
)
