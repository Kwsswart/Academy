
from flask import render_template, flash, redirect, request, url_for, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, UserRegistrationForm
from app.models import User , PermissionGroups, group_required, Academy


@bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        # redirect back to first viewed page if not logged in.
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register_user', methods=['GET','POST'])
@login_required
@group_required(['Master', 'Upper Management', 'Management'])
def register():
    
    form = UserRegistrationForm()

    if form.validate_on_submit():
        
        if dict(form.position.choices).get(form.position.data) == "Upper Management":
            if not current_user.is_master() and current_user.position != "Upper Management":
                print('True')
                flash("You don't have permissions to set Upper Management.")
                return redirect(url_for('auth.register'))

        academy = Academy.query.filter_by(name=dict(form.academy.choices).get(form.academy.data)).first()

        if not current_user.is_master() and current_user.position != "Upper Management":
            if current_user.academy_id != academy.id:
                flash('You can only add people to your own academy.')
                return redirect(url_for('auth.register'))

        user = User(
                username=form.username.data, 
                name=form.name.data, 
                phone=form.phone.data,
                email=form.email.data,
                position=form.position.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        user.academy_id = academy.id

        new_permission = PermissionGroups(group_name=dict(form.position.choices).get(form.position.data))
        db.session.add(new_permission)
        db.session.commit()

        permission = PermissionGroups.query.filter_by(group_name=new_permission.group_name).first()
        user.add_access(permission)
        db.session.commit()

        flash('Registration successful.')
        return redirect(url_for('main.index'))

    return render_template('auth/user_register.html', title="Register Staff", form=form)