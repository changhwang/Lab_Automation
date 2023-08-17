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


def check_telemetry(device):
    if "telemetry" in list(
        devices_ref_redundancy[device].keys()
    ) and "default_obj" in list(devices_ref_redundancy[device].keys()):
        return True
    else:
        return False


layout = html.Div(
    [
        html.H1("Real Time Telemetry", className="mb-3"),
        dcc.Dropdown(
            options=list(filter(check_telemetry, list(devices_ref_redundancy.keys()))),
            id="real-time-telemetry-device-dropdown",
            className="mb-3",
        ),
        dcc.Interval(id="interval-real-time-telemetry", interval=500, n_intervals=0),
        html.Div(id="real-time-telemetry-div"),
    ],
    className="container",
)
