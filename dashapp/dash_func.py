from datetime import datetime, timedelta
from flask_login import current_user, login_required
import dash_html_components as html
import pandas as pd
import uuid
import os
import pickle


def apply_layout_with_auth(app, layout):
    def serve_layout():
        return layout

    # app.config.supress_callback_exceptions = True
    app.layout = serve_layout


def _protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.url_base_pathname):
            dashapp.server.view_functions[view_func] = login_required(
                dashapp.server.view_functions[view_func]
            )
