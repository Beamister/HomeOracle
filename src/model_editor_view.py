import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from server import *

parameter_names = ['test param one', 'test param two']
existing_model_names = ['test model one', 'test model two']

layout = html.Div(children=[
    html.H1("Model Creator"),
    html.Div(id='feedback_container'),
    html.Div(id='inputsContainer',
             style={'display': 'flex', 'justify-content': 'space-around', 'height': '30em'},
             children=[
                html.Div(id='model_settings_container',
                         style={'display': 'flex-box', 'width': '48%'},
                         children=[
                            html.Div("Model Name"),
                            dcc.Input(id='model_name_input',
                                      value='',
                                      type='text',
                                      ),
                            html.Div("Model Type"),
                            dcc.Dropdown(id='model_type_select',
                                         options=[{'label': 'Decision Tree', 'value': 'decision_tree'},
                                                  {'label': 'SVM', 'value': 'svm'}],
                                         value='decision_tree'
                                         ),
                            html.Div(id='model_type_specific_options_container',
                                     children=[
                                        html.Div(id='decision_tree_options_container',
                                                 style={'display': 'none'},
                                                 children=[
                                                     html.Div("Number of estimators:"),
                                                     dcc.Input(id='estimator_count_input',
                                                               type='number',
                                                               min=1
                                                               ),
                                                     dcc.Checklist(id='enable_max_tree_depth_checkbox',
                                                                   options=[{'label': 'Enable maximum tree depth',
                                                                             'value': 'enabled_max_tree_depth'}],
                                                                   values=[]
                                                                   ),
                                                     html.Div(id='max_tree_depth_input_container',
                                                              children=[
                                                                 html.Div("Maximum tree depth:"),
                                                                 dcc.Input(id='max_tree_depth_input',
                                                                           type='number',
                                                                           min=1
                                                                           )
                                                              ]),
                                                 ]),
                                        html.Div(id='svm_options_container',
                                                 style={'display': 'none'},
                                                 children=[
                                                     html.Div("Kernel Type:"),
                                                     dcc.Dropdown(id='kernel_type_select',
                                                                  options=[{'label': 'rbf', 'value': 'rbf'},
                                                                           {'label': 'linear', 'value': 'linear'},
                                                                           {'label': 'polynomial',
                                                                            'value': 'polynomial'},
                                                                           {'label': 'sigmoid', 'value': 'sigmoid'}],
                                                                  value='rbf'
                                                                  ),
                                                     html.Div(id='polynomial_degree_input_container',
                                                              children=[
                                                                  html.Div("Polynomial Degree:"),
                                                                  dcc.Input(id='polynomial_degree_input',
                                                                            value=3,
                                                                            step=1,
                                                                            min=1,
                                                                            type='number',
                                                                            ),
                                                              ]),
                                                     html.Div("Select C value: "),
                                                     dcc.Input(id='c_value_input',
                                                               value=1.0,
                                                               step=0.1,
                                                               type='number',
                                                               ),
                                                     html.Div("Select epsilon value:"),
                                                     dcc.Input(id='epsilon_value_input',
                                                               value=0.1,
                                                               step=0.1,
                                                               type='number',
                                                               )
                                                 ])
                                      ]),
                         ]),
                html.Div(id='data_settings_container',
                         style={'display': 'flex-box', 'width': '48%'},
                         children=[
                            html.Div("Select Dataset"),
                            dcc.Dropdown(id='dataset_select',
                                         options=[{'label': 'Boston Housing', 'value': 'boston_housing'},
                                                  {'label': 'Core Dataset', 'value': 'core_dataset'}],
                                         value=''
                                         ),
                            dcc.Checklist(id='enable_use_entire_dataset',
                                          options=[{'label': 'Use entire dataset',
                                                    'value': 'enable_use_entire_dataset'}],
                                          values=['enable_use_entire_dataset']
                                          ),
                            html.Div(id='training_count_input_container',
                                     children=[
                                        html.Div("Maximum number of entries to train on:"),
                                        dcc.Input(id='training_examples_count_input',
                                                  value=10000,
                                                  type='number',
                                                  min=1
                                                  ),
                                     ]),
                            html.Div("Inflation Adjustment"),
                            dcc.Dropdown(id='inflation_adjustment_select',
                                         value='none',
                                         options=[{'label': 'None', 'value': 'none'}]
                                         ),
                            html.Div("Select input parameters:"),
                            dcc.Checklist(id='parameter_select',
                                          options=[{'label': parameter_name, 'value': parameter_name}
                                                   for parameter_name in parameter_names],
                                          values=[],
                                          labelStyle={'display': 'inline-block'}
                                          ),
                            html.Div("Select input models:"),
                            dcc.Checklist(id='composite_model_select',
                                          options=[{'label': model_name, 'value': model_name}
                                                   for model_name in existing_model_names],
                                          values=[],
                                          labelStyle={'display': 'inline-block'}
                                          ),
                         ])
             ]),
    html.Br(),
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
def create_model(n_clicks, model_name, inflation_adjustment_type, input_parameters, input_models):
    # Catch for when callback is called on page load
    if n_clicks is None:
        return ""


@app.callback(Output('max_tree_depth_input_container', 'style'),
              [Input('enable_max_tree_depth_checkbox', 'values')])
def update_max_tree_depth_input_display(selected_options):
    if 'enabled_max_tree_depth' in selected_options:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(Output('polynomial_degree_input_container', 'style'),
              [Input('kernel_type_select', 'value')])
def update_max_tree_depth_input_display(svm_kernel_type):
    if 'polynomial' == svm_kernel_type:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(Output('training_count_input_container', 'style'),
              [Input('enable_use_entire_dataset', 'values')])
def update_training_count_select_display(selected_options):
    if 'enable_use_entire_dataset' not in selected_options:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


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
