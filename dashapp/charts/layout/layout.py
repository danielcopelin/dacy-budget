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
    df_grouped = df.groupby(df.date.dt.month).agg({"amount": "sum"})

    layout = html.Div(
        children=[
            dcc.Graph(
                id="expenses_chart",
                figure={
                    "data": [go.Bar(x=df_grouped.index, y=df_grouped.amount * -1)],
                    "layout": go.Layout(
                        xaxis={
                            "title": "Month",
                            "tickmode": "array",
                            "tickvals": df_grouped.index,
                            "ticktext": df_grouped.index.to_series().apply(
                                lambda x: calendar.month_name[x]
                            ),
                        },
                        yaxis={"title": "Expenses $"},
                        margin={"t": 10},
                        hovermode="closest",
                        barmode="stack",
                    ),
                },
            )
        ]
    )

    return layout
