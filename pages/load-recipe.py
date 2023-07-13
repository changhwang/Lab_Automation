from dash import Dash, html, dcc, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc
import dash

dash.register_page(__name__, path="/load-recipe", title="Load Recipe", name="Load Recipe")



layout = html.Div(
    [
        html.H1("Load Recipe"),
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
                            {"name": "Posix Compatible", "id": "posix_friendly"},
                            {"name": "Viewer Compatible", "id": "dash_friendly"},
                            {"name": "Python Code Available", "id": "python_code"},
                        ],
                        data=[],
                        style_table={"width": "100%"},
                        style_cell={"textAlign": "left"},
                        style_header={"fontWeight": "bold"},
                        page_current=0,
                        page_size=10,
                        style_data_conditional=[
                            {
                                "if": {
                                    "column_id": "posix_friendly",
                                    "filter_query": "{posix_friendly} contains true",
                                },
                                "backgroundColor": "#b7e8c4",
                                "color": "black",
                            },
                            {
                                "if": {
                                    "column_id": "posix_friendly",
                                    "filter_query": "{posix_friendly} contains false",
                                },
                                "backgroundColor": "#e8b7b7",
                                "color": "black",
                            },
                            {
                                "if": {
                                    "column_id": "dash_friendly",
                                    "filter_query": "{dash_friendly} contains true",
                                },
                                "backgroundColor": "#b7e8c4",
                                "color": "black",
                            },
                            {
                                "if": {
                                    "column_id": "dash_friendly",
                                    "filter_query": "{dash_friendly} contains false",
                                },
                                "backgroundColor": "#e8b7b7",
                                "color": "black",
                            },
                            {
                                "if": {
                                    "column_id": "python_code",
                                    "filter_query": "{python_code} contains true",
                                },
                                "backgroundColor": "#b7e8c4",
                                "color": "black",
                            },
                            {
                                "if": {
                                    "column_id": "python_code",
                                    "filter_query": "{python_code} contains false",
                                },
                                "backgroundColor": "#e8b7b7",
                                "color": "black",
                            },
                        ],
                    ),
                    width=10,
                )
            ]
        ),
    ],
    className="container",
)
