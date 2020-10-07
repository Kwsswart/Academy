
from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from wtforms.validators import ValidationError
from app import  db
from app.models import User , PermissionGroups, group_required, Academy, TrainedIn
from app.main import bp


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    
    return render_template('index.html', title='home')

