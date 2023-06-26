from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
import dash

dash.register_page(__name__, "/")

layout = html.Div(
    [
        html.H1("Home"),
        dcc.Input(id="filename-input", type="text", placeholder="Enter filename name"),
        dbc.Button("Load", id="filename-input-button", n_clicks=0),
        html.Div(id="home-output"),
        dbc.Button("Refresh List", id="home-refresh-list-button", n_clicks=0),
        dash_table.DataTable(
            id="home-recipes-list-table",
            columns=[
                {"name": "File Name", "id": "file_name"},
                #  {'name':'YAML', 'id':'yaml_data'}
            ],
            data=[],
            style_table={"width": "300px"},
            style_cell={"textAlign": "left"},
        ),
    ]
)