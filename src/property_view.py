import dash_html_components as html
import dash_core_components as dcc
import plotly.offline as plotly
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from server import *
from constants import *

map_data = [
    go.Scattermapbox(
        lat=['45.5017'],
        lon=['-73.5673'],
        mode='markers',
        marker=dict(
            size=14
        ),
        text=['Montreal'],
    )
]

map_layout = go.Layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=MAPBOX_ACCESS_TOKEN,
        bearing=0,
        center=dict(
            lat=45,
            lon=-73
        ),
        pitch=0,
        zoom=5
    ),
)


layout = html.Div(children=[
    html.H1("Property Value Predictor"),
    dcc.Graph(id='map_container',
              figure=go.Figure(data=map_data,
                               layout=map_layout
                               )
              ),
    html.Div("Postcode:"),
    dcc.Input(id='postcode_input'),
    html.Div("Select Model:"),
    dcc.Dropdown(id='model_select'),
    html.Div("Input start and end area values"),
    html.Div(id='parameter_input_container'),
    dcc.Input(id='current_price'),
    html.Button("Predict",
                id='predict_button'
                )
])
