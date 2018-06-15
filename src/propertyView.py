import dash_core_components as dcc
import dash_html_components as html

layout = html.Div(
    [
        html.H1(children='Property View', id='title'),
        html.Div(id='houseSelectContainer'),
        html.Div(id='areaAttributesContainer'),
        html.Div(id='outputsContainer')
    ]
)