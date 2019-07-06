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
    def displayed_categories_for_month(selected_months):
        if selected_months is None:
            df_cat = (
                df.groupby(df.category)
                .agg({"amount": "sum"})
                .sort_values("amount", ascending=False)
            )
        else:
            months = [point["x"] for point in selected_months["points"]]
            df_cat = (
                df[df.date.dt.month.isin(months)]
                .groupby(df.category)
                .agg({"amount": "sum"})
                .sort_values("amount", ascending=False)
            )

        return {"data": [go.Bar(x=df_cat.amount * -1, y=df_cat.index, orientation="h")]}

    @app.callback(
        Output("sub_categories_chart", "figure"),
        [
            Input("expenses_chart", "selectedData"),
            Input("categories_chart", "selectedData"),
        ],
    )
    def displayed_categories_for_month(selected_months, selected_categories):
        if selected_months is None and selected_categories is None:
            df_subcat = (
                df.groupby(df.sub_category)
                .agg({"amount": "sum"})
                .sort_values("amount", ascending=False)
            )
        elif selected_months is None:
            categories = [point["y"] for point in selected_categories["points"]]
            df_subcat = (
                df[df.category.isin(categories)]
                .groupby(df.sub_category)
                .agg({"amount": "sum"})
                .sort_values("amount", ascending=False)
            )
        elif selected_categories is None:
            months = [point["x"] for point in selected_months["points"]]
            df_subcat = (
                df[df.date.dt.month.isin(months)]
                .groupby(df.sub_category)
                .agg({"amount": "sum"})
                .sort_values("amount", ascending=False)
            )
        else:
            months = [point["x"] for point in selected_months["points"]]
            categories = [point["y"] for point in selected_categories["points"]]
            df_subcat = (
                df[df.category.isin(categories) & df.date.dt.month.isin(months)]
                .groupby(df.sub_category)
                .agg({"amount": "sum"})
                .sort_values("amount", ascending=False)
            )

        return {
            "data": [
                go.Bar(x=df_subcat.amount * -1, y=df_subcat.index, orientation="h")
            ]
        }

    @app.callback(
        Output("transaction_table", "data"),
        [
            Input("expenses_chart", "selectedData"),
            Input("categories_chart", "selectedData"),
        ],
    )
    def displayed_categories_for_month(selected_months, selected_categories):
        if selected_months is None and selected_categories is None:
            df_selected = df
        elif selected_months is None:
            categories = [point["y"] for point in selected_categories["points"]]
            df_selected = (
                df[df.category.isin(categories)]
                .groupby(df.sub_category)
                .agg({"amount": "sum"})
                .sort_values("amount", ascending=False)
            )
        elif selected_categories is None:
            months = [point["x"] for point in selected_months["points"]]
            df_selected = df[df.date.dt.month.isin(months)]
        else:
            months = [point["x"] for point in selected_months["points"]]
            categories = [point["y"] for point in selected_categories["points"]]
            df_selected = df[
                df.category.isin(categories) & df.date.dt.month.isin(months)
            ]

        return df_selected.sort_values("added_date").to_dict("rows")

