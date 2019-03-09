import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from server import *


layout = html.Div(children=[
    html.H1("Model Creator"),
    html.Div(id='model_editor_feedback_container'),
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
                                                 style={'display': 'block'},
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
                                                 style={'display': 'block'},
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
                                         value='core_dataset',
                                         clearable=False
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
                                          options=[{}],
                                          values=[],
                                          labelStyle={'display': 'inline-block'}
                                          ),
                            html.Div("Select input models:"),
                            dcc.Checklist(id='composite_model_select',
                                          options=[{}],
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


def validate_model_input(model_name, model_type, estimator_count, enable_max_tree_depth, max_tree_depth, kernel_type,
                 polynomial_degree, c_value, epsilon_value, dataset, enable_use_entire_dataset, training_examples_count,
                 inflation_adjustment_type, input_parameters, input_models):
    result = ""
    if model_name == "":
        result = "Please input model name"
    elif model_name in model_manager.get_model_names():
        result = "Model name already exists"
    elif dataset is None:
        result = "Please select a dataset"
    elif enable_use_entire_dataset != 'enable_use_entire_dataset' and (training_examples_count is None
                                                                       or training_examples_count <= 0):
        result = "Please select number of training examples"
    elif inflation_adjustment_type is None:
        result = "Please select inflation adjustment"
    elif input_parameters == [] and input_models == []:
        result = "Please select inputs"
    elif model_type == 'decision_tree':
        if estimator_count is None or estimator_count <= 0:
            result = "Please select the number of estimators"
        elif enable_max_tree_depth == 'enabled_max_tree_depth' and (max_tree_depth is None or max_tree_depth <= 0):
            result = "Please set max tree depth"
    elif model_type == 'svm':
        if kernel_type is None or kernel_type not in ['rbf', 'linear', 'polynomial', 'sigmoid']:
            result = "Please select kernel type"
        elif kernel_type == 'polynomial' and (polynomial_degree is None or polynomial_degree <= 0):
            result = "Please select valid kernel type"
        elif c_value is None:
            result = "Please select C value"
        elif epsilon_value is None:
            result = "Please select epsilon value"
    else:
        result = "Please select a model type"
    return result


@app.callback(Output('model_editor_feedback_container', 'children'),
              [Input('create_model_button', 'n_clicks')],
              [State('model_name_input', 'value'),
               State('model_type_select', 'value'),
               State('estimator_count_input', 'value'),
               State('enable_max_tree_depth_checkbox', 'value'),
               State('max_tree_depth_input', 'value'),
               State('kernel_type_select', 'value'),
               State('polynomial_degree_input', 'value'),
               State('c_value_input', 'value'),
               State('epsilon_value_input', 'value'),
               State('dataset_select', 'value'),
               State('enable_use_entire_dataset', 'value'),
               State('training_examples_count_input', 'value'),
               State('inflation_adjustment_select', 'value'),
               State('parameter_select', 'values'),
               State('composite_model_select', 'values')])
def create_model(n_clicks, model_name, model_type, estimator_count, enable_max_tree_depth, max_tree_depth, kernel_type,
                 polynomial_degree, c_value, epsilon_value, dataset, enable_use_entire_dataset, training_examples_count,
                 inflation_adjustment_type, input_parameters, input_models):
    # Catch for when callback is called on page load
    if n_clicks is None:
        return ""
    validation_result = validate_model_input(model_name, model_type, estimator_count, enable_max_tree_depth,
                                             max_tree_depth, kernel_type, polynomial_degree, c_value, epsilon_value,
                                             dataset, enable_use_entire_dataset, training_examples_count,
                                             inflation_adjustment_type, input_parameters, input_models)
    if validation_result != "":
        feedback_colour = 'red'
        feedback_message = validation_result
    else:
        settings = {'name': model_name, 'type': model_type, 'dataset': dataset, 'input_parameters': input_parameters,
                    'input_models': input_models}
        if enable_use_entire_dataset == 'enable_use_entire_dataset':
            settings['max_training_examples'] = MAX_TRAINING_ENTRIES
        else:
            settings['max_training_examples'] = training_examples_count
        if model_type == 'decision_tree':
            settings['estimator_count'] = estimator_count
            if enable_max_tree_depth != 'enabled_max_tree_depth':
                settings['max_tree_depth'] = None
            else:
                settings['max_tree_depth'] = max_tree_depth
        elif model_type == 'svm':
            settings['kernel_type'] = kernel_type
            if kernel_type == 'polynomial':
                settings['polynomial_degree'] = polynomial_degree
            settings['c_value '] = c_value
            settings['epsilon_value'] = epsilon_value
        model_manager.add_new_model(settings)
        feedback_colour = 'lime'
        feedback_message = "Model successfully created"
    return html.Div(feedback_message, style={'background-color': feedback_colour})


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


@app.callback(Output('decision_tree_options_container', 'style'),
              [Input('model_type_select', 'value')])
def update_decision_tree_options_display(model_selected):
    if model_selected == 'decision_tree':
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


@app.callback(Output('composite_model_select', 'options'),
              [Input('create_model_button', 'n_clicks'),
               Input('dataset_select', 'value')])
def update_available_input_models(n_clicks, dataset_name):
    return [{'label': model_name, 'value': model_name}
            for model_name in model_manager.get_model_names(dataset_name=dataset_name)]


@app.callback(Output('parameter_select', 'options'),
              [Input('dataset_select', 'value')])
def update_available_input_parameters(dataset_name):
    return [{'label': parameter_name, 'value': parameter_name}
            for parameter_name in model_manager.get_available_inputs(dataset_name)]