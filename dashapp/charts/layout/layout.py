import dash_core_components as dcc
import dash_html_components as html

# import dash_table
# import dash_table.FormatTemplate as FormatTemplate
import pandas as pd


def layout(app):
    from app import db
    from app.models import Transaction

    with app.server.app_context():
        transactions = db.session.query(Transaction)
        df = pd.read_sql(transactions.statement, transactions.session.bind)

        accounts = Transaction.query.with_entities(Transaction.account).distinct()

    layout = html.Div(["charts will go here"])

    return layout
