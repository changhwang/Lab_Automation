from dash import Dash, html, dcc, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc
import dash
import dash_ace

dash.register_page(__name__, "/python-edit-recipe")

layout = html.Div(
    [
        html.H1("Edit Recipe in Python"),
        html.Div(
            [
                html.Div(
                    [
                        dbc.Alert(
                            "Alert", id="ace-editor-alert", is_open=False, duration=500
                        ),
                        dbc.ButtonGroup([dbc.Button("Fill editor", id="refresh-button-ace", n_clicks=0),
                        dbc.Button("Add device", id="add-device-button-ace"),
                        dbc.Button("Add command", id="add-command-button-ace"),
                        dbc.Button(
                            "Execute and save yaml",
                            id="execute-and-save-button",
                            n_clicks=0,
                        ),], className='mb-3'),
                        
                        dbc.Modal(
                            [
                                dbc.ModalHeader(dbc.ModalTitle("Add Device")),
                                dbc.ModalBody(
                                    [
                                        dcc.Dropdown(
                                            id="add-device-dropdown-ace",
                                            options=[],
                                            value=None,
                                        ),
                                    ]
                                ),
                                dbc.ModalFooter(
                                    dbc.Button("Add", id="add-device-editor-ace")
                                ),
                            ],
                            id="device-add-modal-ace",
                            keyboard=False,
                            backdrop="static",
                        ),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(dbc.ModalTitle("Add Command")),
                                dbc.ModalBody(
                                    [
                                        dcc.Dropdown(
                                            id="add-command-device-dropdown-ace",
                                            options=[],
                                            value=None,
                                        ),
                                    ]
                                ),
                                dbc.ModalBody(
                                    [
                                        dcc.Dropdown(
                                            id="add-command-command-dropdown-ace",
                                            options=[],
                                            value=None,
                                        ),
                                    ]
                                ),
                                dbc.ModalFooter(
                                    dbc.Button("Add", id="add-command-editor-ace")
                                ),
                            ],
                            id="command-add-modal-ace",
                            keyboard=False,
                            backdrop="static",
                        ),
                        dash_ace.DashAceEditor(
                            id="ace-recipe-editor",
                            mode="python",
                            enableBasicAutocompletion=True,
                            enableLiveAutocompletion=True,
                            theme="github",
                            wrapEnabled=True,
                            style={"width": "100%", "height": "550px"},
                            cursorStart=333
                        ),
                    ],
                    className="table-container",
                ),
            ],
            className="tables-container",
        ),
    ],
    className="container",
)

@callback(
    Output("command-add-modal-ace", "is_open"),
    [
        Input("add-command-editor-ace", "n_clicks"),
        Input("add-command-button-ace", "n_clicks"),
    ],
    State("command-add-modal-ace", "is_open"),
)
def toggle_command_add_modal_ace(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@callback(
    Output("device-add-modal-ace", "is_open"),
    [
        Input("add-device-button-ace", "n_clicks"),
        Input("add-device-editor-ace", "n_clicks"),
    ],
    [State("device-add-modal-ace", "is_open")],
)
def toggle_device_add_modal_ace(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


