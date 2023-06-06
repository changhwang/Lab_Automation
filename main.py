# from mongodb_helper import MongoDBHelper

# mongo_uri = "mongodb+srv://ppahuja2:s5eMFr1js8iEcMt8@diaogroup.nrcgqsq.mongodb.net/?retryWrites=true&w=majority"
# database_name = "diaogroup"

# mongo = MongoDBHelper(mongo_uri, database_name)

#ppahuja2
##s5eMFr1js8iEcMt8



# mongo.close_connection()

# import pymongo
# import yaml

# # Connect to MongoDB
# client = pymongo.MongoClient('mongodb+srv://ppahuja2:s5eMFr1js8iEcMt8@diaogroup.nrcgqsq.mongodb.net/?retryWrites=true&w=majority')
# db = client['diaogroup']
# collection = db['recipes']

# document = collection.find_one({})

# # Retrieve the YAML data from the document
# yaml_data = document['yaml_data']
# print(yaml_data)
# # Save the YAML data to a local file
# with open('retrieved_file.yaml', 'wb') as file:
#     file.write(yaml_data)

# # Close the MongoDB connection
# client.close()




import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from pymongo import MongoClient

# MongoDB connection setup
client = MongoClient('mongodb+srv://ppahuja2:s5eMFr1js8iEcMt8@diaogroup.nrcgqsq.mongodb.net/?retryWrites=true&w=majority')
db = client['diaogroup']
collection = db['recipes']

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='document-dropdown',
        options=[],
        value='',
        placeholder='Select a document'
    ),
    dcc.Textarea(id='yaml-editor', style={'width': '100%', 'height': '400px'}),
    html.Div(id='yaml-output')
])

@app.callback(Output('document-dropdown', 'options'), Output('document-dropdown', 'value'),
              [Input('document-dropdown', 'value')])
def update_document_dropdown(selected_document):
    # Fetch the list of documents from the MongoDB collection
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
        yaml_content = document.get('yaml_data', '')

        # Update the YAML output
        yaml_output = html.Pre(yaml_content)

        return yaml_content, yaml_output

    return '', ''


if __name__ == '__main__':
    app.run_server(debug=True)
