import dash_core_components as dcc
import dash_html_components as html
import json
from constants import *
from dash.dependencies import Input, Output, State
from server import *
from datetime import datetime as dt

indicatorNameContainers = []
for index in range(maxSourceColumnCount):
    indicatorNameInputID = 'indicatorNameInput-' + str(index)
    indicatorColumnInputID = 'indicatorColumnInput-' + str(index)
    indicatorNameLabel = html.Div("Indicator " + str(index + 1) + ":")
    indicatorNameInput = dcc.Input(id=indicatorNameInputID,
                                   type='text',
                                   value='',
                                   max=40,
                                   placeholder="Name",
                                   style={'width' : '80%'})
    indicatorColumnInput = dcc.Input(id=indicatorColumnInputID,
                                     type='number',
                                     value='',
                                     size=60,
                                     min=0,
                                     max=100,
                                     step=1,
                                     placeholder="Column",
                                     style={"width" : '20%'})
    indicatorNameContainer = html.Div(id='indicatorContainer-' + str(index),
                                      children=[indicatorNameLabel, indicatorNameInput, indicatorColumnInput],
                                      style={'display' : 'none'})
    indicatorNameContainers.append(indicatorNameContainer)

layout = html.Div(children=[
    html.H4("Source Input"),
    html.Div(id='feedbackContainer'),
    html.Div(id='inputsContainer',
             style={'display' : 'flex', 'justify-content' : 'space-around'},
             children=[
        html.Div(id='leftInputContainer',
                 style={'display' : 'flex-box', 'width' : '48%'},
                 children=[
                    html.Div("Source Name:"),
                    dcc.Input(id='sourceNameInput',
                              value='',
                              type='text',
                              style={'width' : '100%'}),
                    html.Div(id='description', children="How to use source input"),
                    dcc.Input(id='sourceURLInput',
                              value='',
                              type='text',
                              style={'width' : '100%'}),
                    dcc.RadioItems(id='startOptionSelect',
                                  options=[{'label' : "Start Immediately", 'value' : 'startNow'},
                                           {'label' : "Start from date", 'value' : 'setDate'}],
                                  value='startNow'),
                    html.Div(id='startDateContainer',
                             style={'display' : 'none'},
                             children=
                                [html.Div("Start date:"),
                                dcc.DatePickerSingle(id='startDateSelect',
                                                     display_format='DD/MM/YYYY',
                                                     first_day_of_week = 1,
                                                     number_of_months_shown=3,
                                                     with_full_screen_portal=True,
                                                     initial_visible_month=dt.now())]),
                    html.Div("Select update frequency:"),
                    dcc.Dropdown(id='frequencySelect',
                                 options=[{'label' : 'Monthly', 'value' : 'monthly'},
                                          {'label' : 'Daily', 'value' : 'daily'},
                                          {'label' : 'Yearly', 'value' : 'yearly'}]),
                    html.Div("Select number of indicators:"),
                    html.Div(id='indicatorCountContainer',
                             children=[
                                dcc.Slider(id='indicatorCountSelect',
                                           min=1,
                                           max=maxSourceColumnCount,
                                           step=1,
                                           value=1)],
                            style = {'width': '90%', 'display': 'inline-block'}),
                    html.Div(id='indicatorCountlabel',
                             style={'display' : 'inline-block', 'width' : '10%', 'text-align' : 'center'}),
                    html.Button("Save", id='addSourceButton', style={'margin': '2em'})]),
        html.Div(id='indicatorNamesTopContainer',
                 children=indicatorNameContainers,
                 style={'display' : 'flex-box', 'width' : '48%'},)
        ])
    ])

@app.callback(Output('startDateContainer', 'style'),
              [Input('startOptionSelect', 'value')])
def updateCalendarDisplay(startOption):
    if startOption == 'startNow':
        return {'display' : 'none'}
    else:
        return {'display' : 'block'}

def createUpdateInputDisplayFuntion(index):
    def updateContainerDisplay(indicatorCount):
        if index < indicatorCount:
            return {'display' : 'block'}
        else:
            return {'display' : 'none'}
    return updateContainerDisplay


for index in range(maxSourceColumnCount):
    updateFunction = createUpdateInputDisplayFuntion(index)
    app.callback(Output('indicatorContainer-' + str(index), 'style'),
                  [Input('indicatorCountSelect', 'value')])(updateFunction)

@app.callback(Output('feedbackContainer', 'children'),
              [Input('addSourceButton', 'n_clicks')],
              [State('sourceNameInput', 'value'),
               State('sourceURLInput', 'value'),
               State('startDateSelect', 'date'),
               State('frequencySelect', 'value'),
               State('indicatorCountSelect', 'value'),
               State('startOptionSelect', 'value')]
              + [State('indicatorNameInput-' + str(index), 'value') for index in range(maxSourceColumnCount)]
              + [State('indicatorColumnInput-' + str(index), 'value') for index in range(maxSourceColumnCount)])
def addSourceButtonClicked(numberOfClicks, sourceName, sourceURL, startDate, frequency,
                           indicatorCount, startOption, *indicatorNamesAndColumns):
    # Catch for when callback is called on page load
    if numberOfClicks == None:
        return ""
    feedbackColor = 'red'
    # Input validation
    if sourceName != '':
        feedbackMessage = "Please add a source name"
    elif sourceURL != '':
        feedbackMessage = "Please add a source URL"
    elif startOption != 'startNow' and startDate == None:
        feedbackMessage = "Please select start date"
    elif frequency == None:
        feedbackMessage = "Please select an update frequency"
    elif '' in indicatorNamesAndColumns[:indicatorCount]:
        feedbackMessage = "Please ensure that all indicators are given names"
    elif '' in indicatorNamesAndColumns[maxSourceColumnCount:maxSourceColumnCount + indicatorCount]:
        feedbackMessage = "Please ensure that all indicators are given a column index"
    else:
        if startOption == 'startNow':
            startDate = dt.now().date().strftime("%d/%m/%Y")
        else:
            startDate = dt.strptime(startDate, '%Y-%m-%d').strftime("%d/%m/%Y")
        indicators = {}
        for i in range(indicatorCount):
            indicators[indicatorNamesAndColumns[i * 2]] = str(indicatorNamesAndColumns[maxSourceColumnCount + i])
        newSource = {'sourceTokens' : sourceURL.split(' '),
                       'startDate' : startDate,
                       'frequency' : frequency,
                       'indicators' : indicators}
        # Add source to file
        sourcesFile = open("sources.json", 'r')
        sourcesFileContents = json.load(sourcesFile)
        sourcesFile.close()
        if sourceName in sourcesFileContents.keys():
            feedbackMessage = "Successfully updated source: " + sourceName
        else:
            feedbackMessage = "Successfully added new source: " + sourceName
        sourcesFileContents[sourceName] = newSource
        sourcesFile = open("sources.json", 'w')
        json.dump(sourcesFileContents, sourcesFile)
        sourcesFile.close()
        feedbackColor = 'lime'
        feedbackMessage = "Successfully added new source"
    return(html.Div(feedbackMessage, style={'background-color' : feedbackColor}))

@app.callback(Output('indicatorCountlabel', 'children'),
              [Input('indicatorCountSelect', 'value')])
def updateIndicatorCounter(count):
    return str(count)