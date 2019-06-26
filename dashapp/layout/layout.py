import dash_core_components as dcc
import dash_html_components as html
import dash_table

layout = html.Div([html.Div(id="main"), dash_table.DataTable(id="transaction_table")])
