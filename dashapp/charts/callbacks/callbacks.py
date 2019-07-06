from collections import OrderedDict

import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

import dashapp.charts.layout


def register_callbacks(app):
    from app import db
    from app.models import Transaction

    with app.server.app_context():
        transactions = db.session.query(Transaction)
        df = pd.read_sql(transactions.statement, transactions.session.bind)
        df = df[(df.amount < 0) & (df.category != "Credit Card")]

    @app.callback(
        Output("categories_chart", "figure"), [Input("expenses_chart", "selectedData")]
    )
    def display_selection(selected_data):
        if selected_data is None:
            df_cat = (
                df.groupby(df.category)
                .agg({"amount": "sum"})
                .sort_values("amount", ascending=False)
            )
        else:
            months = [point["x"] for point in selected_data["points"]]
            df_cat = (
                df[df.date.dt.month.isin(months)]
                .groupby(df.category)
                .agg({"amount": "sum"})
                .sort_values("amount", ascending=False)
            )
        return {"data": [go.Bar(x=df_cat.amount * -1, y=df_cat.index, orientation="h")]}
