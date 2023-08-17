from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import dash


dash.register_page(__name__, path="/options", title="Options", name="Options")

layout = html.Div(
    [html.H1("Options", className="mb-3")],
    className="container",
)
