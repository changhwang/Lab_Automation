from command_sequence import CommandSequence
from command_invoker import CommandInvoker
import json
from devices.device import SerialDevice
import util
from mongodb_helper import MongoDBHelper
import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import os, signal
import inspect
from pw import mongo_username, mongo_password

try:
    import serial.tools.list_ports
except ImportError:
    _has_serial = False
else:
    _has_serial = True
import typing


print("\nreset complete")
com = CommandSequence()
invoker = CommandInvoker(com, log_to_file=True, log_filename="mylog.log")
invoker.clear_log_file()
invoker.invoking = False
com.load_from_yaml("blank.yaml")


mongo = MongoDBHelper(
    "mongodb+srv://"+mongo_username+":"+mongo_password+"@diaogroup.nrcgqsq.mongodb.net/?retryWrites=true&w=majority",
    "diaogroup",
)

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    use_pages=True,
    prevent_initial_callbacks="initial_duplicate",
)
server = app.server

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("View Recipe", href="/view-recipe")),
        dbc.NavItem(dbc.NavLink("Edit Recipe", href="/python-edit-recipe")),
        dbc.NavItem(dbc.NavLink("Execute Recipe", href="/execute-recipe")),
        dbc.NavItem(dbc.NavLink("Manual Control", href="/manual-control")),
        dbc.NavItem(dbc.NavLink("Document", href="/data")),
        dbc.NavItem(dbc.NavLink("Database", href="/database")),
    ],
    brand="AAMP",
    brand_href="/",
    color="primary",
    dark=True,
    id="navbar",
    className="mb-3",
)


app.layout = html.Div([dcc.Location(id="url"), navbar, dash.page_container])


@app.callback(Output("navbar", "brand"), Input("url", "pathname"))
def print_pagename(url):  # all pages
    print("loading: " + url + "\n")
    return "AAMP"


# ---------------------------------------------------
# Home Page
# ---------------------------------------------------


@app.callback(
    Output("home-recipes-list-table", "data"),
    [Input("home-refresh-list-button", "n_clicks")],
    # prevent_initial_call=True,
)
def fetch_recipe_list(n_clicks):  # homepage
    docs = mongo.find_documents("recipes", {})
    docs = mongo.db["recipes"].find(
        {},
        {
            "_id": 0,
            "file_name": 1,
            "posix_friendly": 1,
            "dash_friendly": 1,
            "python_code": 1,
        },
    )
    print("fetch_recipe_list")
    data = []
    for doc in docs:
        file_name = doc.get("file_name", "")
        posix_friendly = doc.get("posix_friendly", True)
        dash_friendly = doc.get("dash_friendly", False)
        if "python_code" in doc:
            python_code = True
        else:
            python_code = False
        data.append(
            {
                "file_name": file_name,
                "posix_friendly": posix_friendly,
                "dash_friendly": dash_friendly,
                "python_code": python_code,
            }
        )
    return data


@app.callback(
    Output("filename-input", "value"),
    Input("home-recipes-list-table", "active_cell"),
    State("home-recipes-list-table", "data"),
    # prevent_initial_call=True,
)
def fill_filename_input(active_cell, data):  # homepage
    if active_cell is not None:
        print("fill_filename_input")
        return data[active_cell["row"]]["file_name"]
    if hasattr(com, "document"):
        print("fill_filename_input")
        return com.document["file_name"]
    return ""


@app.callback(
    [
        Output("home-load-file-alert", "is_open"),
        Output("home-load-file-alert", "children"),
        Output("home-load-file-alert", "color"),
        Output("home-load-file-alert", "duration"),
    ],
    [Input("filename-input-button", "n_clicks")],
    [State("filename-input", "value")],
    prevent_initial_call=True,
)
def get_document_from_db(n_clicks, filename):  # homepage
    print("get_document_from_db")
    if filename is not None and filename != "":
        # Extract the YAML content from the document
        document = mongo.find_documents("recipes", {"file_name": filename})[0]
        invoker.clear_log_file()
        if os.name == "posix":
            if "posix_friendly" in document and not document["posix_friendly"]:
                return [
                    True,
                    "This recipe is not compatible with your system (POSIX compatability error)",
                    "danger",
                    8000,
                ]
        if (
            document.get("dash_friendly", "") == False
            or document.get("python_code", "") == ""
        ):
            yaml_content = document.get("yaml_data", "")
            # Update the YAML output
            with open("to_load.yaml", "w") as file:
                file.write(yaml_content)
            com.load_from_yaml("to_load.yaml")
            com.document = document
            return [True, "Recipe loaded", "success", 10000]
        else:
            exec(document.get("python_code", ""))
            com.load_from_yaml("to_save.yaml")
            com.document = document

        # com.python_code = document.get("python_code", "")

        return [True, "Recipe loaded", "success", 10000]

    return [True, "No recipe selected", "warning", 3000]


# ---------------------------------------------------
# View Recipe Page
# ---------------------------------------------------


@app.callback(
    Output("devices-table-div", "children"),
    [Input("refresh-button1", "n_clicks"), Input("devices-table", "data")],
    [State("devices-table-div", "children")],
)
def update_device_table(n_clicks, data, table):  # view-recipe page
    print("update_device_table")
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
    return table


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
def save_command(n_clicks, active_cell, data, value):  # view-recipe page
    print("save_command")
    if active_cell is not None and data[active_cell["row"]]["params"] != str(
        json.loads(value)
    ):
        com.command_list[data[active_cell["row"]]["index"]][0]._params = eval(value)
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
def save_device(n_clicks, active_cell, data, value):  # view-recipe page
    print("save_device")
    if active_cell is not None and data[active_cell["row"]]["params"] != str(
        json.loads(value)
    ):
        # data_row = data[active_cell["row"]]
        params = eval(value)
        com.device_by_name[params["name"]].update_init_args(params)
        return None
    return data


@app.callback(
    Output("command-json-editor", "value"),
    [Input("command-editor-modal", "is_open")],
    [State("commands-table", "active_cell"), State("commands-table", "data")],
    prevent_initial_call=True,
)
def fill_command_json_editor(is_open, active_cell, data):  # view-recipe page
    if active_cell is not None and is_open:
        print("fill_command_json_editor")
        return json.dumps(eval(data[active_cell["row"]]["params"]), indent=4)

    return ""


@app.callback(
    Output("add-device-dropdown", "options"),
    [Input("device-add-modal", "is_open")],
    [State("devices-table", "active_cell"), State("devices-table", "data")],
    prevent_initial_call=True,
)
def fill_device_add_modal(is_open, active_cell, data):  # view-recipe page
    print("fill_device_add_modal")
    return util.approved_devices


@app.callback(
    [Output("add-device-json-editor", "value")],
    [Input("add-device-dropdown", "value"), Input("device-add-modal", "is_open")],
    prevent_initial_call=True,
)
def fill_device_add_json_editor(value, is_open):  # view-recipe page
    print("fill_device_add_json_editor")
    if not is_open or value is None:
        return [""]
    args_list = inspect.getfullargspec(util.named_devices[value].__init__).args
    args_dict = {}
    for arg in args_list:
        if arg != "self" and arg != "name":
            args_dict[arg] = None
        if arg == "name":
            args_dict[arg] = value
    return [(json.dumps(args_dict, indent=4))]


@app.callback(
    [
        Output("device-json-editor", "value"),
        Output("edit-device-serial-ports-info", "children"),
    ],
    [Input("device-editor-modal", "is_open")],
    [State("devices-table", "active_cell"), State("devices-table", "data")],
    prevent_initial_call=True,
)
def fill_device_json_editor(is_open, active_cell, data):  # view-recipe page
    print("fill_device_json_editor")
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
def enable_save_command_button(value, is_open):  # view-recipe page
    if not is_open:
        return False, ""
    try:
        parsed_json = json.loads(value)
        if parsed_json["delay"] < 0:
            return True, "Delay must be greater than or equal to 0"
        print("enable_save_command_button")
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
def enable_save_device_button(value, is_open):  # view-recipe page
    if not is_open:
        return False, ""
    try:
        parsed_json = json.loads(value)
        print("enable_save_device_button")
        return False, ""
    except Exception as e:
        if type(e) == json.decoder.JSONDecodeError:
            return True, "Invalid JSON"
        return True, str(type(e))


@app.callback(
    [Output("add-device-editor", "disabled"), Output("add-device-error", "children")],
    [Input("add-device-json-editor", "value"), Input("add-device-dropdown", "value")],
    State("device-add-modal", "is_open"),
    prevent_initial_call=True,
)
def enable_add_device_button(value, device_type, is_open):  # view-recipe page
    if value == "":
        return True, "No device selected"
    if not is_open:
        return False, ""
    try:
        sig = inspect.signature(util.named_devices[device_type].__init__)
        args = {}
        for param in sig.parameters.values():
            arg_type = param.annotation
            args[param.name] = (
                typing.get_args(arg_type)[0]
                if typing.get_origin(arg_type) is typing.Union
                else arg_type
            )
        parsed_json = json.loads(value)
        for key in parsed_json:
            print("\n" + key)
            print(
                "input: "
                + str(type((parsed_json[key])))
                + ", expected: "
                + str(args[key])
            )
            if type((parsed_json[key])) != args[key]:
                return True, f"Invalid type for {key}. Expected {str(args[key])}"
            # if not isinstance(parsed_json[key], args[key]):
            #     return True, f"Invalid type for {key}. Expected {str(args[key])}"
        print("enable_add_device_button")
        return False, ""
    except Exception as e:
        if type(e) == json.decoder.JSONDecodeError:
            return True, "Invalid JSON"
        return True, str(type(e))


@app.callback(
    Output("edit-command-button", "disabled"),
    Input("commands-table", "active_cell"),
)
def edit_command_button(table_div_children):  # view-recipe page
    active_cell = table_div_children
    if active_cell is not None:
        print("edit_command_button")
        return False
    else:
        return True


@app.callback(
    Output("edit-device-button", "disabled"),
    Input("devices-table", "active_cell"),
)
def edit_device_button(table_div_children):  # view-recipe page
    print("edit_device_button")
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
def update_commands_table(n_clicks, data, table):  # view-recipe page
    print("update_commands_table")
    command_list = com.command_list.copy()
    command_params = []
    for index, command in enumerate(command_list):
        temp_dict_command_params = {"command": type(command[0]).__name__}
        temp_dict_command_params.update(
            {"params": str(command[0].get_init_args()), "index": index}
        )
        command_params.append((temp_dict_command_params))
        # else:
        #     command_params.append(command._params)

    table_data2 = command_params
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
    return table


# ---------------------------------------------------
# Python Edit Recipe Page
# ---------------------------------------------------


@app.callback(
    [
        Output("ace-recipe-editor", "value", allow_duplicate=True),
        Output("ace-editor-alert", "is_open"),
        Output("ace-editor-alert", "children"),
        Output("ace-editor-alert", "color"),
        Output("ace-editor-alert", "duration"),
    ],
    [Input("refresh-button-ace", "n_clicks")],
    State("url", "pathname"),
    # prevent_initial_call=True,
)
def fill_ace_editor(n, url):  # python-edit-recipe page
    if url == "/python-edit-recipe":
        if hasattr(com, "document"):
            python_code = com.document.get("python_code", "")
            if python_code is not None and python_code != "":
                print("fill_ace_editor")
                return [str(python_code), True, "Loaded!", "success", 1500]
            else:
                print("fill_ace_editor")
                return ["", True, "No code available", "warning", 1000]
        else:
            return ["", True, "No code available", "warning", 1000]
    else:
        return ["", False, "na", "success", 0]


@app.callback(
    [
        Output("ace-recipe-editor", "value", allow_duplicate=True),
        Output("ace-editor-alert", "is_open", allow_duplicate=True),
        Output("ace-editor-alert", "children", allow_duplicate=True),
        Output("ace-editor-alert", "color", allow_duplicate=True),
        Output("ace-editor-alert", "duration", allow_duplicate=True),
    ],
    Input("execute-and-save-button", "n_clicks"),
    [State("ace-recipe-editor", "value")],
    prevent_initial_call=True,
)
def execute_and_save(n, value):  # python-edit-recipe page
    print("execute_and_save")
    if value is not None and value != "":
        try:
            exec(value)
            doc_id = com.document.get("_id", "")
            (mongo.update_yaml_file("recipes", doc_id, {"python_code": value}))
            com.load_from_yaml("to_save.yaml")
            com.document = mongo.find_documents("recipes", {"_id": doc_id})[0]
            return [str(value), True, "Saved!", "success", 1500]
        except Exception as e:
            return [str(value), True, str(e), "danger", 5000]
    else:
        return ["", True, "No code to execute", "warning", 1000]

    # return ["", False, "", "success", 1500]


@app.callback(
    [
        Output("add-device-dropdown-ace", "options"),
        Output("add-device-dropdown-ace", "value"),
    ],
    [Input("device-add-modal-ace", "is_open")],
    prevent_initial_call=True,
)
def fill_device_add_modal_ace(is_open):  # python-edit-recipe page
    if is_open:
        print("fill_device_add_modal_ace")
        return list(util.devices_ref_redundancy.keys()), ""
    return [], ""


@app.callback(
    [
        Output("add-command-device-dropdown-ace", "options"),
        Output("add-command-device-dropdown-ace", "value"),
    ],
    [Input("command-add-modal-ace", "is_open")],
    prevent_initial_call=True,
)
def fill_command_device_add_modal_ace(is_open):  # python-edit-recipe page
    if is_open:
        print("fill_command_device_add_modal_ace")
        return list(util.devices_ref_redundancy.keys()), ""
    return [], ""


@app.callback(
    [
        Output("add-command-command-dropdown-ace", "options"),
        Output("add-command-command-dropdown-ace", "value"),
    ],
    [Input("add-command-device-dropdown-ace", "value")],
    prevent_initial_call=True,
)
def fill_command_add_modal_ace(device):  # python-edit-recipe page
    if device is not None and device != "":
        print("fill_command_add_modal_ace")
        return list(util.devices_ref_redundancy[device]["commands"].keys()), ""
    return [], ""


@app.callback(
    Output("add-device-editor-ace", "disabled"),
    [
        Input("add-device-dropdown-ace", "value"),
        Input("device-add-modal-ace", "is_open"),
    ],
    State("device-add-modal-ace", "is_open"),
    prevent_initial_call=True,
)
def enable_add_device_button_ace(value, is_openInp, is_open):  # python-edit-recipe page
    if value == "" or value is None:
        return True
    print("enable_add_device_button_ace")
    return False


@app.callback(
    Output("add-command-editor-ace", "disabled"),
    [
        Input("add-command-command-dropdown-ace", "value"),
        Input("command-add-modal-ace", "is_open"),
    ],
    State("command-add-modal-ace", "is_open"),
    prevent_initial_call=True,
)
def enable_add_command_button_ace(
    value, is_openInp, is_open
):  # python-edit-recipe page
    if value == "" or value is None:
        return True
    print("enable_add_command_button_ace")
    return False


@app.callback(
    [
        Output("ace-recipe-editor", "value"),
        Output("ace-editor-alert", "is_open", allow_duplicate=True),
        Output("ace-editor-alert", "children", allow_duplicate=True),
        Output("ace-editor-alert", "color", allow_duplicate=True),
        Output("ace-editor-alert", "duration", allow_duplicate=True),
    ],
    Input("add-device-editor-ace", "n_clicks"),
    [State("ace-recipe-editor", "value"), State("add-device-dropdown-ace", "value")],
    prevent_initial_call=True,
)
def add_device_to_recipe_ace(n_clicks, value, device_type):  # python-edit-recipe page
    print("add_device_to_recipe_ace")
    if value == "" or value is None:
        return ["", True, "No code in editor", "warning", 3000]
    try:
        value = str(value)
        import_line = util.devices_ref_redundancy[device_type]["import_device"]
        init_line = util.devices_ref_redundancy[device_type]["init"]['default_code']
        if import_line not in value:
            value = import_line + "\n" + value
        value = value.replace(
            "##################################################\n##### Add commands to the command sequence",
            "seq.add_device("
            + init_line
            + ")\n\n##################################################\n##### Add commands to the command sequence",
        )
        return [str(value), True, "Device added successfully", "success", 3000]
    except Exception as e:
        print(e)
        return [str(value), True, "Error adding device: " + str(e), "danger", 6000]


@app.callback(
    [
        Output("ace-recipe-editor", "value", allow_duplicate=True),
        Output("ace-editor-alert", "is_open", allow_duplicate=True),
        Output("ace-editor-alert", "children", allow_duplicate=True),
        Output("ace-editor-alert", "color", allow_duplicate=True),
        Output("ace-editor-alert", "duration", allow_duplicate=True),
    ],
    Input("add-command-editor-ace", "n_clicks"),
    [
        State("ace-recipe-editor", "value"),
        State("add-command-command-dropdown-ace", "value"),
        State("add-command-device-dropdown-ace", "value"),
    ],
    prevent_initial_call=True,
)
def add_commands_to_recipe_ace(
    n_clicks, value, command, device_type
):  # python-edit-recipe page
    print("add_commands_to_recipe_ace")
    og_value = str(value)
    if value == "" or value is None:
        return ["", True, "No code in editor", "warning", 3000]
    try:
        value = str(value)
        command_line = util.devices_ref_redundancy[device_type]["commands"][command]['default_code']
        import_line = util.devices_ref_redundancy[device_type]["import_commands"]
        import_device_line = util.devices_ref_redundancy[device_type]["import_device"]
        if import_device_line not in value:
            raise Exception(
                "Device (or its import '"
                + import_device_line
                + "') not found in recipe"
            )
        if import_line not in value:
            value = import_line + "\n" + value
        if "\nrecipe_file = 'to_save.yaml'\nseq.save_to_yaml(recipe_file)" not in value:
            raise Exception("Code is not in valid format")
        value = value.replace(
            "\nrecipe_file = 'to_save.yaml'\nseq.save_to_yaml(recipe_file)",
            "\nseq.add_command("
            + command_line
            + ")\n\n\nrecipe_file = 'to_save.yaml'\nseq.save_to_yaml(recipe_file)",
        )
        return [str(value), True, "Command added successfully", "success", 3000]
    except Exception as e:
        print(e)
        return [og_value, True, str("Error adding command: " + str(e)), "danger", 6000]


# ---------------------------------------------------
# Execute Recipe Page
# ---------------------------------------------------


def kill_execution():  # execute-recipe page
    os.kill(os.getpid(), signal.SIGINT)


@app.callback(
    Output("hidden-div", "children"),
    Input("stop-button", "n_clicks"),
    prevent_initial_call=True,
)
def stop_execution(n):  # execute-recipe page
    print("stop_execution")
    # kill_execution()
    return []


@app.callback(
    Output("execute-recipe-output", "children"),
    [Input("execute-button", "n_clicks")],
    prevent_initial_call=True,
)
def execute_recipe(n_clicks):  # execute-recipe page
    print("execute_recipe")
    invoker.invoking = True
    invoker.invoke_commands()
    invoker.invoking = False
    return ["done"]


@app.callback(
    Output("console-out2", "children"),
    Input("interval1", "n_intervals"),
    [State("url", "pathname"), State("show-log-switch", "value")],
    prevent_initial_call=True,
)
def update_output(n, url, switch_val):  # execute-recipe page
    if url == "/execute-recipe" and switch_val:
        log_string = ""
        log_list = invoker.get_log_messages()
        for msg in log_list:
            log_string += msg
            # log_string += '<br>'
        return html.Pre(log_string)
    return ""


@app.callback(
    Output("console-out2", "children", allow_duplicate=True),
    Input("reset-button", "n_clicks"),
    prevent_initial_call=True,
)
def reset_console(n):  # execute-recipe page
    print("reset_console")
    invoker.clear_log_file()
    # dashLoggerHandler.queue = []
    return []


# ---------------------------------------------------
# Data Page
# ---------------------------------------------------


def render_dict(data):  # data page
    if isinstance(data, dict):
        return [
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.Div(
                                render_dict(value),
                                style={"margin-left": "15px"},
                            )
                        ],
                        title=key,
                    )
                    for key, value in data.items()
                ]
            )
        ]
    else:
        return html.P(str(data))


@app.callback(
    Output("data-output-div2", "children"),
    Input("load-data-button", "n_clicks"),
    prevent_initial_call=True,
)
def load_data_accordion(n):  # data page
    if not hasattr(com, "document"):
        print("load_data_accordion - no document")
        return []
    print("load_data_accordion")
    return render_dict(com.document)


# ---------------------------------------------------
# Manual Control Recipe Page
# ---------------------------------------------------


@app.callback(
    Output("manual-control-device-dropdown", "options"),
    Input("interval-manual-control", "n_intervals"),
    State("url", "pathname"),
)
def fill_manual_control_device_dropdown(n, url):  # manual-control page
    if str(url) == "/manual-control":
        print("fill_manual_control_device_dropdown")
        return list(util.devices_ref_redundancy.keys())


@app.callback(
    [
        Output("manual-control-command-dropdown", "disabled"),
        Output("manual-control-command-dropdown", "options"),
    ],
    Input("manual-control-device-dropdown", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def fill_manual_control_command_dropdown(val, url):  # manual-control page
    if str(url) == "/manual-control":
        print("fill_manual_control_command_dropdown")
        if val is None or val == "":
            return [True, []]
        else:
            if util.devices_ref_redundancy[val]["serial"] == False:
                return [False, list(util.devices_ref_redundancy[val]["commands"].keys())]
            else:
                toRet = list(util.devices_ref_redundancy[val]["commands"].keys()).copy()
                for command in util.devices_ref_redundancy[val]["serial_sequence"]:
                    if command in toRet:
                        toRet.remove(command)
                return [False, toRet]


@app.callback(
    [Output("manual-control-device-form", "children")],
    Input("manual-control-device-dropdown", "value"),
    State("url", "pathname"),
)
def create_manual_control_device_form(value, url):
    if str(url) == "/manual-control":
        print("create_manual_control_device_form")
        if value is None or value == "":
            return [[]]
        else:
            args = util.devices_ref_redundancy[value]["init"]["args"]
            toRet = []
            for arg in args:
                toRet.append(
                    dbc.Row(
                        [
                            dbc.Label([arg], html_for=str(value + "+" + arg), width=2),
                            dbc.Col(
                                [
                                    dbc.Input(
                                        id=str(value + "+" + arg),
                                        value=args[arg]["default"],
                                        placeholder=args[arg]["notes"],
                                    ),
                                ],
                                width=10,
                            ),
                        ],
                        className="mb-2",
                    )
                )

            return [toRet]


@app.callback(
    [Output("manual-control-command-form", "children")],
    [
        Input("manual-control-command-dropdown", "value"),
        Input("manual-control-device-dropdown", "value"),
    ],
    [
        State("url", "pathname"),
        State("manual-control-device-form", "children"),
    ],
)
def create_manual_control_command_form(command, device, url, device_form):
    if str(url) == "/manual-control":
        print("create_manual_control_command_form")
        if command is None or command == "" or device is None or device == "":
            return [[]]
        else:
            toRet = []
            if util.devices_ref_redundancy[device]["serial"] == True:
                seq_toRet = []
                for seq_command in util.devices_ref_redundancy[device][
                    "serial_sequence"
                ]:
                    seq_toRet.append(dbc.Row([dbc.Label([seq_command])]))
                    args = util.devices_ref_redundancy[device]["commands"][seq_command][
                        "args"
                    ]
                    for arg in args:
                        seq_toRet.append(
                            dbc.Row(
                                [
                                    dbc.Label(
                                        [arg],
                                        html_for=str(device+"+" + seq_command + "+" + arg),
                                        width=2,
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Input(
                                                id=str(device +"+"+ seq_command + "+" + arg),
                                                value=args[arg]["default"],
                                                placeholder=args[arg]["notes"],
                                            ),
                                        ],
                                        width=10,
                                    ),
                                ],
                                className="mb-2",
                            )
                        )
                toRet.append(dbc.Row(seq_toRet, className="mb-3"))
            toRet.append(dbc.Row([dbc.Label([command])]))
            args = util.devices_ref_redundancy[device]["commands"][command]["args"]
            com_toRet = []
            for arg in args:
                com_toRet.append(
                    dbc.Row(
                        [
                            dbc.Label(
                                [arg],
                                html_for=str(device + command + "+" + arg),
                                width=2,
                            ),
                            dbc.Col(
                                [
                                    dbc.Input(
                                        id=str(device + command + "+" + arg),
                                        value=args[arg]["default"],
                                        placeholder=args[arg]["notes"],
                                    ),
                                ],
                                width=10,
                                
                            ),
                        ],
                        className="mb-2",
                    )
                )
            toRet.append(dbc.Row(com_toRet, className="mb-3"))
            return [toRet]


@app.callback(
    Output("manual-control-device-dropdown", "value"),
    Input("manual-control-clear-button", "n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def manual_control_clear_form(n, url):
    if str(url) == "/manual-control":
        print("manual_control_clear_form")
        return None


@app.callback(
    Output("manual-control-clear-button", "disabled"),
    Input("manual-control-device-dropdown", "value"),
    State("url", "pathname"),
)
def manual_control_clear_button(value, url):
    if str(url) == "/manual-control":
        print("manual_control_clear_button")
        if value is None or value == "":
            return True
        else:
            return False


@app.callback(
    Output("manual-control-execute-button", "disabled"),
    Input("manual-control-command-dropdown", "value"),
    State("url", "pathname"),
)
def manual_control_execute_button(value, url):
    if str(url) == "/manual-control":
        print("manual_control_execute_button")
        if value is None or value == "":
            return True
        else:
            return False


@app.callback(
    Output("manual-control-command-dropdown", "className"),
    Input("manual-control-execute-button", "n_clicks"),
    [
        State('url', 'pathname'),
        State("manual-control-command-dropdown", "className"),
        State("manual-control-device-dropdown", "value"),
        State("manual-control-command-dropdown", "value"),
        State("manual-control-device-form", "children"),
        State("manual-control-command-form", "children"),
    ],
    prevent_initial_call=True,
)
def manual_control_execute(n, url, opt, device, command, device_form, command_form):
    if str(url) == "/manual-control":
        print("manual_control_execute")
        code = ""
        code += util.devices_ref_redundancy[device]["import_device"]
        code += "\n"
        code += util.devices_ref_redundancy[device]["import_commands"]
        code += "\n"
        code += "from command_sequence import CommandSequence\nfrom command_invoker import CommandInvoker\n"

        instantiate_code = ""
        instantiate_code += util.devices_ref_redundancy[device]["init"]["obj_name"]
        instantiate_code += "("
        for i, arg in enumerate(util.devices_ref_redundancy[device]["init"]["args"]):
            if i != 0:
                instantiate_code += ", "
            instantiate_code += arg + "="
            if util.devices_ref_redundancy[device]["init"]["args"][arg]["type"] == str:
                instantiate_code += "'"
                instantiate_code += str(
                    device_form[i]["props"]["children"][1]["props"]["children"][0][
                        "props"
                    ]["value"]
                )
                instantiate_code += "'"
            else:
                instantiate_code += str(
                    device_form[i]["props"]["children"][1]["props"]["children"][0][
                        "props"
                    ]["value"]
                )
        instantiate_code += ")"
        code_seq = str(device) + "_seq" 
        code += code_seq + " = CommandSequence()"
        code += "\n"
        code += code_seq + ".add_device(" + instantiate_code + ")"
        code += "\n"


        if util.devices_ref_redundancy[device]["serial"] == True:
            for i, serial_seq_command in enumerate(util.devices_ref_redundancy[device]['serial_sequence']):
                code += code_seq + ".add_command(" + str(serial_seq_command)+"("
                for ii, serial_seq_command_arg in enumerate(util.devices_ref_redundancy[device]['commands'][serial_seq_command]['args']):
                    if ii != 0:
                        code += ", "
                    if serial_seq_command_arg == "receiver":
                        code += serial_seq_command_arg + "="+str(device)+"_seq.device_by_name['"+str(command_form[0]['props']['children'][(2*ii)+1]['props']['children'][1]['props']['children'][0]['props']['value'])+"']"
                    elif util.devices_ref_redundancy[device]['commands'][serial_seq_command]['args'][serial_seq_command_arg]['type'] == str:
                        code += serial_seq_command_arg + "="+"'"+str(command_form[0]['props']['children'][(2*ii)+1]['props']['children'][1]['props']['children'][0]['props']['value'])+"'"
                    else:
                        code += serial_seq_command_arg + "="+str(command_form[0]['props']['children'][(2*ii)+1]['props']['children'][1]['props']['children'][0]['props']['value'])
                    
                code += "))\n"
            code += code_seq + ".add_command(" + str(command)+"("
            for ii, seq_command_arg in enumerate(util.devices_ref_redundancy[device]['commands'][command]['args']):
                if ii != 0:
                    code += ", "
                if seq_command_arg == "receiver":
                    code += seq_command_arg + "="+str(device)+"_seq.device_by_name['"+str(command_form[2]['props']['children'][ii]['props']['children'][1]['props']['children'][0]['props']['value'])+"']"
                elif util.devices_ref_redundancy[device]['commands'][command]['args'][seq_command_arg]['type'] == str:
                    code += seq_command_arg + "="+"'"+str(command_form[2]['props']['children'][ii]['props']['children'][1]['props']['children'][0]['props']['value'])+"'"
                else:
                    code += seq_command_arg + "="+str(command_form[2]['props']['children'][ii]['props']['children'][1]['props']['children'][0]['props']['value'])
                
            code += "))\n"
        else:
            code += code_seq + ".add_command(" + str(command)+"("
            for ii, seq_command_arg in enumerate(util.devices_ref_redundancy[device]['commands'][command]['args']):
                if ii != 0:
                    code += ", "
                if seq_command_arg == "receiver":
                    code += seq_command_arg + "="+str(device)+"_seq.device_by_name['"+str(command_form[1]['props']['children'][ii]['props']['children'][1]['props']['children'][0]['props']['value'])+"']"
                elif util.devices_ref_redundancy[device]['commands'][command]['args'][seq_command_arg]['type'] == str:
                    code += seq_command_arg + "="+"'"+str(command_form[1]['props']['children'][ii]['props']['children'][1]['props']['children'][0]['props']['value'])+"'"
                else:
                    code += seq_command_arg + "="+str(command_form[1]['props']['children'][ii]['props']['children'][1]['props']['children'][0]['props']['value'])
                
            code += "))\n"
        code += str(device)+"_seq_invoker = CommandInvoker("+str(device)+"_seq, False, False, False)\n"
        code += str(device)+"_seq_invoker.invoke_commands()\n"
        print("\n"+code + "\n")
        try:
            exec(code)
        except Exception as e:
            print(e)               
    
    return opt


#---------------------------------------------------------------
# Database page
#---------------------------------------------------------------

@app.callback(
    Output("database-collection-dropdown", "options"),
    Input("interval-database", "n_intervals"),
    State("url", "pathname"),
)
def fill_database_collection_dropdown(n, url):  # database page
    if str(url) == "/database":
        print("fill_database_collection_dropdown")
        return mongo.db.list_collection_names()


@app.callback(
    [Output('database-document-dropdown', 'disabled'),Output('database-document-dropdown', 'options')],
    Input('database-collection-dropdown', 'value'),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def fill_database_document_dropdown(collection, url):
    if str(url) == "/database":
        if collection is not None and collection != "":
            print("fill_database_document_dropdown")
            docs = list(mongo.db[collection].find({}))
            toRet = []
            for doc in docs:
                toRet.append(str(doc['_id']))
            return False, toRet
        else:
            return True, []


if __name__ == "__main__":
    app.run(debug=True)


# @app.callback(
#     Output("data-output-div", "children"),
#     Input("load-data-button", "n_clicks"),
#     prevent_initial_call=True,
# )
# def load_data(n):
#     print('load_data')
#     # val = ""
#     # docs = mongo.db["recipes"].find()
#     # for doc in docs:
#     #     val += str(doc)
#     #     val += "<br><br>"
#     # nval = val.
#     return (json.dumps(str(com.document)))


# class DashLoggerHandler(logging.StreamHandler):
#     def __init__(self):
#         logging.StreamHandler.__init__(self)
#         self.queue = []

#     def emit(self, record):
#         msg = self.format(record)
#         self.queue.append(msg)


# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
# dashLoggerHandler = DashLoggerHandler()
# logger.addHandler(dashLoggerHandler)

# logger = logging.getLogger(invoker.log.name)
# logger.setLevel(logging.DEBUG)
# from io import StringIO
# log_capture = StringIO()

# # Create a stream handler and set its stream to the log_capture object
# stream_handler = logging.StreamHandler(log_capture)
# logger.addHandler(stream_handler)
# log_messages = []

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

# @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
# def display_page(pathname):
#     print("\n\nrefreshing to " + pathname)
#     if pathname == "/":
#         return home_layout
#     elif pathname == "/edit-recipe":
#         return edit_recipe_layout
#     elif pathname == "/execute-recipe":
#         return execute_recipe_layout
#     elif pathname == "/data":
#         return data_layout
#     else:
#         return html.Div("404")


# data_list4 = com.device_list

# dl5 = []
# for list in data_list4:
#     dl5.append(list.__dict__)

# print(dl5[2]['motor'].__dict__)


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


# @app.callback(
#     Output("commands-accordion", "children"),
#     Input("refresh-button2", "n_clicks"),
#     State("commands-accordion", "children"),
#     # allow_duplicate=True
# )
# def load_commands_accordion(n_clicks, children):
#     children = []
#     # print()
#     command_list = com.get_unlooped_command_list().copy()
#     # print(command_list)
#     # for command in command_list:
#     #     if isinstance(command, CompositeCommand):
#     #         for sub_command in command._command_list:
#     #             sub_command._receiver = sub_command._receiver._name
#     #             sub_command = sub_command.__dict__
#     #     else:
#     #         # print(command.__dict__)
#     #         command._receiver = command._receiver._name
#     command_params = []
#     for command in command_list:
#         # if isinstance(command, CompositeCommand):
#         # print(type(command).__name__)
#         temp_dict_command_params = {"command": type(command).__name__}
#         temp_dict_command_params.update({"params": command.get_init_args()})
#         command_params.append(temp_dict_command_params)
#         # print(command._params)
#         # else:
#         #     command_params.append(command._params)
#     # print(command_params)
#     # print(com.get_command_names())
#     for index, command in enumerate(command_params):
#         # print(command)
#         children.append(
#             dbc.AccordionItem(
#                 dcc.Markdown(
#                     children=[
#                         "**Command Object:**",
#                         "```json",
#                         json.dumps(command, indent=4, cls=util.Encoder),
#                         # str(command.__dict__),
#                         "```",
#                     ],
#                 ),
#                 # str(command.__dict__),
#                 title=command["command"],
#                 item_id=command["command"] + str(index),
#             )
#         )
#     return children


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
