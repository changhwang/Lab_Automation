from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
import dash

dash.register_page(__name__, "/")

# layout = html.Div(
#     [
#         html.H1("Home"),
#         dcc.Input(id="filename-input", type="text", placeholder="Enter filename name"),
#         dbc.Button("Load", id="filename-input-button", n_clicks=0),
#         html.Div(id="home-output"),
#         dbc.Button("Refresh List", id="home-refresh-list-button", n_clicks=0),
#         dash_table.DataTable(
#             id="home-recipes-list-table",
#             columns=[
#                 {"name": "File Name", "id": "file_name"},
#                 #   {'name':'Posix', 'id':'posix_friendly'}
#             ],
#             data=[],
#             style_table={"width": "300px"},
#             style_cell={"textAlign": "left"},
#         ),
#     ]
# )

layout = html.Div(
    [
        html.H1("Home"),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Input(
                        id="filename-input",
                        type="text",
                        placeholder="Enter file name",
                        className="form-control",
                    ),
                    width=6,
                ),
                dbc.Col(
                    dbc.Button(
                        "Load",
                        id="filename-input-button",
                        n_clicks=0,
                        color="primary",
                        className="btn btn-primary",
                    ),
                    width=2,
                ),
            ],
            className="mb-3",
        ),
        dbc.Alert(
            id="home-load-file-alert",
            color="success",
            is_open=False,
            # fade=True,
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Refresh List",
                        id="home-refresh-list-button",
                        n_clicks=0,
                        color="secondary",
                        className="btn btn-secondary mb-3",
                    ),
                    width=2,
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dash_table.DataTable(
                        id="home-recipes-list-table",
                        columns=[
                            {"name": "File Name", "id": "file_name"},
                        ],
                        data=[],
                        style_table={"width": "100%"},
                        style_cell={"textAlign": "left"},
                        style_header={"fontWeight": "bold"},
                        page_current=0,
                        page_size=10,
                    ),
                    width=8,
                )
            ]
        ),
    ],
    className="container",
)
