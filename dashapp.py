# import dash
# import dash_html_components as html
# import dash_core_components as dcc
# from dash.dependencies import Input, Output, State
# from pymongo import MongoClient

# # MongoDB connection setup
# client = MongoClient('mongodb+srv://ppahuja2:s5eMFr1js8iEcMt8@diaogroup.nrcgqsq.mongodb.net/?retryWrites=true&w=majority')
# db = client['diaogroup']
# collection = db['recipes']

# app = dash.Dash(__name__)

# app.layout = html.Div([
#     dcc.Input(id='document-name', type='text', placeholder='Enter document name'),
#     dcc.Textarea(id='yaml-editor', style={'width': '100%', 'height': '400px'}),
#     html.Button('Save Document', id='save-button', n_clicks=0),
#     html.Div(id='save-message'),
#     html.Hr(),
#     dcc.Dropdown(
#         id='document-dropdown',
#         options=[],
#         value='',
#         placeholder='Select a document'
#     ),
#     html.Div(id='yaml-output')
# ])


# @app.callback(Output('document-dropdown', 'options'), Output('document-dropdown', 'value'),
#               [Input('document-dropdown', 'value'), Input('save-button', 'n_clicks')],
#               [State('document-name', 'value'), State('yaml-editor', 'value')])
# def update_document_dropdown(selected_document, save_clicks, document_name, yaml_content):
#     # Fetch the list of documents from the MongoDB collection
#     documents = collection.find({}, {"_id": 0, "name": 1})
#     options = [{'label': doc['name'], 'value': doc['name']} for doc in documents]

#     if selected_document not in [doc['value'] for doc in options]:
#         selected_document = options[0]['value']

#     if save_clicks > 0:
#         # Insert the new document into the collection
#         new_document = {'name': document_name, 'content': yaml_content}
#         collection.insert_one(new_document)

#     return options, selected_document


# @app.callback(Output('yaml-editor', 'value'), Output('yaml-output', 'children'),
#               [Input('document-dropdown', 'value')])
# def update_yaml_editor(selected_document):
#     # Fetch the selected document from the MongoDB collection
#     document = collection.find_one({'name': selected_document})

#     if document:
#         # Extract the YAML content from the document
#         yaml_content = document.get('content', '')

#         # Update the YAML output
#         yaml_output = html.Pre(yaml_content)

#         return yaml_content, yaml_output

#     return '', ''


# @app.callback(Output('save-message', 'children'),
#               [Input('save-button', 'n_clicks')],
#               [State('document-name', 'value'), State('yaml-editor', 'value')])
# def save_document(n_clicks, document_name, yaml_content):
#     if n_clicks > 0:
#         # Insert the new document into the collection
#         new_document = {'name': document_name, 'content': yaml_content}
#         collection.insert_one(new_document)
#         return html.Div('Document saved successfully.')
    
#     return ''


# if __name__ == '__main__':
#     app.run_server(debug=True)





import dash
import dash_core_components as dcc
import dash_html_components as html
from dash import dash_table
from dash.dependencies import Input, Output, State
from pymongo import MongoClient
import json
from bson import ObjectId

# MongoDB connection
client = MongoClient('mongodb+srv://ppahuja2:s5eMFr1js8iEcMt8@diaogroup.nrcgqsq.mongodb.net/?retryWrites=true&w=majority')
db = client["diaogroup"]
collection = db["recipes2"]
# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div(
    children=[
        html.H1("CRUD App with MongoDB"),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H3("Create Document"),
                        dcc.Input(id="create-id-input", type="text", placeholder="Enter document ID"),
                        dcc.Input(id="create-input", type="text", placeholder="Enter document data"),
                        html.Button("Create", id="create-button", n_clicks=0),
                    ],
                    className="crud-item",
                ),
                html.Div(
                    children=[
                        html.H3("Existing Documents"),
                        html.Button("Refresh", id="refresh-button", n_clicks=0),
                        dash_table.DataTable(
                            id="documents-table",
                            columns=[
                                {"name": "ID", "id": "identifier"},
                                {"name": "Data", "id": "data"},
                            ],
                            data=[],
                            editable=False,
                            row_selectable="single",
                            style_cell={"textAlign": "left"},
                            style_data={"whiteSpace": "normal", "height": "auto"},
                        ),
                    ],
                    className="crud-item",
                ),
                html.Div(
                    children=[
                        html.H3("Selected Document"),
                        html.Div(id="selected-document-output"),
                        html.Button("Read", id="read-button", n_clicks=0),
                        html.Button("Update", id="update-button", n_clicks=0),
                        html.Button("Delete", id="delete-button", n_clicks=0),
                    ],
                    className="crud-item",
                ),
            ],
            className="crud-container",
        ),
    ]
)
# Update the documents table with existing documents
@app.callback(
    Output("documents-table", "data"),
    Output("selected-document-output", "children"),
    Input("create-button", "n_clicks"),
    Input("read-button", "n_clicks"),
    Input("update-button", "n_clicks"),
    Input("delete-button", "n_clicks"),
    Input("refresh-button", "n_clicks"),
    State("create-id-input", "value"),
    State("create-input", "value"),
    State("documents-table", "selected_rows"),
    State("documents-table", "data"),
)
def update_documents_table(
    create_n_clicks,
    read_n_clicks,
    update_n_clicks,
    delete_n_clicks,
    refresh_n_clicks,
    id_input_value,
    input_value,
    selected_rows,
    documents,
):
    ctx = dash.callback_context
    triggered_button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if triggered_button_id == "create-button" and create_n_clicks > 0 and id_input_value and input_value:
        document = {"identifier": id_input_value, "data": input_value}
        collection.insert_one(document)

    if triggered_button_id == "refresh-button" and refresh_n_clicks > 0:
        documents = list(collection.find())

    # Convert ObjectId values to strings
    for document in documents:
        document["_id"] = str(document["_id"])

    data = []
    if documents:
        data = json.loads(json.dumps(documents))

    selected_document_output = ""
    if selected_rows:
        selected_document = documents[selected_rows[0]]
        selected_document_output = html.Div(
            [
                html.H4("Selected Document"),
                html.P(f"ID: {selected_document['identifier']}"),
                html.P(f"Data: {selected_document['data']}"),
            ]
        )

    if triggered_button_id == "read-button" and read_n_clicks > 0 and selected_rows:
        selected_document = documents[selected_rows[0]]
        selected_document_output = html.Div(
            [
                html.H4("Selected Document"),
                html.P(f"ID: {selected_document['identifier']}"),
                html.P(f"Data: {selected_document['data']}"),
                html.P(f"Data3: {selected_document.get('data3', '')}"),
            ]
        )

    if triggered_button_id == "update-button" and update_n_clicks > 0 and selected_rows:
        selected_document = documents[selected_rows[0]]
        # Implement your update logic here
        # For example, update the 'data' field with the new value
        # new_data_value = "New Value"
        # collection.update_one(
        #     {"identifier": selected_document["identifier"]},
        #     {"$set": {"data": new_data_value}},
        # )
        selected_document_output = html.Div(
            [
                html.H4("Selected Document"),
                html.P(f"ID: {selected_document['identifier']}"),
                html.P(f"Data: {selected_document['data']}"),
            ]
        )

    if triggered_button_id == "delete-button" and delete_n_clicks > 0 and selected_rows:
        selected_document = documents[selected_rows[0]]
        collection.delete_one({"identifier": selected_document["identifier"]})
        documents = list(collection.find())
        # Convert ObjectId values to strings
        for document in documents:
            document["_id"] = str(document["_id"])
        data = json.loads(json.dumps(documents))
        selected_document_output = ""

    return data, selected_document_output



if __name__ == "__main__":
    app.run_server(debug=True)
