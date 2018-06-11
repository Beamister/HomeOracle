import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from server import *
import dash_table_experiments as dt
import dataView


app.layout = html.Div([
    #dcc.Location(id='url', refresh=False),
    dcc.Tabs(tabs=[{'label' : 'Home', 'value' : 'home'},
                   {'label' : 'Data Viewer', 'value' : 'dataView'}],
             id='tabs',
             value='dataView'),
    html.Div(id='page-content'),
    #Hidden table required due to Dash design flaw, ensures table module is loaded
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
])

@app.callback(Output('page-content', 'children'),
              [Input('tabs', 'value')])
def display_page(value):
    if value == 'dataView':
        return dataView.layout
    elif value == 'home':
        return 'Welcome to the home page'
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)