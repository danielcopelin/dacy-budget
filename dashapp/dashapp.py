from dash import Dash
from dash.dependencies import Input, State, Output
from .dash_func import apply_layout_with_auth, _protect_dashviews
import dash_core_components as dcc
import dash_html_components as html

url_base = "/dash/app1/"

layout = html.Div(
    [
        html.Div("This is dash app1"),
        html.Br(),
        dcc.Input(id="input_text"),
        html.Br(),
        html.Br(),
        html.Div(id="target"),
    ]
)


def add_dash(server):
    meta_viewport = {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1, shrink-to-fit=no",
    }
    external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
    app = Dash(
        server=server,
        url_base_pathname=url_base,
        meta_tags=[meta_viewport],
        external_stylesheets=external_stylesheets,
    )
    app.url_base_pathname = url_base
    apply_layout_with_auth(app, layout)
    _protect_dashviews(app)

    # @app.callback(Output("target", "children"), [Input("input_text", "value")])
    # def callback_fun(value):
    #     return "your input is {}".format(value)

    return app.server
