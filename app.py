from command_sequence import CommandSequence
from command_invoker import CommandInvoker
import json
from devices.device import Device
from commands.command import Command, CompositeCommand
from devices.device import Device, SerialDevice


com = CommandSequence()


com.load_from_yaml("to_load.yaml")


import util
import ctypes
from mongodb_helper import MongoDBHelper
import pandas as pd

mongo = MongoDBHelper(
    "mongodb+srv://ppahuja2:s5eMFr1js8iEcMt8@diaogroup.nrcgqsq.mongodb.net/?retryWrites=true&w=majority",
    "diaogroup",
)


# out = util.device_to_dict(com.device_list[0])

import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output, State
import random
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("Edit Recipe", href="/edit-recipe")),
        dbc.NavItem(dbc.NavLink("Execute Recipe", href="/execute-recipe")),
    ],
    brand="AAMP",
    brand_href="/",
    color="primary",
    dark=True,
)

home_layout = html.Div(
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


@app.callback(
    Output("home-recipes-list-table", "data"),
    [Input("home-refresh-list-button", "n_clicks")],
    # prevent_initial_call=True,
)
def fetch_recipe_list(n_clicks):
    docs = mongo.find_documents("recipes", {})
    docs = mongo.db["recipes"].find({}, {"_id": 0, "file_name": 1})
    # print(pd.DataFrame(docs).to_dict('records'))
    print("recipe list refresh done")
    return pd.DataFrame(docs).to_dict("records")


@app.callback(
    Output("filename-input", "value"),
    Input("home-recipes-list-table", "active_cell"),
    State("home-recipes-list-table", "data"),
    prevent_initial_call=True,
)
def fill_filename_input(active_cell, data):
    if active_cell is not None:
        return data[active_cell["row"]]["file_name"]
    return ""


execute_recipe_layout = html.Div(
    [
        html.H1("Execute Recipe"),
        dbc.Button("Execute", id="execute-button", n_clicks=0),
        html.Div(id="execute-recipe-output"),
        dcc.Interval(id="update-interval", interval=1000, n_intervals=0),
        dcc.Textarea(
            id="console-output", readOnly=True, style={"width": "100%", "height": 200}
        ),
    ]
)


@app.callback(
    Output("execute-recipe-output", "children"),
    [Input("execute-button", "n_clicks")],
    prevent_initial_call=True,
)
def execute_recipe(n_clicks):
    invoker = CommandInvoker(com, False, None, False)
    return html.Div(str(invoker.invoke_commands()))


# import sys
# from io import StringIO
# stringio = StringIO()
# sys.stdout = stringio
# @app.callback(Output('console-output', 'value'), [Input('update-interval', 'n_intervals')])
# def show_console_output(n):
#     # Retrieve console output from StringIO object
#     stringio.seek(0)
#     console_output = stringio.read()
#     return console_output


@app.callback(
    Output("url", "pathname"),
    [Input("filename-input-button", "n_clicks")],
    [State("filename-input", "value")],
)
def get_document_from_db(n_clicks, filename):
    if filename is not None and filename != "":
        # Extract the YAML content from the document
        document = mongo.find_documents("recipes", {"file_name": filename})[0]
        yaml_content = document.get("yaml_data", "")
        # Update the YAML output
        with open("to_load.yaml", "w") as file:
            file.write(yaml_content)
        com.load_from_yaml("to_load.yaml")
        return "/edit-recipe"

    return "/"


edit_recipe_layout = html.Div(
    [
        html.H1("Edit Recipe"),
        html.Div(
            [
                html.Div(
                    [
                        html.H2("Devices"),
                        dbc.Button("Refresh", id="refresh-button1", n_clicks=0),
                        dbc.Button("Add device", id="add-device-button"),
                        dbc.Button("Edit", id="edit-device-button"),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(
                                    dbc.ModalTitle("Editor"), close_button=False
                                ),
                                dbc.ModalBody(
                                    [
                                        dcc.Textarea(
                                            id="device-json-editor",
                                            style={
                                                "width": "100%",
                                                "height": "200px",
                                                "fontFamily": "monospace",
                                                "backgroundColor": "#f5f5f5",
                                                "border": "1px solid #ccc",
                                                "padding": "10px",
                                                "color": "#333",
                                            },
                                        ),
                                        html.Div(
                                            id="edit-device-error",
                                            style={"color": "red"},
                                        ),
                                        html.Div(
                                            id="edit-device-serial-ports-info",
                                        ),
                                    ]
                                ),
                                dbc.ModalFooter(
                                    dbc.Button("Save", id="save-device-editor")
                                ),
                            ],
                            id="device-editor-modal",
                            keyboard=False,
                            backdrop="static",
                        ),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(dbc.ModalTitle("Add Device")),
                                dbc.ModalBody(
                                    [
                                        dcc.Dropdown(
                                            id="add-device-dropdown",
                                            options=[],
                                            value=None,
                                        ),
                                        dcc.Textarea(
                                            id="add-device-json-editor",
                                            style={
                                                "width": "100%",
                                                "height": "200px",
                                                "fontFamily": "monospace",
                                                "backgroundColor": "#f5f5f5",
                                                "border": "1px solid #ccc",
                                                "padding": "10px",
                                                "color": "#333",
                                            },
                                        ),
                                        html.Div(
                                            id="add-device-error",
                                            style={"color": "red"},
                                        ),
                                        html.Div(
                                            id="add-device-serial-ports-info",
                                        ),
                                    ]
                                ),
                                dbc.ModalFooter(
                                    dbc.Button("Add", id="add-device-editor")
                                ),
                            ],
                            id="device-add-modal",
                            keyboard=False,
                            backdrop="static",
                        ),
                        html.Div(
                            children=[dash_table.DataTable(id="devices-table")],
                            id="devices-table-div",
                        ),
                    ],
                    className="table-container",
                ),
                html.Div(
                    [
                        html.H2("Commands"),
                        dbc.Button("Refresh", id="refresh-button2", n_clicks=0),
                        dbc.Button("Add command", id="add-command-button"),
                        dbc.Button("Edit", id="edit-command-button"),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(
                                    dbc.ModalTitle("Editor"), close_button=False
                                ),
                                dbc.ModalBody(
                                    [
                                        dcc.Textarea(
                                            id="command-json-editor",
                                            style={
                                                "width": "100%",
                                                "height": "200px",
                                                "fontFamily": "monospace",
                                                "backgroundColor": "#f5f5f5",
                                                "border": "1px solid #ccc",
                                                "padding": "10px",
                                                "color": "#333",
                                            },
                                        ),
                                        html.Div(
                                            id="edit-command-error",
                                            style={"color": "red"},
                                        ),
                                    ]
                                ),
                                dbc.ModalFooter(
                                    dbc.Button("Save", id="save-command-editor")
                                ),
                            ],
                            id="command-editor-modal",
                            keyboard=False,
                            backdrop="static",
                        ),
                        html.Div(
                            children=[dash_table.DataTable(id="commands-table")],
                            id="commands-table-div",
                        ),
                        dbc.Accordion(
                            [
                                dbc.AccordionItem(
                                    "item1", title="Item 1", item_id="item1"
                                )
                            ],
                            id="commands-accordion",
                            # start_collapsed=True,
                            style={"display": "none"},
                        ),
                    ],
                    className="table-container",
                ),
                html.Div(
                    [
                        html.H2("Command Iterations"),
                        html.Button("Refresh", id="refresh-button3", n_clicks=0),
                        html.Div(id="table-container3"),
                    ],
                    className="table-container",
                ),
            ],
            className="tables-container",
        ),
    ],
    className="main-container",
)

app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), navbar, html.Div(id="page-content")]
)


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    print("\n\nrefreshing to " + pathname)
    if pathname == "/":
        return home_layout
    elif pathname == "/edit-recipe":
        return edit_recipe_layout
    elif pathname == "/execute-recipe":
        return execute_recipe_layout
    else:
        return html.Div("404")


data_list4 = com.device_list

# dl5 = []
# for list in data_list4:
#     dl5.append(list.__dict__)

# print(dl5[2]['motor'].__dict__)


@app.callback(
    Output("devices-table-div", "children"),
    [Input("refresh-button1", "n_clicks"), Input("devices-table", "data")],
    [State("devices-table-div", "children")],
)
def update_table1(n_clicks, data, table):
    # dl5 = dl5_og.copy()
    # dl5_props_temp = {}
    # count = 0
    # for list in dl5:
    #     dl5_props_temp.clear()
    #     if len(list) > 1:
    #         for prop in list:
    #             if prop != "_name":
    #                 dl5_props_temp[prop] = list[prop]
    #                 # print(prop)
    #         # print("h")
    #         dl5_temp_list = list
    #         dl5[count] = {}
    #         dl5[count]["_name"] = dl5_temp_list["_name"]
    #         # dl5[count]["_is_initialized"] = dl5_temp_list["_is_initialized"]
    #         dl5[count]["props"] = str(dl5_props_temp)
    #         # print(str(dl5_props_temp))
    #     count += 1

    # table_data1 = dl5
    table_data1 = com.get_clean_device_list().copy()
    # print(com.device_list[1].get_init_args())
    table_data1_new = []
    for index, list in enumerate(table_data1):
        # table_data1[index][1].update({"device_type": table_data1[index][0]})
        # del table_data1[index][0]
        table_data1_new.append(
            {
                "index": index,
                "device_type": table_data1[index][0],
                "params": str(table_data1[index][1]),
            }
        )

    table_data1 = table_data1_new

    table = dash_table.DataTable(
        id="devices-table",
        data=table_data1,
        columns=[
            {"name": "Index", "id": "index"},
            {"name": "Type", "id": "device_type"},
            # {"name": "Initialized", "id": "_is_initialized"},
            {"name": "Parameters", "id": "params"},
        ],
        # style_data_conditional=[
        #     {"if": {"column_id": "_name"}, "width": "250px", 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
        #     # {"if": {"column_id": "_is_initialized"}, "width": "20%"},
        #     # {"if": {"column_id": "props"}, "width": "100px", 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
        # ],
        # style_cell={"textAlign": "left", "padding": "5px"},
        style_cell={
            "overflow": "hidden",
            "textOverflow": "ellipsis",
            "maxWidth": 0,
            "textAlign": "left",
            "padding": "5px",
        },
        style_cell_conditional=[
            {"if": {"column_id": "index"}, "width": "5%"},
            {"if": {"column_id": "device_type"}, "width": "20%"},
            {"if": {"column_id": "params"}, "width": "70%"},
        ],
        # tooltip_data=[
        #     {
        #         column: {"value": str(value), "type": "markdown"}
        #         for column, value in row.items()
        #     }
        #     for row in table_data1
        # ],
        # tooltip_duration=None,
        # editable = True,
    )
    print("devices table refresh done")
    return table


@app.callback(
    Output("device-editor-modal", "is_open"),
    [Input("edit-device-button", "n_clicks"), Input("save-device-editor", "n_clicks")],
    [State("device-editor-modal", "is_open")],
)
def toggle_device_editor_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("device-add-modal", "is_open"),
    [Input("add-device-button", "n_clicks"), Input("add-device-editor", "n_clicks")],
    [State("device-add-modal", "is_open")],
)
def toggle_device_add_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("command-editor-modal", "is_open"),
    [
        Input("edit-command-button", "n_clicks"),
        Input("save-command-editor", "n_clicks"),
    ],
    [State("command-editor-modal", "is_open")],
)
def toggle_command_editor_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("commands-table", "data"),
    Input("save-command-editor", "n_clicks"),
    [
        State("commands-table", "active_cell"),
        State("commands-table", "data"),
        State("command-json-editor", "value"),
    ],
    prevent_initial_call=True,
)
def save_command(n_clicks, active_cell, data, value):
    if active_cell is not None and data[active_cell["row"]]["params"] != str(
        json.loads(value)
    ):
        # data[active_cell['row']]['params'] = str(json.loads(value))
        # com.command_list[data[active_cell['row']]['index']]
        # print(data[active_cell['row']]['params'])
        # print((eval(value)))

        com.command_list[data[active_cell["row"]]["index"]][0]._params = eval(value)
        # print((com.command_list[data[active_cell['row']]['index']][0]._params))
        # print(com.get_unlooped_command_list()[active_cell['row']])
        return None
    return data


@app.callback(
    Output("devices-table", "data"),
    Input("save-device-editor", "n_clicks"),
    [
        State("devices-table", "active_cell"),
        State("devices-table", "data"),
        State("device-json-editor", "value"),
    ],
    prevent_initial_call=True,
)
def save_device(n_clicks, active_cell, data, value):
    if active_cell is not None and data[active_cell["row"]]["params"] != str(
        json.loads(value)
    ):
        # data_row = data[active_cell["row"]]
        params = eval(value)
        # print(com.device_by_name[params['name']])
        # init_str = data_row['device_type'] + '('
        # for key, value2 in params.items():
        #     if isinstance(value2, str):
        #         init_str += key + '=' + "'" + str(value2) + "'" + ','
        #     else:
        #         init_str += key + '=' + str(value2) + ','
        # init_str = init_str[:-1] + ')'
        com.device_by_name[params["name"]].update_init_args(params)
        return None
    return data


@app.callback(
    Output("command-json-editor", "value"),
    [Input("command-editor-modal", "is_open")],
    [State("commands-table", "active_cell"), State("commands-table", "data")],
    prevent_initial_call=True,
)
def fill_command_json_editor(is_open, active_cell, data):
    if active_cell is not None and is_open:
        # print(active_cell)
        # print(eval(data[active_cell['row']]['params']))
        return json.dumps(eval(data[active_cell["row"]]["params"]), indent=4)

    return ""


@app.callback(
    [
        # Output("add-device-json-editor", "value"),
        Output("add-device-dropdown", "options"),
    ],
    [Input("device-add-modal", "is_open")],
    [State("devices-table", "active_cell"), State("devices-table", "data")],
    prevent_initial_call=True,
)
def fill_device_add_modal(is_open, active_cell, data):
    return [util.approved_devices]

import inspect

@app.callback(
    [Output('add-device-json-editor', 'value')],
    [Input('add-device-dropdown', 'value'), Input('device-add-modal', 'is_open')],
    prevent_initial_call=True
)
def fill_device_add_json_editor(value, is_open):
    if not is_open or value is None:
        return [""]
    args_list = inspect.getfullargspec(util.named_devices[value].__init__).args
    args_dict = {}
    for arg in args_list:
        if arg != 'self' and arg != 'name':
            args_dict[arg] = None
        if arg == 'name':
            args_dict[arg] = value
    return [(json.dumps(args_dict, indent=4))]


try:
    import serial.tools.list_ports
except ImportError:
    _has_serial = False
else:
    _has_serial = True


@app.callback(
    [
        Output("device-json-editor", "value"),
        Output("edit-device-serial-ports-info", "children"),
    ],
    [Input("device-editor-modal", "is_open")],
    [State("devices-table", "active_cell"), State("devices-table", "data")],
    prevent_initial_call=True,
)
def fill_device_json_editor(is_open, active_cell, data):
    if active_cell is not None and is_open:
        if _has_serial and isinstance(
            com.device_by_name[eval(data[active_cell["row"]]["params"])["name"]],
            SerialDevice,
        ):
            ports = serial.tools.list_ports.comports()
            str_ports = ""
            for port, desc, hwid in sorted(ports):
                str_ports += f"{port}: {desc} [{hwid}]\n"
            lines = str_ports.splitlines()
            device_port_html = [
                html.Div(["COM Port Info:"], style={"font-weight": "bold"})
            ]
            device_port_html.append(html.Div([html.Div(line) for line in lines]))
        else:
            device_port_html = ""
        return (
            json.dumps(eval(data[active_cell["row"]]["params"]), indent=4),
            device_port_html,
        )
    return "", ""


@app.callback(
    [
        Output("save-command-editor", "disabled"),
        Output("edit-command-error", "children"),
    ],
    Input("command-json-editor", "value"),
    State("command-editor-modal", "is_open"),
    prevent_initial_call=True,
)
def enable_save_command_button(value, is_open):
    if not is_open:
        return False, ""
    try:
        parsed_json = json.loads(value)
        # print(type(parsed_json))
        # print(parsed_json)
        if parsed_json["delay"] < 0:
            return True, "Delay must be greater than or equal to 0"
        return False, ""
    except Exception as e:
        if type(e) == json.decoder.JSONDecodeError:
            return True, "Invalid JSON"
        return True, str(type(e))


@app.callback(
    [Output("save-device-editor", "disabled"), Output("edit-device-error", "children")],
    Input("device-json-editor", "value"),
    State("device-editor-modal", "is_open"),
    prevent_initial_call=True,
)
def enable_save_device_button(value, is_open):
    if not is_open:
        return False, ""
    try:
        parsed_json = json.loads(value)
        return False, ""
    except Exception as e:
        if type(e) == json.decoder.JSONDecodeError:
            return True, "Invalid JSON"
        return True, str(type(e))

import typing

@app.callback(
    [Output("add-device-editor", "disabled"), Output("add-device-error", "children")],
   [ Input("add-device-json-editor", "value"), Input('add-device-dropdown', 'value')],
    State("device-add-modal", "is_open"),
    prevent_initial_call=True,
)
def enable_add_device_button(value, device_type, is_open):
    if value == "":
        return True, "No device selected"
    if not is_open:
        return False, ""
    try:
        sig = inspect.signature(util.named_devices[device_type].__init__)
        args = {}
        for param in sig.parameters.values():
            arg_type = param.annotation
            args[param.name] = typing.get_args(arg_type)[0] if typing.get_origin(arg_type) is typing.Union else arg_type
        parsed_json = json.loads(value)
        for key in parsed_json:
            print('\n'+key)
            print('input: '+str(type((parsed_json[key]))) + ', expected: '+ str(args[key]))
            if type((parsed_json[key])) != args[key]:
                return True, f"Invalid type for {key}. Expected {str(args[key])}"
            # if not isinstance(parsed_json[key], args[key]):
            #     return True, f"Invalid type for {key}. Expected {str(args[key])}"
        return False, ""
    except Exception as e:
        if type(e) == json.decoder.JSONDecodeError:
            return True, "Invalid JSON"
        return True, str(type(e))


# @app.callback(
#         Output("commands-accordion", "children"),
#         Input("add-command-button", "n_clicks"),
#         State("commands-accordion", "children"),
#         prevent_initial_call=True,
#         allow_duplicate=True
# )
# def add_command_accordian(n_clicks, children):
#     children=[
#         dbc.AccordionItem(
#             "new item", title="new title", item_id="new")
#     ]

#     return children


@app.callback(
    Output("commands-accordion", "children"),
    Input("refresh-button2", "n_clicks"),
    State("commands-accordion", "children"),
    # allow_duplicate=True
)
def load_commands_accordion(n_clicks, children):
    children = []
    # print()
    command_list = com.get_unlooped_command_list().copy()
    # print(command_list)
    # for command in command_list:
    #     if isinstance(command, CompositeCommand):
    #         for sub_command in command._command_list:
    #             sub_command._receiver = sub_command._receiver._name
    #             sub_command = sub_command.__dict__
    #     else:
    #         # print(command.__dict__)
    #         command._receiver = command._receiver._name
    command_params = []
    for command in command_list:
        # if isinstance(command, CompositeCommand):
        # print(type(command).__name__)
        temp_dict_command_params = {"command": type(command).__name__}
        temp_dict_command_params.update({"params": command.get_init_args()})
        command_params.append(temp_dict_command_params)
        # print(command._params)
        # else:
        #     command_params.append(command._params)
    # print(command_params)
    # print(com.get_command_names())
    for index, command in enumerate(command_params):
        # print(command)
        children.append(
            dbc.AccordionItem(
                dcc.Markdown(
                    children=[
                        "**Command Object:**",
                        "```json",
                        json.dumps(command, indent=4, cls=util.Encoder),
                        # str(command.__dict__),
                        "```",
                    ],
                ),
                # str(command.__dict__),
                title=command["command"],
                item_id=command["command"] + str(index),
            )
        )
    return children


@app.callback(
    Output("edit-command-button", "disabled"),
    Input("commands-table", "active_cell"),
)
def edit_command_button(table_div_children):
    active_cell = table_div_children
    # print(active_cell)
    # if active_cell is not None and active_cell["column_id"] == "params":
    if active_cell is not None:
        return False
    else:
        return True


@app.callback(
    Output("edit-device-button", "disabled"),
    Input("devices-table", "active_cell"),
)
def edit_device_button(table_div_children):
    active_cell = table_div_children
    if active_cell is not None:
        return False
    else:
        return True


@app.callback(
    Output("commands-table-div", "children"),
    [Input("refresh-button2", "n_clicks"), Input("commands-table", "data")],
    [State("commands-table-div", "children")],
)
def update_table2(n_clicks, data, table):
    command_list = com.command_list.copy()
    # print(command_list)
    # for command in command_list:
    #     if isinstance(command, CompositeCommand):
    #         for sub_command in command._command_list:
    #             sub_command._receiver = sub_command._receiver._name
    #             sub_command = sub_command.__dict__
    #     else:
    #         # print(command.__dict__)
    #         command._receiver = command._receiver._name
    command_params = []
    for index, command in enumerate(command_list):
        # if isinstance(command, CompositeCommand):
        # print(type(command).__name__)
        temp_dict_command_params = {"command": type(command[0]).__name__}
        temp_dict_command_params.update(
            {"params": str(command[0].get_init_args()), "index": index}
        )
        command_params.append((temp_dict_command_params))
        # print(command._params)
        # else:
        #     command_params.append(command._params)
    # print(command_params)

    # print(command_params)
    table_data2 = command_params
    # print(com.get_unlooped_command_list().copy()[3].__dict__)
    # add_command_accordian(0, to_add=[dbc.AccordionItem("new new", title="new new", item_id="new new")])

    table = dash_table.DataTable(
        id="commands-table",
        data=table_data2,
        columns=[
            {"name": "Index", "id": "index"},
            {"name": "Command", "id": "command"},
            {"name": "Parameters", "id": "params"},
        ],
        style_cell={
            "overflow": "hidden",
            "textOverflow": "ellipsis",
            "maxWidth": 0,
            "textAlign": "left",
            "padding": "5px",
        },
        style_cell_conditional=[
            {"if": {"column_id": "index"}, "width": "5%"},
            {"if": {"column_id": "command"}, "width": "20%"},
            {"if": {"column_id": "params"}, "width": "70%"},
        ],
        # tooltip_data=[
        #     {
        #         column: {"value": str(value), "type": "markdown"}
        #         for column, value in row.items()
        #     }
        #     for row in table_data2
        # ],
        # tooltip_duration=None,
        # editable = True,
    )
    print("commands table refresh done")
    return table


# @app.callback(
#     Output("table-container3", "children"),
#     [Input("refresh-button3", "n_clicks")],
#     [State("table-container3", "children")],
# )
# def update_table3(n_clicks, table):
#     table_data3 = data_list3
#     table = dash_table.DataTable(
#         data=table_data3,
#         columns=[{"name": "Name", "id": "Name"}, {"name": "Value", "id": "Value"}],
#     )
#     return table


if __name__ == "__main__":
    app.run_server(debug=True)
