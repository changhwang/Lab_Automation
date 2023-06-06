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
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from pymongo import MongoClient

# MongoDB connection setup
client = MongoClient('mongodb+srv://ppahuja2:s5eMFr1js8iEcMt8@diaogroup.nrcgqsq.mongodb.net/?retryWrites=true&w=majority')
db = client["diaogroup"]
collection = db["recipes"]

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Input(id='document-name', type='text', placeholder='Enter document name'),
    dcc.Textarea(id='yaml-editor', style={'width': '100%', 'height': '400px'}),
    html.Button('Save', id='save-button', n_clicks=0),
    html.Button('Update', id='update-button', n_clicks=0),
    html.Button('Delete', id='delete-button', n_clicks=0),
    html.Div(id='message'),
    html.Hr(),
    dcc.Dropdown(
        id='document-dropdown',
        options=[],
        value='',
        placeholder='Select a document'
    ),
    html.Div(id='yaml-output')
])


@app.callback(Output('document-dropdown', 'options'), Output('document-dropdown', 'value'),
              [Input('document-dropdown', 'value'), Input('save-button', 'n_clicks'),
               Input('update-button', 'n_clicks'), Input('delete-button', 'n_clicks')],
              [State('document-name', 'value'), State('yaml-editor', 'value')])
def update_document_dropdown(selected_document, save_clicks, update_clicks, delete_clicks,
                             document_name, yaml_content):
    if save_clicks > 0:
        # Insert the new document into the collection
        new_document = {'name': document_name, 'content': yaml_content}
        collection.insert_one(new_document)

    elif update_clicks > 0:
        # Update the selected document in the collection
        collection.update_one({'name': selected_document}, {'$set': {'content': yaml_content}})

    elif delete_clicks > 0:
        # Delete the selected document from the collection
        collection.delete_one({'name': selected_document})

    # Fetch the updated list of documents from the MongoDB collection
    documents = collection.find({}, {"_id": 0, "name": 1})
    options = [{'label': doc['name'], 'value': doc['name']} for doc in documents]

    if selected_document not in [doc['value'] for doc in options]:
        selected_document = options[0]['value']

    return options, selected_document


@app.callback(Output('yaml-editor', 'value'), Output('yaml-output', 'children'),
              [Input('document-dropdown', 'value')])
def update_yaml_editor(selected_document):
    # Fetch the selected document from the MongoDB collection
    document = collection.find_one({'name': selected_document})

    if document:
        # Extract the YAML content from the document
        yaml_content = document.get('content', '')

        # Update the YAML output
        yaml_output = html.Pre(yaml_content)

        return yaml_content, yaml_output

    return '', ''


if __name__ == '__main__':
    app.run_server(debug=True)
