from . import bp
from flask import render_template
from flask_login import login_required
import dashapp


@bp.route("/app1")
@login_required
def app1_template():
    return render_template("app1.html", dash_url=dashapp.url_base)

