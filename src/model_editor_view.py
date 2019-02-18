import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from server import *

parameter_names = ['test']
existing_model_names = ['test']

layout = html.Div(children=[
    html.Div(id='feedback_container'),
    html.H1("Model Creator"),
    html.Div("Model Name"),
    dcc.Input(id='model_name_input'),
    html.Div("Model Type"),
    dcc.Dropdown(id='model_type_select',
                 options=[{'label': 'Decision Tree', 'value': 'decision_tree'},
                          {'label': 'SVM', 'value': 'svm'}],
                 value='decision_tree'
                 ),
    html.Div("Inflation Adjustment"),
    dcc.Dropdown(id='inflation_adjustment_select',
                 value='none',
                 options=[{'label': 'None', 'value': 'none'}]
                 ),
    dcc.Checklist(id='parameter_select',
                  options=[{'label': parameter_name, 'value': parameter_name} for parameter_name in parameter_names],
                  values=[]
                  ),
    dcc.Checklist(id='composite_model_select',
                  options=[{'label': model_name, 'value': model_name} for model_name in existing_model_names],
                  values=[]
                  ),
    html.Div(id='model_type_specific_options_container',
             children=[
                 html.Div(id='decision_tree_options_container',
                          style={'display': 'none'},
                          children=[
                              html.Div("Number of estimators:"),
                              dcc.Input(id='estimator_count_input'),
                              dcc.Checklist(id='enable_max_tree_depth_checkbox',
                                            options=[{'label': 'Enable maximum tree depth',
                                                     'value': 'enabled_max_tree_depth'}],
                                            values=[]
                                            ),
                              html.Div("Maximum tree depth:"),
                              dcc.Input(id='max_tree_depth_input',
                                        type='number',
                                        )
                          ]),
                 html.Div(id='svm_options_container',
                          style={'display': 'none'},
                          children=[
                              html.Div("Kernel Type:"),
                              dcc.Dropdown(id='kernel_type_select',
                                           options=[{'label': 'rbf', 'value': 'rbf'},
                                                    {'label': 'linear', 'value': 'linear'},
                                                    {'label': 'poly', 'value': 'poly'},
                                                    {'label': 'sigmoid', 'value': 'sigmoid'}],
                                           value='rbf'
                                           ),
                              html.Div("Select C value: "),
                              dcc.Input(id='c_value_input',
                                        value=0.1,
                                        type='number',
                                        ),
                              html.Div("Select epsilon value:"),
                              dcc.Input(id='epsilon_value_input',
                                        value=0.1,
                                        type='number',
                                        )
                          ])
             ]
             ),
    dcc.Checklist(id='enable_use_entire_dataset',
                  options=[{'label': 'Use entire dataset',
                            'value': 'enable_use_entire_dataset'}],
                  values=[]
                  ),
    html.Div("Maximum number of entries to train on:"),
    dcc.Input(id='training_examples_count_input',
              value=10000,
              type='number',
              min=1
              ),
    html.Button("Create Model",
                id='create_model_button'
                )
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


@app.callback(Output('svm_options_container', 'style'),
              [Input('model_type_select', 'value')])
def update_svm_options_display(model_selected):
    if model_selected == 'svm':
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(Output('decision_tree_options_container', 'style'),
              [Input('model_type_select', 'value')])
def update_svm_options_display(model_selected):
    if model_selected == 'decision_tree':
        return {'display': 'block'}
    else:
        return {'display': 'none'}
