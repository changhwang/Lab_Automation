from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
import dash


dash.register_page(__name__, path="/data", title="Recipe Document", name="Recipe Document")

layout = html.Div(
    [
        html.H1("View Recipe Document"),
        dbc.Button("Load data", id="load-data-button", n_clicks=0, className="mb-3"),
        # dcc.Textarea(
        #     id="data-output", readOnly=True, style={"width": "100%", "height": 0}
        # ),
        # html.Div(id="data-output-div"),
        html.Div(id="data-output-div2"),
    ],
    className="container",
)
