import dash_bootstrap_components as dbc
from dash import Dash

from dashapp.charts.callbacks import register_callbacks
from dashapp.charts.layout import layout

from .dash_func import _protect_dashviews, apply_layout_with_auth

url_base = "/dash/charts/"


def add_dash(server):
    meta_viewport = {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1, shrink-to-fit=no",
    }
    external_stylesheets = [
        "https://codepen.io/chriddyp/pen/bWLwgP.css",
        dbc.themes.GRID,
    ]
    app = Dash(
        server=server,
        url_base_pathname=url_base,
        meta_tags=[meta_viewport],
        external_stylesheets=external_stylesheets,
    )
    app.url_base_pathname = url_base
    apply_layout_with_auth(app, layout(app))
    register_callbacks(app)
    _protect_dashviews(app)

    return app.server
