from . import bp
from flask import render_template
from flask_login import login_required
from dashapp import dash_transactions, dash_charts


@bp.route("/transactions")
@login_required
def transactions_template():
    return render_template("transactions.html", dash_url=dash_transactions.url_base)


@bp.route("/charts")
@login_required
def charts_template():
    return render_template("charts.html", dash_url=dash_charts.url_base)
