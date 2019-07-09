import calendar

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_table.FormatTemplate as FormatTemplate
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
    df_subcat = (
        df.groupby(df.sub_category)
        .agg({"amount": "sum"})
        .sort_values("amount", ascending=False)
    )

    layout = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Graph(
                                id="expenses_chart",
                                figure={
                                    "data": [
                                        go.Bar(
                                            x=df_monthly.index, y=df_monthly.amount * -1
                                        )
                                    ],
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
                                        margin={"t": 10, "r": 10},
                                        dragmode="select",
                                        hovermode="closest",
                                        clickmode="event+select",
                                    ),
                                },
                            )
                        ],
                        className="col-sm",
                    ),
                    html.Div(
                        [
                            dcc.Graph(
                                id="categories_chart",
                                figure={
                                    "data": [
                                        go.Bar(
                                            x=df_cat.amount * -1,
                                            y=df_cat.index,
                                            orientation="h",
                                        )
                                    ],
                                    "layout": go.Layout(
                                        xaxis={"title": "Expenses $"},
                                        margin={"t": 10, "r": 10},
                                        dragmode="select",
                                        hovermode="closest",
                                        clickmode="event+select",
                                    ),
                                },
                            )
                        ],
                        className="col-sm",
                    ),
                ],
                className="row",
                style={"width": "95%"},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Graph(
                                id="sub_categories_chart",
                                figure={
                                    "data": [
                                        go.Bar(
                                            x=df_subcat.amount * -1,
                                            y=df_subcat.index,
                                            orientation="h",
                                        )
                                    ],
                                    "layout": go.Layout(
                                        xaxis={"title": "Expenses $"},
                                        margin={"t": 10, "r": 10},
                                        dragmode="select",
                                        hovermode="closest",
                                        clickmode="event+select",
                                    ),
                                },
                            )
                        ],
                        className="col-sm",
                    ),
                    html.Div(
                        [
                            dash_table.DataTable(
                                id="transaction_table",
                                data=df.sort_values("added_date").to_dict("rows"),
                                columns=[
                                    {
                                        "id": "id",
                                        "name": "Hash",
                                        "type": "text",
                                        "hidden": True,
                                    },
                                    {"id": "date", "name": "Date", "type": "text"},
                                    {
                                        "id": "narration",
                                        "name": "Narration",
                                        "type": "text",
                                    },
                                    {
                                        "id": "amount",
                                        "name": "Amount",
                                        "type": "numeric",
                                        "format": FormatTemplate.money(2),
                                    },
                                ],
                                style_cell={"padding": "5px"},
                                style_header={
                                    "backgroundColor": "white",
                                    "fontWeight": "bold",
                                },
                                page_size=10,
                            )
                        ],
                        className="col-sm",
                    ),
                ],
                className="row",
                style={"width": "95%"},
            ),
        ]
    )

    return layout
