from sqlalchemy import Table
from server import app, database_engine
from tables import Base, get_class_by_tablename, Session
from constants import *
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

table_names = database_engine.table_names()

layout = html.Div(children=[
    html.H1(children='RDS View', id='title'),
    html.Div(id='input_container',
             style={'display': 'flex'},
             children=[
                html.Div(id='table_select_container',
                         style={'width': '50%', 'display': 'flex'},
                         children=[
                            html.Div('Select Table:'),
                            dcc.Dropdown(id='table_select',
                                         value='jobs',
                                         style={'width': '30rem'},
                                         options=[{'label': table_name, 'value': table_name}
                                                  for table_name in table_names],
                                         clearable=False
                                         ),
                         ]
                         ),
                html.Div(id='page_select_container',
                         style={'width': '50%', 'display': 'flex', 'justify-content': 'flex-end'},
                         children=[
                            html.Div('Page:'),
                            dcc.Dropdown(id='page_select',
                                         style={'width': '10rem'},
                                         value=1,
                                         options=[],
                                         clearable=False
                                         )
                         ]
                         )
                ]
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
def update_table_rows(table_name, page_number):
    session = Session()
    Table('core_dataset', Base.metadata, autoload=True, autoload_with=database_engine,
          keep_existing=False, extend_existing=True)
    entries = session.query(Base.metadata.tables[table_name])\
                     .offset(RDS_VIEW_ROW_COUNT * (page_number - 1))\
                     .limit(RDS_VIEW_ROW_COUNT).all()
    column_names = Base.metadata.tables[table_name].columns.keys()
    rows = []
    if len(entries) > 0:
        for entry in entries:
            row = {}
            for column_name in column_names:
                row[column_name] = getattr(entry, column_name)
            rows.append(row)
    # If table is empty then show empty first row
    else:
        row = {}
        for column_name in column_names:
            row[column_name] = ''
        rows.append(row)
    session.close()
    return rows


@app.callback(Output('page_select', 'options'),
              [Input('table_select', 'value')])
def update_page_select_options(table_name):
    session = Session()
    class_type = get_class_by_tablename(table_name)
    row_count = session.query(class_type).count()
    session.close()
    page_count = (row_count // RDS_VIEW_ROW_COUNT) + 1
    options = [{'label': page_number, 'value': page_number} for page_number in range(1, page_count + 1)]
    return options


# Ensures that when a new table is selected the page select is set to 1
@app.callback(Output('page_select', 'value'),
              [Input('table_select', 'value')])
def update_page_select_value(table_name):
    return 1
