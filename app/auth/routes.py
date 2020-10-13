from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, UserRegistrationForm
from app.email import send_email, send_confirmation_email
from app.models import User , PermissionGroups, group_required, Academy, TrainedIn


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
                flash("You don't have permissions to set Upper Management.")
                return redirect(url_for('auth.register'))

        academy = Academy.query.filter_by(name=dict(form.academy.choices).get(form.academy.data)).first()

        if not current_user.is_master() and current_user.position != "Upper Management":
            if current_user.academy_id != academy.id:
                flash('You can only add people to your own academy.')
                return redirect(url_for('auth.register'))

        send_confirmation_email(form.email.data)
        flash('Please check given email to confirm the email address.', 'success')    

        user = User(
                username=form.username.data, 
                name=form.name.data, 
                phone=form.phone.data,
                email=form.email.data,
                position=form.position.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        trained = form.trained.data

        for t in trained:
            i = TrainedIn(name=t, teacher=user.id)
            db.session.add(i)
            db.session.commit()

        user.academy_id = academy.id

        new_permission = PermissionGroups(group_name=dict(form.position.choices).get(form.position.data))
        db.session.add(new_permission)
        db.session.commit()

        permission = PermissionGroups.query.filter_by(group_name=new_permission.group_name).first()
        user.add_access(permission)
        db.session.commit()

        flash('Registration successful.')
        return redirect(url_for('staff.user', name= user.name))

    return render_template('auth/user_register.html', title="Register Staff", form=form)


@bp.route('/confirm/<token>')
def confirm_email(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = confirm_serializer.loads(token, salt='email-confirmation-salt', max_age=3600)
    except:
        flash('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('auth.login'))
 
    user = User.query.filter_by(email=email).first()
    academy = Academy.query.filter_by(id=user.academy_id).first()
 
    if user.email_confirmed:
        flash('Account already confirmed. Please login.', 'info')
    else:
        user.email_confirmed = True
        user.email_confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        
        send_email('[Number 16] Your Access information',
                sender=current_app.config['ADMINS'][0], 
                recipients=[user.email],
                text_body=render_template('email/information.txt', 
                                            user=user.name, 
                                            username=user.username, 
                                            position=user.position,
                                            phone=user.phone,
                                            email=user.email,
                                            academy=academy.name),
                html_body=render_template('email/information.html',
                                            user=user.name, 
                                            username=user.username, 
                                            position=user.position,
                                            phone=user.phone,
                                            email=user.email,
                                            academy=academy.name))
        flash('Thank you for confirming the email address!')
 
    return redirect(url_for('main.index'))