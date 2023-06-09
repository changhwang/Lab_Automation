from command_sequence import CommandSequence
import project_const


com = CommandSequence()


print()
print()

com.load_from_yaml("e1.yaml")
# print(com.device_list[0].__dict__)


# print(com.device_list[0].__dict__)
# print(com.device_list[1])
# print(type(com.command_list[0][0].__dict__))


# print(com.get_device_names_classes())
print(com.get_clean_device_list())
# quit()
# print(com.get_command_names())

# temp = {
#         "_name": "heater1",
#         "_is_initialized": False,
#         "_heat_rate": 20.0,
#         "min_heat_rate": 1.0,
#         "max_heat_rate": 50.0,
#         "min_temperature": 25.0,
#         "max_temperature": 100.0,
#         "_temperature": 95.71927572168929,
#         "_hardware_interval": 0.05,
#         # "name": "heater1",
#     }
# print("hello")
# print(temp)

import util

# out = util.dict_to_device(com.device_list[1].__dict__, com.get_device_names_classes()[1][1])
# out = util.dict_to_device(com.device_list[0], com.get_device_names_classes()[0][1])

out = util.device_to_dict(com.device_list[0])


print("\n\nresult:\n\n")
print(out)
# quit()


# device_cls = project_const.named_devices[com.get_device_names_classes()[0][1]]
# arg_dict = temp
# com.add_device(device_cls(**arg_dict))
# print(com.add_device(device_cls(**arg_dict)))

# quit()

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import random

app = dash.Dash(__name__)

# Sample data lists
data_list1 = [
    {"Name": "John", "Value": 25},
    {"Name": "Amy", "Value": 31},
    {"Name": "David", "Value": 28},
]
data_list2 = [
    {"Name": "Apple", "Value": 10},
    {"Name": "Banana", "Value": 5},
    {"Name": "Orange", "Value": 8},
]
data_list3 = [
    {"Name": "Red", "Value": 15},
    {"Name": "Green", "Value": 20},
    {"Name": "Blue", "Value": 12},
]

app.layout = html.Div(
    [
        html.H1("Dash Tables"),
        html.Div(
            [
                html.Div(
                    [
                        html.H2("Devices"),
                        html.Button("Refresh", id="refresh-button1", n_clicks=0),
                        html.Div(id="table-container1"),
                    ],
                    className="table-container",
                ),
                html.Div(
                    [
                        html.H2("Table 2"),
                        html.Button("Refresh", id="refresh-button2", n_clicks=0),
                        html.Div(id="table-container2"),
                    ],
                    className="table-container",
                ),
                html.Div(
                    [
                        html.H2("Table 3"),
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

data_list4 = com.device_list
dl5_og = [
    {
        "_name": "heater1",
        "_is_initialized": False,
        "_heat_rate": 20.0,
        "min_heat_rate": 1.0,
        "max_heat_rate": 50.0,
        "min_temperature": 25.0,
        "max_temperature": 100.0,
        "_temperature": 95.71927572168929,
        "_hardware_interval": 0.05,
    },
    {
        "_name": "motor1",
        "_is_initialized": False,
        "motor": {
            "_speed": 20.0,
            "min_speed": 1.0,
            "max_speed": 50.0,
            "min_position": 0.0,
            "max_position": 100.0,
            "_position": 37.44120879993549,
            "_hardware_interval": 0.05,
        },
    },
    {
        "_name": "motor2",
        "_is_initialized": False,
        "motor": {
            "_speed": 20.0,
            "min_speed": 1.0,
            "max_speed": 50.0,
            "min_position": 0.0,
            "max_position": 100.0,
            "_position": 82.48283286198111,
            "_hardware_interval": 0.05,
        },
    },
]
# dl5 = []
# for list in data_list4:
#     dl5.append(list.__dict__)

print()
print()
print()
# print(dl5[2]['motor'].__dict__)


@app.callback(
    Output("table-container1", "children"),
    [Input("refresh-button1", "n_clicks")],
    [State("table-container1", "children")],
)
def update_table1(n_clicks, table):
    dl5 = dl5_og.copy()
    dl5_props_temp = {}
    count = 0
    for list in dl5:
        dl5_props_temp.clear()
        if len(list) > 1:
            for prop in list:
                if prop != "_name":
                    dl5_props_temp[prop] = list[prop]
                    # print(prop)
            # print("h")
            dl5_temp_list = list
            dl5[count] = {}
            dl5[count]["_name"] = dl5_temp_list["_name"]
            # dl5[count]["_is_initialized"] = dl5_temp_list["_is_initialized"]
            dl5[count]["props"] = str(dl5_props_temp)
            # print(str(dl5_props_temp))
        count += 1

    # table_data1 = dl5
    table_data1 = com.get_clean_device_list().copy()
    
    table_data1_new = []
    for index, list in enumerate(table_data1):
        # table_data1[index][1].update({"device_type": table_data1[index][0]})
        # del table_data1[index][0]
        table_data1_new.append({"device_type": table_data1[index][0], "props": str(table_data1[index][1])})
    
    table_data1 = table_data1_new
    # print(table_data1)
    table = dash_table.DataTable(
        data=table_data1,
        columns=[
            {"name": "Type", "id": "device_type"},
            # {"name": "Initialized", "id": "_is_initialized"},
            {"name": "Properties", "id": "props"},
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
            {"if": {"column_id": "_name"}, "width": "20%"},
            {"if": {"column_id": "props"}, "width": "80%"},
        ],
        tooltip_data=[
            {
                column: {"value": str(value), "type": "markdown"}
                for column, value in row.items()
            }
            for row in table_data1
        ],
        tooltip_duration=None,
        editable = True,
    )
    print("done")
    return table


# @app.callback(
#     Output("table-container2", "children"),
#     [Input("refresh-button2", "n_clicks")],
#     [State("table-container2", "children")],
# )
# def update_table2(n_clicks, table):
#     table_data2 = data_list2
#     table = dash_table.DataTable(
#         data=table_data2,
#         columns=[{"name": "Name", "id": "Name"}, {"name": "Value", "id": "Value"}],
#     )
#     return table


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
