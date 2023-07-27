from dash import Dash, html, dcc, dash_table, Input, Output, callback, State
import dash_bootstrap_components as dbc
import dash
import logging


dash.register_page(__name__, path="/execute-recipe", name="Execute Recipe", title="Execute Recipe")

layout = html.Div(
    [
        html.H1("Execute Recipe"),
        dbc.ButtonGroup(
            [
                dbc.Button("Execute", id="execute-button", n_clicks=0),
                dbc.Button("Clear Log", id="reset-button", n_clicks=0),
                dbc.Button("Emergency Stop", id="stop-button", n_clicks=0, color="danger"),
            ],
            className="mb-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Input(
                            id="execute-recipe-upload-name",
                            placeholder="Name this execution",
                            type="text",
                        ),
                    ]
                )
            ],
            className="mb-3",
        ),
        # html.Div(
        #     [
        #         dbc.Switch(
        #             id='show-log-switch',
        #             label='Show log',
        #             value = False,
        #             style={'display': 'none'}
        #         )
        #     ],
        #     className="d-flex align-items-center mt-3",
        # ),
        html.Div(id="execute-recipe-output", className="mt-3", style={"display": "none"}),
        dcc.Interval(id="update-interval", interval=500, n_intervals=0),
        dcc.Interval(id="interval1", interval=50, n_intervals=0),
        html.Div(id="hidden-div", style={"display": "none"}),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("Recipe Data"),
                        dbc.Textarea(
                            id="execute-recipe-upload-document",
                            className="log-container mb-3",
                            readOnly=True,
                            style={"height": "200px"},
                        ),
                    ]
                ),
            ]
        ),
        html.H4("Log"),
        html.Div(
            id="console-out2",
            className="log-container mb-3",
            style={
                "height": "500px",
                "overflow-y": "scroll",
                "padding": "10px",
                "border": "2px solid",
            },
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("Notes"),
                        dbc.Textarea(
                            id="execute-recipe-upload-notes",
                            className="log-container mb-3",
                            style={"height": "200px"},
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.H4("Upload Files"),
                        dcc.Upload(
                            id="execute-recipe-upload-files",
                            children=html.Div(
                                [
                                    "Drag and Drop or ",
                                    html.A(
                                        "Select Files",
                                        style={
                                            "color": "blue",
                                            "textDecoration": "underline",
                                        },
                                    ),
                                    " or ",
                                    html.A(
                                        "Replace Selected",
                                        id="execute-recipe-clear-files",
                                        style={
                                            "color": "blue",
                                            "textDecoration": "underline",
                                        },
                                    ),
                                    html.Div(id="execute-recipe-upload-files-names"),
                                ]
                            ),
                            style={
                                "width": "100%",
                                "height": "200px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                            },
                            multiple=True,
                        ),
                    ]
                ),
            ]
        ),
        dbc.Button(
            "Save and Upload Data",
            id="execute-recipe-upload-data-button",
            className="mb-3",
            color="primary",
        ),
        html.Div(id="execute-recipe-upload-data-output"),
    ],
    className="container",
)


@callback(
    Output("execute-recipe-upload-files-names", "children"),
    Input("execute-recipe-upload-files", "filename"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def add_filenames_to_upload_box(filenames, url):
    if str(url) == "/execute-recipe":
        if filenames is None or filenames == []:
            return ""
        toRet = ""
        for i, filename in enumerate(filenames):
            if i < len(filenames) - 1:
                toRet += filename + ", "
            else:
                toRet += filename
        return toRet


@callback(
    Output("execute-recipe-upload-files", "filename"),
    Input("execute-recipe-clear-files", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def clear_selected_files(n, url):
    if str(url) == "/execute-recipe":
        return None
