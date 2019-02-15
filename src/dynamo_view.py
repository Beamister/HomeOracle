import boto3
import dash_core_components as dcc
import dash_html_components as html
import simplejson as json
from dash.dependencies import Input, Output
from constants import *

from server import *

dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
dynamodb_client = boto3.client('dynamodb', region_name=AWS_REGION)
table_names = dynamodb_client.list_tables()['TableNames']

layout = html.Div(children=[
    dcc.Dropdown(id='dataSetSelect',
                 value=table_names[0],
                 options=[{'label': table_name, 'value': table_name} for table_name in table_names]
    ),
    html.Div(id='outputArea',
             style={'overflow-y': 'scroll', 'white-space': 'pre', 'height': '40em'}
    )
])




@app.callback(Output('outputArea', 'children'),
              [Input('dataSetSelect', 'value')])
def update_output_area(table_name):
    table = dynamodb.Table(table_name)
    table_data = table.scan()['Items']
    return json.dumps(table_data, indent='\t')
