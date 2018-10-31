import boto3
import dash_core_components as dcc
import dash_html_components as html
import simplejson as json
from dash.dependencies import Input, Output

from server import *

dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
sources_table = dynamodb.Table('Sources')
sources_data = sources_table.scan()['Items']
indicators_table = dynamodb.Table('Indicators')
indicators = [indicator['IndicatorName'] for indicator in
              indicators_table.scan(ProjectionExpression='IndicatorName')['Items']]

layout = html.Div(children=[
    dcc.Dropdown(id='dataSetSelect',
                 value='sources',
                 options=[{'label': 'Sources', 'value': 'sources'},
                          {'label': 'Indicator', 'value': 'indicators'}
                          ]),
    html.Div(id='indicatorSelectContainer',
             style={'display': 'none'},
             children=[
                 dcc.Dropdown(id='indicatorSelect',
                              options=[{'label': indicator, 'value': indicator}
                                       for indicator in indicators],
                              value=indicators[0])
             ]),
    html.Div(id='outputArea',
             style={'overflow-y': 'scroll', 'white-space': 'pre', 'height': '40em'})
])


@app.callback(Output('indicatorSelectContainer', 'style'),
              [Input('dataSetSelect', 'value')])
def update_display_indicator_select(data_set):
    if data_set == 'sources':
        return {'display': 'none'}
    else:
        return {'display': 'block'}


@app.callback(Output('outputArea', 'children'),
              [Input('dataSetSelect', 'value'),
               Input('indicatorSelect', 'value')])
def update_output_area(data_set, indicator):
    if data_set == 'sources':
        data = sources_data
        # jsonString = json.dumps(sources_data,  indent='\t')
    else:
        data = indicators_table.get_item(Key={'IndicatorName': indicator})['Item']
    return json.dumps(data, indent='\t')
