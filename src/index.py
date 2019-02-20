import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output

import data_view
import dynamo_view
import model_editor_view
import property_view
import sources_view
import rds_view
import model_view
from server import *

# app.css.append_css({'external_url' : 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})
app.layout = html.Div([
    # dcc.Location(id='url', refresh=False),
    dcc.Tabs(children=[dcc.Tab(label='Home', value='home', className="myTab"),
                       dcc.Tab(label='Data Viewer', value='dataView', className="myTab"),
                       dcc.Tab(label='Property Predictor', value='propertyView', className="myTab"),
                       dcc.Tab(label='Model Viewer', value='modelView', className="myTab"),
                       dcc.Tab(label='Model Editor', value='modelEditorView', className="myTab"),
                       dcc.Tab(label='Source Input', value='sourcesView', className="myTab"),
                       dcc.Tab(label='Dynamo Viewer', value='dynamoView', className="myTab"),
                       dcc.Tab(label='RDS Viewer', value='rdsView', className="myTab")],
             id='tabs',
             value='home'),
    html.Div(id='page-content'),
    # Hidden table required due to Dash design flaw, ensures table module is loaded
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),
]
)


@app.callback(Output('page-content', 'children'),
              [Input('tabs', 'value')])
def display_page(value):
    if value == 'dataView':
        return data_view.layout
    elif value == 'propertyView':
        return property_view.layout
    elif value == 'modelView':
        return model_view.layout
    elif value == 'modelEditorView':
        return model_editor_view.layout
    elif value == 'sourcesView':
        return sources_view.layout
    elif value == 'dynamoView':
        return dynamo_view.layout
    elif value == 'rdsView':
        return rds_view.layout
    else:
        return 'Welcome to the home page'


application = app.server

if __name__ == '__main__':
    application = app
    application.run_server(debug=True)
