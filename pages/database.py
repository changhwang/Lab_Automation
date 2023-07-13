from dash import Dash, html, dcc, dash_table, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash

dash.register_page(__name__, path="/database", title="Database Browser", name="Database Browser")

layout = html.Div(
    [
        html.H1("Database Browser", className="mb-3"),
        dcc.Interval(id="interval-database", interval=500000, n_intervals=0),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="database-collection-dropdown",
                            options=[],
                            value=None,
                            className="mb-3",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="database-document-dropdown",
                            options=[],
                            value=None,
                            className="mb-3",
                            disabled=True,
                        )
                    ]
                )
            ]
        ),
    ],
    className="container",
)
