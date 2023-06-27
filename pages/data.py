from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
import dash
# from dash_dangerously_set_inner_html import DangerouslySetInnerHTML

dash.register_page(__name__, "/data")

layout = html.Div(
    [
        html.H1("Data"),
        dbc.Button("Load data",id='load-data-button', n_clicks=0),
        dcc.Textarea(
            id="data-output", readOnly=True, style={"width": "100%", "height": 0}
        ),
        html.Div(id='data-output-div')
    ]
)