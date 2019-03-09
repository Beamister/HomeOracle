from datetime import datetime as dt

import boto3
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from tables import add_column, get_indicators
from constants import *
from server import *

indicator_name_containers = []
for index in range(MAX_SOURCE_COLUMN_COUNT):
    indicator_name_input_id = 'indicatorNameInput-' + str(index)
    indicator_column_input_id = 'indicatorColumnInput-' + str(index)
    indicator_name_label = html.Div("Indicator " + str(index + 1) + ":")
    indicatorNameInput = dcc.Input(id=indicator_name_input_id,
                                   type='text',
                                   value='',
                                   max=40,
                                   placeholder="Name",
                                   style={'width': '80%'})
    indicator_column_input = dcc.Input(id=indicator_column_input_id,
                                       type='number',
                                       value='',
                                       size=60,
                                       min=0,
                                       max=100,
                                       step=1,
                                       placeholder="Column",
                                       style={"width": '20%'})
    indicator_name_container = html.Div(id='indicatorContainer-' + str(index),
                                        children=[indicator_name_label, indicatorNameInput, indicator_column_input],
                                        style={'display': 'none'})
    indicator_name_containers.append(indicator_name_container)

layout = html.Div(children=[
    html.H4("Source Input"),
    html.Div(id='sources_view_feedback_container'),
    html.Div(id='inputsContainer',
             style={'display': 'flex', 'justify-content': 'space-around'},
             children=[
                 html.Div(id='leftInputContainer',
                          style={'display': 'flex-box', 'width': '48%'},
                          children=[
                              html.Div("Source Name:"),
                              dcc.Input(id='sourceNameInput',
                                        value='',
                                        type='text',
                                        style={'width': '100%'}),
                              html.Div(id='description', children="How to use source input"),
                              dcc.Input(id='sourceURLInput',
                                        value='',
                                        type='text',
                                        style={'width': '100%'}),
                              html.Div(id='startAndLocationColumnSelectContainer',
                                       style={'display': 'flex'},
                                       children=[
                                           html.Div(id='startSelectContainer',
                                                    style={'display': 'flex-box', 'width': '50%'},
                                                    children=[
                                                        dcc.RadioItems(id='startOptionSelect',
                                                                       options=[{'label': "Start today",
                                                                                 'value': 'startNow'},
                                                                                {'label': "Start from date",
                                                                                 'value': 'setDate'}],
                                                                       value='startNow'),
                                                        html.Div(id='startDateContainer',
                                                                 style={'display': 'none'},
                                                                 children=[
                                                                     html.Div("Start date:"),
                                                                     dcc.DatePickerSingle(id='startDateSelect',
                                                                                          display_format='DD/MM/YYYY',
                                                                                          first_day_of_week=1,
                                                                                          number_of_months_shown=3,
                                                                                          with_full_screen_portal=True,
                                                                                          initial_visible_month=dt.now()
                                                                                          )
                                                                 ])
                                                    ]),
                                           html.Div(id='locationSelectContainer',
                                                    style={'display': 'flex-box', 'width': '50%'},
                                                    children=[
                                                        html.Div("Location column index:"),
                                                        dcc.Input(id='locationColumnInput',
                                                                  style={'width': '50%'},
                                                                  type='number',
                                                                  value='',
                                                                  size=100,
                                                                  min=0,
                                                                  max=100,
                                                                  step=1,
                                                                  placeholder="Location", )
                                                    ]),
                                       ]),
                              html.Div("Select update frequency:"),
                              dcc.Dropdown(id='frequencySelect',
                                           options=[{'label': FREQUENCIES[value], 'value': value}
                                                    for value in FREQUENCIES]),
                              html.Div("Select location resolution:"),
                              dcc.Dropdown(id='resolutionSelect',
                                           options=[{'label': AREA_RESOLUTIONS[value], 'value': value}
                                                    for value in AREA_RESOLUTIONS]),
                              html.Div("Select number of indicators:"),
                              html.Div(id='indicatorCountContainer',
                                       children=[
                                           dcc.Slider(id='indicatorCountSelect',
                                                      min=1,
                                                      max=MAX_SOURCE_COLUMN_COUNT,
                                                      step=1,
                                                      value=1)],
                                       style={'width': '90%', 'display': 'inline-block'}),
                              html.Div(id='indicatorCountlabel',
                                       style={'display': 'inline-block', 'width': '10%', 'text-align': 'center'}),
                              html.Button("Save", id='addSourceButton', style={'margin': '2em'})]),
                 html.Div(id='indicatorNamesTopContainer',
                          children=indicator_name_containers,
                          style={'display': 'flex-box', 'width': '48%'}, )
             ])
])


@app.callback(Output('startDateContainer', 'style'),
              [Input('startOptionSelect', 'value')])
def update_calendar_display(start_option):
    if start_option == 'startNow':
        return {'display': 'none'}
    else:
        return {'display': 'block'}


def create_update_input_display_function(indicator_index):
    def update_container_display(indicator_count):
        if indicator_index < indicator_count:
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    return update_container_display


for index in range(MAX_SOURCE_COLUMN_COUNT):
    update_function = create_update_input_display_function(index)
    app.callback(Output('indicatorContainer-' + str(index), 'style'),
                 [Input('indicatorCountSelect', 'value')])(update_function)


def validate_input(source_name, source_url, start_date, location_column_index, frequency,
                   indicator_count, resolution, start_option, indicator_names_and_columns):
    feedback_message = ""
    if source_name == '':
        feedback_message = "Please add a source name"
    elif source_url == '':
        feedback_message = "Please add a source URL"
    elif start_option != 'startNow' and start_date is None:
        feedback_message = "Please select start date"
    elif location_column_index == '':
        feedback_message = "Please select a column index for the loaction"
    elif frequency is None:
        feedback_message = "Please select an update frequency"
    elif resolution is None:
        feedback_message = "Please select an area resolution"
    elif '' in indicator_names_and_columns[:indicator_count]:
        feedback_message = "Please ensure that all indicators are given names"
    elif '' in indicator_names_and_columns[MAX_SOURCE_COLUMN_COUNT:MAX_SOURCE_COLUMN_COUNT + indicator_count]:
        feedback_message = "Please ensure that all indicators are given a column index"
    elif len([indicator_name for indicator_name in indicator_names_and_columns[:indicator_count]
              if indicator_name in get_indicators()]) > 0:
        feedback_message = "Indicator name already exists"
    elif start_option == 'setDate' and start_date is None:
        feedback_message = "Please ensure that a start date is set"
    return feedback_message


# takes a date token and splits into separate day, month, year and static tokens
def split_date_token(date_token):
    tokens = []
    token_index = -1
    current_type = None
    quote = False
    for character in date_token:
        if quote:
            tokens[token_index] += character
            if character == '"':
                quote = False
        elif character == '"':
            tokens.append('-s')
            token_index += 1
            tokens.append('')
            token_index += 1
            quote = True
        elif character in ['d', 'm', 'y'] and character != current_type:
            current_type = character
            tokens.append('-' + character)
            token_index += 1
            tokens.append('')
            token_index += 1
            tokens[token_index] += character
        else:
            tokens[token_index] += character
    return tokens


# takes the url input string and process it into a list, splits date tokens into component parts
def process_url_input(url_input_string):
    tokens = url_input_string.split(' ')
    while '-d' in tokens:
        date_token_specifier_index = tokens.index('-d')
        #get the date token after the -d
        date_token = tokens[date_token_specifier_index + 1]
        #remove the date token and its specifier
        del tokens[date_token_specifier_index]
        del tokens[date_token_specifier_index + 1]
        #split up the date token and insert it into the tokens list
        if date_token_specifier_index > len(tokens) - 1:
            tokens = tokens[0: date_token_specifier_index] + split_date_token(date_token)
        else:
            tokens = tokens[0 : date_token_specifier_index] + split_date_token(date_token)\
                     + tokens[date_token_specifier_index :]
    return tokens


@app.callback(Output('sources_view_feedback_container', 'children'),
              [Input('addSourceButton', 'n_clicks')],
              [State('sourceNameInput', 'value'),
               State('sourceURLInput', 'value'),
               State('startDateSelect', 'date'),
               State('locationColumnInput', 'value'),
               State('frequencySelect', 'value'),
               State('indicatorCountSelect', 'value'),
               State('resolutionSelect', 'value'),
               State('startOptionSelect', 'value')]
              + [State('indicatorNameInput-' + str(index), 'value') for index in range(MAX_SOURCE_COLUMN_COUNT)]
              + [State('indicatorColumnInput-' + str(index), 'value') for index in range(MAX_SOURCE_COLUMN_COUNT)])
def add_source_button_clicked(number_of_clicks, source_name, source_url, start_date, location_column_index, frequency,
                              indicator_count, resolution, start_option, *indicator_names_and_columns):
    # Catch for when callback is called on page load
    if number_of_clicks is None:
        return ""
    feedback_colour = 'red'
    validation_result = validate_input(source_name, source_url, start_date, location_column_index, frequency,
                                       indicator_count, resolution, start_option, indicator_names_and_columns)
    if validation_result != "":
        feedback_message = validation_result
    else:
        if start_option == 'startNow':
            start_date = dt.now()
        else:
            start_date = dt.strptime(start_date, '%Y-%m-%d')
        start_date.replace(hour=0, minute=0, second=0)
        start_date_string = start_date.strftime("%d/%m/%Y")
        indicators = {}
        for i in range(indicator_count):
            indicators[indicator_names_and_columns[i]] \
                = str(indicator_names_and_columns[MAX_SOURCE_COLUMN_COUNT + i])
        new_source = {'SourceName': source_name,
                      'sourceTokens': source_url.split(' '),
                      'start_date': start_date_string,
                      'locationColumn': location_column_index,
                      'frequency': frequency,
                      'resolution': resolution,
                      'indicatorCount': indicator_count,
                      'indicators': indicators,
                      'lastUpdate': None}
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
        table = dynamodb.Table('Sources')
        if 'Attributes' in table.put_item(Item=new_source, ReturnValues='ALL_OLD'):
            feedback_message = "Successfully updated source: " + source_name
        else:
            feedback_message = "Successfully added new source: " + source_name
        for indicator in indicators.keys():
            add_column(indicator, database_engine)
        job_manager.update_indicators_metadata()
        job_manager.update_commit_schedule(start_date, frequency)
        job_manager.add_job(start_date, PULL_SOURCE_JOB, source_name)
        feedback_colour = 'lime'
    return html.Div(feedback_message, style={'background-color': feedback_colour})


@app.callback(Output('indicatorCountlabel', 'children'),
              [Input('indicatorCountSelect', 'value')])
def update_indicator_counter(count):
    return str(count)
