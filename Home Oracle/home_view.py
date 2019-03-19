import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from server import *

description_file = open(DESCRIPTION_FILE_PATH, 'r')
description_text = description_file.read()
description_file.close()

layout = html.Div(children=[
    dcc.Markdown(description_text)
    ],
    style={'margin': '10em', 'margin-top': '2em'}
)