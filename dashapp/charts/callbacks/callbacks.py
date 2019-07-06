from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_table
from flask_login import current_user
import pandas as pd
from collections import OrderedDict
from sqlalchemy.exc import IntegrityError
import dashapp.charts.layout


def register_callbacks(app):
    from app import db
    from app.models import Transaction

