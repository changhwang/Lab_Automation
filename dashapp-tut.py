import dash
from dash import html, Input, Output, State, dcc, dash_table
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from bson.objectid import ObjectId
from mongodb_helper import MongoDBHelper



# client = MongoClient('mongodb+srv://ppahuja2:s5eMFr1js8iEcMt8@diaogroup.nrcgqsq.mongodb.net/?retryWrites=true&w=majority')
# db = client["diaogroup"]
# collection = db["recipes2"]

mongo = MongoDBHelper('mongodb+srv://ppahuja2:s5eMFr1js8iEcMt8@diaogroup.nrcgqsq.mongodb.net/?retryWrites=true&w=majority', 'diaogroup')


# Define Layout of App
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Editor', style={'textAlign': 'center'}),
    # interval activated every second or when page refreshed
    dcc.Interval(id='interval_db', interval=1000, n_intervals=0),
    html.Div(id='mongo-datatable', children=[]),

    html.Div([
        html.Div(id='pie-graph', className='five columns'),
        html.Div(id='hist-graph', className='six columns'),
    ], className='row'),
    dcc.Store(id='changed-cell')
])



if __name__ == '__main__':
    app.run_server(debug=True)