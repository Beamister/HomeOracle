import dash_html_components as html
import dash_core_components as dcc
import dash_table_experiments as dt
from dash.dependencies import Input, Output, State
from server import *


layout = html.Div(children=[
    html.H1("Model Viewer"),
    html.Div(id='model_view_feedback_container'),
    dt.DataTable(id='model_table',
                 row_selectable=True,
                 rows=[{}],
                 editable=True,
                 filterable=True,
                 sortable=True,
                 selected_row_indices=[]
                 ),
    html.Br(),
    html.Div(id='retrain_and_delete_button_container',
             style={'display': 'flex', 'justify-content': 'space-around'},
             children=[
                html.Button("Delete",
                            id='delete_button'
                            ),
                html.Button("Retrain",
                            id='retrain_button'
                            )
             ]),
    dcc.Interval(id='timer',
                 interval=10*1000,
                 n_intervals=0
                 ),
    html.Div(id='delete_button_clicks',
             style={'display': 'none'}),
    html.Div(id='retrain_button_clicks',
             style={'display': 'none'})
])


@app.callback(Output('model_table', 'rows'),
              [Input('delete_button_clicks', 'children'),
               Input('retrain_button_clicks', 'children'),
               Input('timer', 'n_intervals')])
def update_model_table(delete_clicks, retrain_clicks, n_intervals):
    return model_manager.get_model_table()

@app.callback(Output('delete_button_clicks', 'children'),
              [Input('retrain_button', 'n_clicks')],
              [State('model_table', 'rows'),
               State('model_table', 'selected_row_indices')])
def retrain_models(n_clicks, rows, rows_selected):
    for row_index in rows_selected:
        model_manager.train_model(rows[row_index]['name'])
    return str(n_clicks)


@app.callback(Output('retrain_button_clicks', 'children'),
              [Input('retrain_button', 'n_clicks')],
              [State('model_table', 'rows'),
               State('model_table', 'selected_row_indices')])
def delete_models(n_clicks, rows, rows_selected):
    for row_index in rows_selected:
        model_manager.delete_model(rows[row_index]['name'])
    return str(n_clicks)