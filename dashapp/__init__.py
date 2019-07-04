from dash import Dash
from .dash_func import apply_layout_with_auth, _protect_dashviews
from dashapp.callbacks import register_callbacks
from dashapp.layout import layout


url_base = "/dash/app1/"


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
    register_callbacks(app)
    _protect_dashviews(app)

    return app.server
