import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from sqlalchemy.orm import sessionmaker
from dash.dependencies import Input, Output

from server import app, database_engine

session_maker = sessionmaker(bind=database_engine)
session = session_maker()
table_names = database_engine.table_names()
print('Tables:', table_names)

layout = html.Div(children=[
    dcc.Dropdown(id='table_select',
                 value='jobs',
                 options=[{'label': table_name, 'value': table_name} for table_name in table_names]
    ),
    dcc.Dropdown(id='page_select',
                 value=1,
                 options=[]
    ),
    dt.DataTable(
        id='table',
        row_selectable=True,
        rows=[{}],
        editable=False,
        filterable=True,
        sortable=True,
        selected_row_indices=[]
    )
])




@app.callback(Output('table', 'rows'),
              [Input('table_select', 'value'),
               Input('page_select', 'value')])
def update_table_rows(table_name):
    return [{}]

@app.callback(Output('page_select', 'options'),
              [Input('table_select', 'value')])
def update_page_select_options(table_name):
    return [{}]

# Ensures that when a new table is selected the page select is set to 1
@app.callback(Output('page_select', 'value'),
              [Input('table_select', 'value')])
def update_page_select_value(table_name):
    return 1
