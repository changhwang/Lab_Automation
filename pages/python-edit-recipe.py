from dash import Dash, html, dcc, dash_table
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
                        dbc.Button("Fill editor", id="refresh-button-ace", n_clicks=0),
                        dbc.Button("Add device", id="add-device-button-ace"),
                        dbc.Button("Add command", id="add-command-button"),
                        dbc.Button(
                            "Execute and save yaml",
                            id="execute-and-save-button",
                            n_clicks=0,
                        ),
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
                        dash_ace.DashAceEditor(
                            id="ace-recipe-editor",
                            mode="python",
                            enableBasicAutocompletion=True,
                            enableLiveAutocompletion=True,
                            theme="github",
                            wrapEnabled=True,
                            style={"width": "100%", "height": "550px"},
                        ),
                    ],
                    className="table-container",
                ),
                # html.Div(
                #     [
                #         html.H2("Commands"),
                #         dbc.Button("Refresh", id="refresh-button2", n_clicks=0),
                #         dbc.Button("Edit", id="edit-command-button"),
                #         dbc.Modal(
                #             [
                #                 dbc.ModalHeader(
                #                     dbc.ModalTitle("Editor"), close_button=False
                #                 ),
                #                 dbc.ModalBody(
                #                     [
                #                         dcc.Textarea(
                #                             id="command-json-editor",
                #                             style={
                #                                 "width": "100%",
                #                                 "height": "200px",
                #                                 "fontFamily": "monospace",
                #                                 "backgroundColor": "#f5f5f5",
                #                                 "border": "1px solid #ccc",
                #                                 "padding": "10px",
                #                                 "color": "#333",
                #                             },
                #                         ),
                #                         html.Div(
                #                             id="edit-command-error",
                #                             style={"color": "red"},
                #                         ),
                #                     ]
                #                 ),
                #                 dbc.ModalFooter(
                #                     dbc.Button("Save", id="save-command-editor")
                #                 ),
                #             ],
                #             id="command-editor-modal",
                #             keyboard=False,
                #             backdrop="static",
                #         ),
                #         html.Div(
                #             children=[dash_table.DataTable(id="commands-table")],
                #             id="commands-table-div",
                #         ),
                #         dbc.Accordion(
                #             [
                #                 dbc.AccordionItem(
                #                     "item1", title="Item 1", item_id="item1"
                #                 )
                #             ],
                #             id="commands-accordion",
                #             # start_collapsed=True,
                #             style={"display": "none"},
                #         ),
                #     ],
                #     className="table-container",
                # ),
            ],
            className="tables-container",
        ),
    ],
    className="main-container",
)
