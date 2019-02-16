import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from server import *

parameter_names = []
existing_model_names = []

layout = html.Div(children=[
    html.Div(id='feedback_container'),
    html.H1("Model Creator"),
    html.Div("Model Name"),
    dcc.Input(id='model_name_input'),
    html.Div("Model Type"),
    dcc.Dropdown(id='model_type_select',
                 options=[{'label': 'Decision Tree', 'value': 'decision_tree'},
                          {'label': 'SVM', 'value': 'svm'}]
                 ),
    html.Div("Inflation Adjustment"),
    dcc.Dropdown(id='inflation_adjustment_select',
                 value='none',
                 options=[{'label': 'None', 'value': 'none'}]),
    dcc.Checklist(id='parameter_select',
                  options=[{'label': parameter_name, 'value': parameter_name} for parameter_name in parameter_names],
                  ),
    dcc.Checklist(id='composite_model_select',
                  options=[{'label': model_name, 'value': model_name} for model_name in existing_model_names]),
    html.Button("Create Model",
                id='create_model_button')
])

@app.callback(Output('feedback_container', 'children'),
              [Input('create_model_button', 'n_clicks')],
              [State('model_name_input', 'value'),
               State('inflation_adjustment_select', 'value'),
               State('parameter_select', 'value'),
               State('composite_model_select', 'value')])
def create_model(n_clicks, model_name, inflation_adjustment_type, parameters, ):
    # Catch for when callback is called on page load
    if n_clicks is None:
        return ""
