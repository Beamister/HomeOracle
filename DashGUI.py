import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import plotly.graph_objs as go
from sklearn import linear_model as lm
from numpy import *
from Prototype.DataStore import DataStore

app = dash.Dash()
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

dataFrame = pd.read_csv("Data/housing.csv", sep = '\s+', names = ["Crime", "Residential", "Industrial", "River Boundary", "Nitric Oxide",
                          "Rooms", "Pre 1940", "Employment distance", "Accessibility", "Tax",
                          "Education", "Black Population", "Lower Status", "Median Value"])

app.layout = html.Div(
    [
        html.H1(children = "Raw Data View", id = "title"),
        html.Div(
            [
                dcc.RadioItems(
                    id = 'dimensionSelect',
                    options =
                    [
                        {'label': '2D', 'value': '2D'},
                        {'label': '3D', 'value': '3D'}
                    ],
                    value = '2D',
                    style={'display': 'table-row'}
                ),
                html.Div(
                    [
                        html.Div('Select X axis'),
                        dcc.Dropdown(
                            id = 'XAxisSelect',
                            options = [{'label' : i, 'value' : i} for i in list(dataFrame)],
                            clearable = False,
                            value = list(dataFrame)[0],
                        )
                    ],
                    style = {'display' : 'table-cell'}
                ),
                html.Div(
                    [
                        html.Div('Select Y axis'),
                        dcc.Dropdown(
                            id = 'YAxisSelect',
                            options = [{'label' : i, 'value' : i} for i in list(dataFrame)],
                            clearable = False,
                            value = list(dataFrame)[1],
                        )
                    ],
                    style = {'display' : 'table-cell'}
                ),
                html.Div(
                    [
                        html.Div('Select Z axis'),
                        dcc.Dropdown(
                            id = 'ZAxisSelect',
                            options = [{'label' : i, 'value' : i} for i in list(dataFrame)],
                            clearable = False,
                            value = list(dataFrame)[2],
                        )
                    ],
                    id = 'ZSelectContainer',
                    style = {'display' : 'table-cell'}
                ),
            ],
            style={'width': '100%', 'display' : 'table'}),

        dcc.Graph(id = 'graphView'),
        dt.DataTable(
            id='tableView',
            rows = dataFrame.to_dict('records'),
            row_selectable = True,
            filterable = True,
            sortable=True,
            selected_row_indices=[]
        )

])

@app.callback(
    dash.dependencies.Output('ZSelectContainer', 'style'),
    [dash.dependencies.Input('dimensionSelect', 'value')])
def updateInputDimensions(selectedDimension):
    if(selectedDimension == '2D'):
        return {'display' : 'none'}
    else:
        return {'display' : 'table-cell'}

@app.callback(
    dash.dependencies.Output('graphView', 'figure'),
    [dash.dependencies.Input('dimensionSelect', 'value'),
     dash.dependencies.Input('XAxisSelect', 'value'),
     dash.dependencies.Input('YAxisSelect', 'value'),
     dash.dependencies.Input('ZAxisSelect', 'value')])
def update_graph(dimensionSelect, xaxisName, yaxisName, zaxisName):
    if(dimensionSelect == '2D'):
        linearModel = lm.LinearRegression()
        linearModel.fit(array(dataFrame[xaxisName], ndmin = 2).transpose(), array(dataFrame[yaxisName], ndmin = 2).transpose())
        return {
            'data':
                [
                    go.Scatter(
                        x = dataFrame[xaxisName],
                        y = dataFrame[yaxisName],
                        text = "(Value, {})".format(xaxisName),
                        mode = 'markers',
                        marker = {
                            'size': 15,
                            'opacity': 0.5,
                            'line': {'width': 0.5, 'color': 'white'}
                        }
                    ),
                    go.Scatter(
                        x = [dataFrame[xaxisName].min(), dataFrame[xaxisName].max()],
                        y = [linearModel.predict(dataFrame[xaxisName].min())[0][0], linearModel.predict(dataFrame[xaxisName].max())[0][0]],
                        mode = 'line',
                        line = {'color' : 'black', 'width' : 5}
                    )

            ],
            'layout': go.Layout(
                title = "{} Over {}".format(yaxisName, xaxisName),
                xaxis = {
                    'title': xaxisName,
                    'type': 'linear'
                },
                yaxis = {
                    'title': yaxisName,
                    'type': 'linear'
                },
                margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
                hovermode = 'closest'
            )
        }
    else:
        return {
            'data':
                [
                    go.Scatter3d(
                        x = dataFrame[xaxisName],
                        y = dataFrame[yaxisName],
                        z = dataFrame[zaxisName],
                        text = "({}, {}, {})".format(xaxisName, yaxisName, zaxisName),
                        mode = 'markers',
                        marker = {
                            'size': 15,
                            'opacity': 0.5
                        }
                    )
                ],
            'layout': go.Layout(
                title = "{} Over {} Over {}".format(yaxisName, xaxisName, zaxisName),
                margin = {'l': 40, 'b': 40, 't': 40, 'r': 40},
                hovermode = 'closest',
                scene = go.Scene(
                    xaxis = go.XAxis(title = xaxisName),
                    yaxis = go.YAxis(title = yaxisName),
                    zaxis = go.ZAxis(title = zaxisName)
                )
            )
        }


if __name__ == '__main__':
    app.run_server()