import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from tables import Locations, Session
from server import *
from constants import *


parameter_input_containers = []
for input_index in range(model_manager.get_max_model_inputs()):
        new_container = html.Div(id='parameter_input_container-' + str(input_index),
                                 style={'display': 'flex', 'justify-content': 'space-around'},
                                 children=[
                                     html.Div(style={'display': 'flex-box', 'width': '48%'},
                                              children=[
                                                  html.Div(id='start_parameter_text-' + str(input_index)),
                                                  dcc.Input(id='start_parameter_input-' + str(input_index),
                                                            type='number',
                                                            value=0
                                                            ),
                                              ]),
                                     html.Div(style={'display': 'flex-box', 'width': '48%'},
                                              children=[
                                                  html.Div(id='end_parameter_text-' + str(input_index)),
                                                  dcc.Input(id='end_parameter_input-' + str(input_index),
                                                            type='number',
                                                            value=0
                                                            )
                                              ]),
                                 ])
        parameter_input_containers.append(new_container)

map_data = [
        go.Scattermapbox(
            lat=[str(DEFAULT_MAP_LATITUDE)],
            lon=[str(DEFAULT_MAP_LONGITUDE)],
            mode='markers',
            marker=dict(
                size=14
            )
        )
    ]
map_layout = go.Layout(
    autosize=True,
    hovermode='closest',
    margin={'l': 0, 'r': 5, 't': 0, 'b': 0},
    mapbox=dict(
        accesstoken=MAPBOX_ACCESS_TOKEN,
        bearing=0,
        center=dict(
            lat=DEFAULT_MAP_LATITUDE,
            lon=DEFAULT_MAP_LONGITUDE
        ),
        pitch=0,
        zoom=8
    ),
)

layout = html.Div(children=[
    html.H1("Property Value Predictor"),
    html.Div(id='property_predictor_feedback_container'),
    html.Div(id='top_container',
             style={'display': 'flex', 'justify-content': 'space-around', 'height': '15em'},
             children=[
                dcc.Graph(id='map_container',
                          style={'display': 'flex-box', 'width': '48%', 'height': '15em'},
                          figure=go.Figure(data=map_data,
                                           layout=map_layout
                                           )
                          ),
                html.Div(id='top_right_container',
                         style={'display': 'flex-box', 'width': '48%'},
                         children=[
                            html.Div("Postcode:"),
                            dcc.Input(id='postcode_input',
                                      style={'width': '70%', 'padding': '0'},
                                      type='text'
                                      ),
                            html.Button("Auto Fill",
                                        id='auto_fill_button',
                                        style={'width': '30%', 'padding': '0'}
                                        ),
                            html.Div("Select Model:"),
                            dcc.Dropdown(id='predictor_model_select',
                                         clearable=False,
                                         options=[{'label': model_name, 'value': model_name}
                                                  for model_name in model_manager.get_trained_model_names()],
                                         value=(model_manager.get_trained_model_names()[0] if
                                                len(model_manager.get_trained_model_names()) > 0
                                                else '')
                                         ),
                            html.Div("Current Price:"),
                            dcc.Input(id='current_price_input',
                                      style={'width': '70%', 'padding': '0'},
                                      type='number',
                                      value=0
                                      ),
                            html.Button("Predict",
                                        id='predict_button',
                                        style={'width': '30%', 'padding': '0'}
                                        ),
                            html.Div(id='prediction_container',
                                     children=""
                                     ),
                            html.Div(id='dummy_predictions_container',
                                     style={'display': 'none'},
                                     children=[html.Div(id='dummy_prediction_' + model_name)
                                               for model_name in model_manager.get_trained_model_names()]
                                     ),
                         ])
             ]),
    html.Br(),
    html.Div(id='parameter_input_container',
             children=parameter_input_containers
             ),
])


@app.callback(Output('predict_button', 'style'),
              [Input('predictor_model_select', 'value')])
def update_predict_button_display(model_select):
    if model_select is None or model_select == '':
        return {'display': 'none', 'width': '30%', 'padding': '0'}
    else:
        return {'width': '30%', 'padding': '0'}


def get_lat_and_long(postcode):
    session = Session()
    postcode_record = session.query(Locations).filter(Locations.pcds == postcode).first()
    session.close()
    if postcode_record is not None:
        return postcode_record.lat, postcode_record.long
    else:
        return None, None


@app.callback(Output('map_container', 'figure'),
              [Input('auto_fill_button', 'n_clicks')],
              [State('postcode_input', 'value')])
def update_map(n_clicks, postcode):
    if n_clicks is None:
        latitude = DEFAULT_MAP_LATITUDE
        longitude = DEFAULT_MAP_LONGITUDE
    else:
        postcode_conversion_result = get_lat_and_long(postcode)
        if postcode_conversion_result is not None:
            latitude = postcode_conversion_result[0]
            longitude = postcode_conversion_result[1]
        else:
            latitude = DEFAULT_MAP_LATITUDE
            longitude = DEFAULT_MAP_LONGITUDE
    map_data = [
        go.Scattermapbox(
            lat=[str(latitude)],
            lon=[str(longitude)],
            mode='markers',
            marker=dict(
                size=14
            ),
            text=[postcode],
        )
    ]
    map_layout = go.Layout(
        autosize=True,
        hovermode='closest',
        margin={'l': 0, 'r': 5, 't': 0, 'b': 0},
        mapbox=dict(
            accesstoken=MAPBOX_ACCESS_TOKEN,
            bearing=0,
            center=dict(
                lat=latitude,
                lon=longitude
            ),
            pitch=0,
            zoom=8
        ),
    )
    figure = go.Figure(data=map_data,
                       layout=map_layout
                       )
    return figure


def create_update_input_display_function(id_number):
    def update_container_display(model_name):
        if model_name == '' or id_number >= len(model_manager.get_model_inputs(model_name)):
            return {'display': 'none'}
        else:
            return {'display': 'flex', 'justify-content': 'space-around'}
    return update_container_display


for input_index in range(model_manager.get_max_model_inputs()):
    update_display_function = create_update_input_display_function(input_index)
    app.callback(Output('parameter_input_container-' + str(input_index), 'style'),
                 [Input('predictor_model_select', 'value')])(update_display_function)


def create_update_input_text_function(id_number, base_text):
    def update_input_text(model_name):
        if model_name == '':
            return ""
        model_inputs = model_manager.get_model_inputs(model_name)
        if id_number < len(model_inputs):
            return base_text + model_inputs[id_number] + ":"
        else:
            return ""
    return update_input_text


for input_index in range(model_manager.get_max_model_inputs()):
    start_update_text_function = create_update_input_text_function(input_index, "Start ")
    end_update_text_function = create_update_input_text_function(input_index, "End ")
    app.callback(Output('start_parameter_text-' + str(input_index), 'children'),
                 [Input('predictor_model_select', 'value')])(start_update_text_function)
    app.callback(Output('end_parameter_text-' + str(input_index), 'children'),
                 [Input('predictor_model_select', 'value')])(end_update_text_function)


@app.callback(Output('prediction_container', 'children'),
              [Input('predict_button', 'n_clicks')],
              [State('predictor_model_select', 'value'),
               State('current_price_input', 'value')]
              + [State('start_parameter_input-' + str(input_index), 'value')
                 for input_index in range(model_manager.get_max_model_inputs())]
              + [State('end_parameter_input-' + str(input_index), 'value')
                 for input_index in range(model_manager.get_max_model_inputs())])
def update_prediction(n_clicks, model_name, current_price, *parameter_inputs):
    # Catch for call on page load
    if n_clicks is None:
        return "Predicted Price: "
    max_model_input = model_manager.get_max_model_inputs()
    model_input_count = len(model_manager.get_model_inputs(model_name))
    start_parameter_inputs = parameter_inputs[0: model_input_count]
    end_parameter_inputs = parameter_inputs[max_model_input: (max_model_input + model_input_count)]
    # Check for invalid input
    if current_price is None or None in start_parameter_inputs or None in end_parameter_inputs:
        return "Invalid input"
    predicted_price = model_manager.get_prediction(model_name, current_price,
                                                   start_parameter_inputs, end_parameter_inputs)
    return "Predicted Price: " + str(predicted_price)
