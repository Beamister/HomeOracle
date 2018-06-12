from os import listdir
from os.path import isfile, join
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import plotly.graph_objs as go
from sklearn import linear_model as lm
from numpy import *
from server import *
from constants import *

dataFileList = [f for f in listdir(dataDirectoryPath) if isfile(join(dataDirectoryPath, f))]
defaultData = pd.read_csv(defaultDataPath, sep='\s+', names=defaultDataHeaders)

dataStore = {"housing.csv": defaultData}

layout = html.Div(
    [
        html.H1(children="Raw Data View", id="title"),
        html.Div(
            [
                html.Div(
                    [
                        html.Div('Select Data File', style={'display': 'block'}),
                        dcc.Dropdown(
                            id='fileSelect',
                            options=[{'label': i, 'value': i} for i in list(dataFileList)],
                            clearable=False,
                            value=dataFileList[0]
                        )
                    ],
                    style={'display': 'block', 'width': '30%'}
                ),
                html.Div(
                    [
                        html.Div('Select Graph Dimensionality', style={'display': 'block'}),
                        dcc.RadioItems(
                            id='dimensionSelect',
                            options=
                            [
                                {'label': '2D', 'value': '2D'},
                                {'label': '3D', 'value': '3D'}
                            ],
                            value='2D',
                            style={'display': 'inline-flex'}
                        ),
                    ],
                    style={'display': 'inline'}
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div('Select X axis'),
                                dcc.Dropdown(
                                    id='XAxisSelect',
                                    clearable=False,
                                    options=[''],
                                    value=''
                                )
                            ],
                            style={'display': 'inline-block', 'width': '30%'}
                        ),
                        html.Div(
                            [
                                html.Div('Select Y axis'),
                                dcc.Dropdown(
                                    id='YAxisSelect',
                                    clearable=False,
                                    options=[''],
                                    value=''
                                )
                            ],
                            style={'display': 'inline-block', 'width': '30%'}
                        ),
                        html.Div(
                            [
                                html.Div('Select Z axis'),
                                dcc.Dropdown(
                                    id='ZAxisSelect',
                                    clearable=False,
                                    options=[''],
                                    value=''
                                )
                            ],
                            id='ZSelectContainer',
                            style={'display': 'none'}
                        )
                    ],
                    style={'display': 'flex'}
                )
            ],
            style={'width': '100%', 'display': 'block'}),

         dcc.Graph(id='graphView'),
         dt.DataTable(
            id='tableView',
            row_selectable=True,
            rows=[{}],
            editable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[]
        )
    ])

@app.callback(
    dash.dependencies.Output('tableView', 'rows'),
    [dash.dependencies.Input('fileSelect', 'value')])
def updateTable(selectedFile):
    if not (selectedFile in dataStore):
        dataStore[selectedFile] = pd.read_csv("Data/" + selectedFile, sep='\s+')
    return dataStore[selectedFile].to_dict('records')


@app.callback(
    dash.dependencies.Output('XAxisSelect', 'options'),
    [dash.dependencies.Input('fileSelect', 'value')])
def updateXAxisSelectOptions(selectedFile):
    return [{'label': i, 'value': i} for i in list(dataStore[selectedFile])]


@app.callback(dash.dependencies.Output('XAxisSelect', 'value'),
              [dash.dependencies.Input('XAxisSelect', 'options')])
def updateXAxisSelectValue(options):
    return options[0]['value']


@app.callback(
    dash.dependencies.Output('YAxisSelect', 'options'),
    [dash.dependencies.Input('fileSelect', 'value')])
def updateYAxisSelectOptions(selectedFile):
    return [{'label': i, 'value': i} for i in list(dataStore[selectedFile])]


@app.callback(dash.dependencies.Output('YAxisSelect', 'value'),
              [dash.dependencies.Input('YAxisSelect', 'options')])
def updateYAxisSelectValue(options):
    return options[0]['value']


@app.callback(
    dash.dependencies.Output('ZAxisSelect', 'options'),
    [dash.dependencies.Input('fileSelect', 'value')])
def updateZAxisSelectOptions(selectedFile):
    return [{'label': i, 'value': i} for i in list(dataStore[selectedFile])]


@app.callback(dash.dependencies.Output('ZAxisSelect', 'value'),
              [dash.dependencies.Input('ZAxisSelect', 'options')])
def updateXAxisSelectValue(options):
    return options[0]['value']


@app.callback(
    dash.dependencies.Output('ZSelectContainer', 'style'),
    [dash.dependencies.Input('dimensionSelect', 'value')])
def updateInputDimensions(selectedDimension):
    if (selectedDimension == '2D'):
        return {'display': 'none'}
    else:
        return {'display': 'inline-block', 'width': '30%'}

@app.callback(
    dash.dependencies.Output('tableView', 'selected_row_indices'),
    [dash.dependencies.Input('graphView', 'clickData')],
    [dash.dependencies.State('tableView', 'selected_row_indices')])
def highlightClickDataPointsInTable(clickData, selectedIndices):
    if clickData:
        for point in clickData['points']:
            if point['pointNumber'] in selectedIndices:
                selectedIndices.remove(point['pointNumber'])
            else:
                selectedIndices.append(point['pointNumber'])
    return selectedIndices

@app.callback(
    dash.dependencies.Output('graphView', 'figure'),
    [dash.dependencies.Input('dimensionSelect', 'value'),
     dash.dependencies.Input('XAxisSelect', 'value'),
     dash.dependencies.Input('YAxisSelect', 'value'),
     dash.dependencies.Input('ZAxisSelect', 'value'),
     dash.dependencies.Input('tableView', 'rows'),
     dash.dependencies.Input('tableView', 'selected_row_indices')],
    [dash.dependencies.State('graphView', 'figure')])
def update_graph(dimensionSelect, xaxisName, yaxisName, zaxisName, rows, selectedIndices, oldFigure):
    dataFrame = pd.DataFrame(rows)
    markerColours = [blue] * len(dataFrame)
    if(selectedIndices != None):
        for i in (selectedIndices):
            markerColours[i] = orange
    if dimensionSelect == '2D':
        linearModel = lm.LinearRegression()
        a1 = array(dataFrame[xaxisName], ndmin=2).transpose()
        a2 = array(dataFrame[yaxisName], ndmin=2).transpose()
        linearModel.fit(a1, a2)
        return {
            'data':
                [
                    go.Scattergl(
                        name='data',
                        x=dataFrame[xaxisName],
                        y=dataFrame[yaxisName],
                        text="({}, {})".format(xaxisName, yaxisName),
                        mode='markers',
                        marker={
                            'size': 15,
                            'opacity': 0.5,
                            'color' : markerColours
                        }
                    ),
                    go.Scattergl(
                        name='Regression Line',
                        x=[dataFrame[xaxisName].min(), dataFrame[xaxisName].max()],
                        y=[linearModel.predict(dataFrame[xaxisName].min())[0][0],
                           linearModel.predict(dataFrame[xaxisName].max())[0][0]],
                        mode='line',
                        line={'color': 'black', 'width': 5}
                    )

                ],
            'layout': go.Layout(
                title="{} Over {}".format(yaxisName, xaxisName),
                xaxis={
                    'title': xaxisName,
                    'type': 'linear'
                },
                yaxis={
                    'title': yaxisName,
                    'type': 'linear'
                },
                margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
                hovermode='closest'
            )
        }
    else:
        if oldFigure['data'][0]['type'] == 'scatter3d':
            camera = oldFigure['layout']['scene']['camera']
        else:
            camera = default3DCamera
        return {
            'data':
                [
                    go.Scatter3d(
                        name='data',
                        x=dataFrame[xaxisName],
                        y=dataFrame[yaxisName],
                        z=dataFrame[zaxisName],
                        text="({}, {}, {})".format(xaxisName, yaxisName, zaxisName),
                        mode='markers',
                        marker={
                            'size': 15,
                            'opacity': 0.5,
                            'color' : markerColours
                        }
                    )
                ],
            'layout': go.Layout(
                title="{} Over {} Over {}".format(yaxisName, xaxisName, zaxisName),
                margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
                hovermode='closest',
                scene=go.Scene(
                    camera=camera,
                    xaxis=go.XAxis(title=xaxisName),
                    yaxis=go.YAxis(title=yaxisName),
                    zaxis=go.ZAxis(title=zaxisName),
                )
            )
        }


if __name__ == '__main__':
    app.run_server()