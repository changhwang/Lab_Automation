from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import dash
from util import devices_ref_redundancy

dash.register_page(
    __name__,
    path="/real-time-telemetry",
    name="Real Time Telemetry",
    title="Real Time Telemetry",
)

layout = html.Div(
    [
        html.H1("Real Time Telemetry", className="mb-3"),
        dcc.Dropdown(
            options=list(devices_ref_redundancy.keys()),
            id="real-time-telemetry-device-dropdown",
        ),
        dcc.Interval(id="interval-real-time-telemetry", interval=500, n_intervals=0),
        html.Div(id="real-time-telemetry-div"),
    ],
    className="container",
)
