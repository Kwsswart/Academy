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
    """ Display error template for 404 calls """
    
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(413)
def too_large(error):
    """ Display error template for 413 calls """

    return render_template('errors/413.html'), 413


@bp.app_errorhandler(500)
def internal_error(error):
    """ 
    Ensure any failed database sessions do not interfere with database access 
    ...
    Issues session rollback to reset the session to a clear state.
    """
    
    db.session.rollback()
    return render_template('errors/500.html'), 500