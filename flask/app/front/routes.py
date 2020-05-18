from flask import url_for, render_template, flash
from flask_login import current_user

from app.front import bp

@bp.route('/')
@bp.route('/index')
def index():
    return render_template("front/index.html")
