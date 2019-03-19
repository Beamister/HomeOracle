from os import listdir
from os.path import isfile, join

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from numpy import *
from sklearn import linear_model as lm

from constants import *
from server import *

data_file_list = [f for f in listdir(DATA_DIRECTORY_PATH) if isfile(join(DATA_DIRECTORY_PATH, f))]
default_data = pd.read_csv(DEFAULT_DATA_PATH, sep='\s+', names=DEFAULT_DATA_HEADERS)
sorted_headers = sorted(list(DEFAULT_DATA_HEADERS))
default_data = default_data[sorted_headers]

data_store = {DEFAULT_DATA_FILE: default_data}

layout = html.Div(
    [
        html.H1(children='Raw Data View', id='title'),
        html.Div(
            [
                html.Div(
                    [
                        html.Div('Select Data File', style={'display': 'block'}),
                        dcc.Dropdown(
                            id='fileSelect',
                            options=[{'label': i, 'value': i} for i in list(data_file_list)],
                            clearable=False,
                            value=data_file_list[0]
                        )
                    ],
                    style={'display': 'block', 'width': '30%'}
                ),
                html.Div(
                    [
                        html.Div('Select Graph Dimensionality', style={'display': 'block'}),
                        dcc.RadioItems(
                            id='dimensionSelect',
                            options=[
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
            id='inputsContainer',
            style={'width': '100%', 'display': 'block'}
        ),

        html.H2('Graph View'),
        dcc.Graph(id='graphView'),
        html.H2('Table View'),
        dt.DataTable(
            id='tableView',
            row_selectable=True,
            rows=[{}],
            editable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[]
        ),
        html.H2('Data Summary'),
        dt.DataTable(
            id='dataDescription',
            row_selectable=False,
            rows=[{}],
            editable=False,
            filterable=False,
            sortable=False
        )
    ]
)


@app.callback(
    Output('tableView', 'rows'),
    [Input('fileSelect', 'value')])
def update_table(selected_file):
    if not (selected_file in data_store):
        new_data = pd.read_csv('Data/' + selected_file, sep='\s+')
        local_sorted_headers = sort(data_store[selected_file].columns.tolist())
        new_data = new_data[local_sorted_headers]
        data_store[selected_file] = new_data
    return data_store[selected_file].to_dict('records')


@app.callback(
    Output('XAxisSelect', 'options'),
    [Input('fileSelect', 'value')])
def update_x_axis_select_options(selected_file):
    return [{'label': i, 'value': i} for i in list(data_store[selected_file])]


@app.callback(Output('XAxisSelect', 'value'),
              [Input('XAxisSelect', 'options')])
def update_x_axis_select_value(options):
    return options[0]['value']


@app.callback(
    Output('YAxisSelect', 'options'),
    [Input('fileSelect', 'value')])
def update_y_axis_select_options(selected_file):
    return [{'label': i, 'value': i} for i in list(data_store[selected_file])]


@app.callback(Output('YAxisSelect', 'value'),
              [Input('YAxisSelect', 'options')])
def update_y_axis_select_value(options):
    return options[0]['value']


@app.callback(
    Output('ZAxisSelect', 'options'),
    [Input('fileSelect', 'value')])
def update_z_axis_select_options(selected_file):
    return [{'label': i, 'value': i} for i in list(data_store[selected_file])]


@app.callback(Output('ZAxisSelect', 'value'),
              [Input('ZAxisSelect', 'options')])
def update_x_axis_select_value(options):
    return options[0]['value']


@app.callback(
    Output('ZSelectContainer', 'style'),
    [Input('dimensionSelect', 'value')])
def update_input_dimensions(selected_dimension):
    if selected_dimension == '2D':
        return {'display': 'none'}
    else:
        return {'display': 'inline-block', 'width': '30%'}


@app.callback(
    Output('tableView', 'selected_row_indices'),
    [Input('graphView', 'clickData')],
    [State('tableView', 'selected_row_indices')])
def highlight_click_data_points_in_table(click_data, selected_indices):
    if click_data:
        for point in click_data['points']:
            if point['pointNumber'] in selected_indices:
                selected_indices.remove(point['pointNumber'])
            else:
                selected_indices.append(point['pointNumber'])
    return selected_indices


@app.callback(
    Output('graphView', 'figure'),
    [Input('dimensionSelect', 'value'),
     Input('XAxisSelect', 'value'),
     Input('YAxisSelect', 'value'),
     Input('ZAxisSelect', 'value'),
     Input('tableView', 'rows'),
     Input('tableView', 'selected_row_indices')],
    [State('graphView', 'figure')])
def update_graph(dimension_select, xaxis_name, yaxis_name, zaxis_name, rows, selected_indices, old_figure):
    data_frame = pd.DataFrame(rows)
    marker_colours = [BLUE] * len(data_frame)
    if selected_indices is not None:
        for i in selected_indices:
            marker_colours[i] = ORANGE
    if dimension_select == '2D':
        linear_model = lm.LinearRegression()
        a1 = array(data_frame[xaxis_name], ndmin=2).transpose()
        a2 = array(data_frame[yaxis_name], ndmin=2).transpose()
        linear_model.fit(a1, a2)
        return {
            'data':
                [
                    go.Scattergl(
                        name='data',
                        x=data_frame[xaxis_name],
                        y=data_frame[yaxis_name],
                        text="({}, {})".format(xaxis_name, yaxis_name),
                        mode='markers',
                        marker={
                            'size': 15,
                            'opacity': 0.5,
                            'color': marker_colours
                        }
                    ),
                    go.Scattergl(
                        name='Regression Line',
                        x=[data_frame[xaxis_name].min(), data_frame[xaxis_name].max()],
                        y=[linear_model.predict([[data_frame[xaxis_name].min()]])[0][0],
                           linear_model.predict([[data_frame[xaxis_name].max()]])[0][0]],
                        mode='line',
                        line={'color': 'black', 'width': 5}
                    )

                ],
            'layout':
                go.Layout(
                    height=800,
                    width=1300,
                    title="{} Over {}".format(yaxis_name, xaxis_name),
                    xaxis={
                        'title': xaxis_name,
                        'type': 'linear'
                    },
                    yaxis={
                        'title': yaxis_name,
                        'type': 'linear'
                    },
                    margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
                    hovermode='closest'
                )
        }
    else:
        if old_figure['data'][0]['type'] == 'scatter3d':
            camera = old_figure['layout']['scene']['camera']
        else:
            camera = DEFAULT_3D_CAMERA
        return {
            'data':
                [
                    go.Scatter3d(
                        name='data',
                        x=data_frame[xaxis_name],
                        y=data_frame[yaxis_name],
                        z=data_frame[zaxis_name],
                        text="({}, {}, {})".format(xaxis_name, yaxis_name, zaxis_name),
                        mode='markers',
                        marker={
                            'size': 4,
                            'opacity': 0.5,
                            'color': marker_colours
                        }
                    )
                ],
            'layout':
                go.Layout(
                    height=800,
                    width=1300,
                    title="{} Over {} Over {}".format(yaxis_name, xaxis_name, zaxis_name),
                    margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
                    hovermode='closest',
                    scene=go.Scene(
                        camera=camera,
                        xaxis=go.XAxis(title=xaxis_name),
                        yaxis=go.YAxis(title=yaxis_name),
                        zaxis=go.ZAxis(title=zaxis_name),
                    )
                )
        }


@app.callback(
    Output('dataDescription', 'rows'),
    [Input('tableView', 'rows')])
def update_description(data):
    data_descriptions = pd.DataFrame(data).describe()
    describtion_headers = data_descriptions.columns.tolist()
    data_descriptions['Attributes'] = pd.Series(SUMMARY_ATTRIBUTES, index=data_descriptions.index)
    # Reorder so attributes are at the left of the table
    data_descriptions = data_descriptions[['Attributes'] + describtion_headers]
    return data_descriptions.to_dict('records')


if __name__ == '__main__':
    app.run_server()
