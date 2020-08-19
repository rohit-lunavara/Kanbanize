from app.visualization import bp
from flask import render_template
from flask_login import login_required
from dashboard.dash import dash_url_base

@bp.route('/')
@login_required
def dashboard() :
    return render_template('visualization/dash.html', dash_url = dash_url_base)