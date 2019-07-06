import calendar

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go


def layout(app):
    from app import db
    from app.models import Transaction

    with app.server.app_context():
        transactions = db.session.query(Transaction)
        df = pd.read_sql(transactions.statement, transactions.session.bind)

    df = df[(df.amount < 0) & (df.category != "Credit Card")]
    df_monthly = df.groupby(df.date.dt.month).agg({"amount": "sum"})
    df_cat = (
        df.groupby(df.category)
        .agg({"amount": "sum"})
        .sort_values("amount", ascending=False)
    )

    layout = html.Div(
        children=[
            dcc.Graph(
                id="expenses_chart",
                figure={
                    "data": [go.Bar(x=df_monthly.index, y=df_monthly.amount * -1)],
                    "layout": go.Layout(
                        xaxis={
                            "title": "Month",
                            "tickmode": "array",
                            "tickvals": df_monthly.index,
                            "ticktext": df_monthly.index.to_series().apply(
                                lambda x: calendar.month_name[x]
                            ),
                        },
                        yaxis={"title": "Expenses $"},
                        margin={"t": 10},
                        hovermode="closest",
                        barmode="stack",
                        clickmode="event+select",
                    ),
                },
            ),
            html.Div(id="selection"),
            dcc.Graph(
                id="categories_chart",
                figure={
                    "data": [
                        go.Bar(x=df_cat.amount * -1, y=df_cat.index, orientation="h")
                    ],
                    "layout": go.Layout(
                        xaxis={"title": "Expenses $"},
                        margin={"t": 10},
                        hovermode="closest",
                    ),
                },
            ),
        ]
    )

    return layout
