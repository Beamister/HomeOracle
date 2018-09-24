import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from server import *
import dash_table_experiments as dt
import dataView, propertyView, sourcesView, modelsView


app.css.append_css({'external_url' : 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})
app.layout = html.Div([
    #dcc.Location(id='url', refresh=False),
    dcc.Tabs(tabs=[{'label' : 'Home', 'value' : 'home'},
                   {'label' : 'Data View', 'value' : 'dataView'},
                   {'label' : 'Property View', 'value' : 'propertyView'},
                   {'label' : 'Models View', 'value': 'modelsView'},
                   {'label' : 'Sources View', 'value': 'sourcesView'}],
             id='tabs',
             value='dataView'),
    html.Div(id='page-content'),
    #Hidden table required due to Dash design flaw, ensures table module is loaded
    html.Div(dt.DataTable(rows=[{}]), style={'display' : 'none'}),
    ]
)

@app.callback(Output('page-content', 'children'),
              [Input('tabs', 'value')])
def display_page(value):
    if value == 'dataView':
        return dataView.layout
    elif value == 'propertyView':
        return  propertyView.layout
    elif value == 'modelsView':
        return modelsView.layout
    elif value == 'sourcesView':
        return sourcesView.layout
    else:
        return 'Welcome to the home page'

application = app.server

if __name__ == '__main__':
    application = app
    application.run_server(debug=True)
