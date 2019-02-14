import boto3
import dash_core_components as dcc
import dash_html_components as html
import simplejson as json
from dash.dependencies import Input, Output

from server import *

dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
sources_table = dynamodb.Table('Sources')
sources_data = sources_table.scan()['Items']

layout = html.Div(children=[
    dcc.Dropdown(id='dataSetSelect',
                 value='sources',
                 options=[{'label': 'Sources', 'value': 'sources'},
                          ]
    ),
    html.Div(id='outputArea',
             style={'overflow-y': 'scroll', 'white-space': 'pre', 'height': '40em'}
    )
])




@app.callback(Output('outputArea', 'children'),
              [Input('dataSetSelect', 'value')])
def update_output_area(data_set):
    if data_set == 'sources':
        data = sources_data
        # jsonString = json.dumps(sources_data,  indent='\t')
    return json.dumps(data, indent='\t')
