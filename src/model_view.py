import dash_html_components as html
import dash_core_components as dcc
import dash_table_experiments as dt
from dash.dependencies import Input, Output, State
from server import *


layout = html.Div(children=[
    html.H1("Model Viewer"),
    dt.DataTable(id='tableView',
                 row_selectable=True,
                 rows=[{}],
                 editable=True,
                 filterable=True,
                 sortable=True,
                 selected_row_indices=[]
                 ),
    html.Button("Delete",
                id='delete_button'
                ),
    html.Button("Retrain",
                id='retrain_button'
                )
])
