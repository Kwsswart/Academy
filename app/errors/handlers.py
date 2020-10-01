from flask import render_template, flash, redirect, url_for
from app import db
from app.errors import bp
from app.models import UnauthorisedAccessError


@bp.app_errorhandler(UnauthorisedAccessError)
def handle_login_error(e):
    """ Redirect to the login page when LoginError is raised.""" 
    flash("You do not have access rights.")
    return redirect(url_for('auth.login'))

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    # To make sure that any failed database sessions do not intefere with any database accesses triggered
    # by the template, we need a session rollback(reset the session to a clear state)
    db.session.rollback()
    return render_template('errors/500.html'), 500