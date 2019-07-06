from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_table
from flask_login import current_user
import pandas as pd
from collections import OrderedDict
from sqlalchemy.exc import IntegrityError
import dashapp.transactions.layout


def register_callbacks(app):
    from app import db
    from app.models import Transaction

    def update_changed_data(old_data, data):
        old = pd.DataFrame.from_records(old_data)
        new = pd.DataFrame.from_records(data)

        ne_stacked = (old != new).stack()

        changed = new.stack()[ne_stacked]
        idx = changed.index.get_level_values(0)[0]
        column = changed.index.get_level_values(1)[0]
        id = old.loc[idx, "id"]
        value = changed[idx][column]
        try:
            transaction = Transaction.query.get(id)
            setattr(transaction, column, value)
            db.session.flush()
        except IntegrityError as e:
            print(e)
            db.session.rollback()
        else:
            db.session.commit()

    @app.callback(
        Output("transaction_table", "data"),
        [
            Input("transaction_table", "data_previous"),
            Input("account_selector", "value"),
            Input("uncategorised_selector", "value"),
        ],
        [State("transaction_table", "data")],
    )
    def update_database_and_generate_table(
        old_table_data, selected_account, uncategorised, table_data
    ):
        with app.server.app_context():
            if (old_table_data is not None) and (
                len(old_table_data) == len(table_data)
            ):
                update_changed_data(old_table_data, table_data)

        with app.server.app_context():
            if selected_account is None:
                transactions = db.session.query(Transaction)
            else:
                transactions = db.session.query(Transaction).filter(
                    Transaction.account == selected_account
                )

            df = pd.read_sql(transactions.statement, transactions.session.bind)

        if uncategorised == "uncategorised":
            df = df[pd.isnull(df.sub_category)]

        return df.sort_values("added_date").to_dict("rows")
