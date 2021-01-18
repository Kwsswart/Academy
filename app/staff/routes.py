import os
from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, current_app, abort, send_from_directory, send_file
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from wtforms.validators import ValidationError
from app import  db
from app.utils import validate_image
from app.email import send_email, send_confirmation_email, send_user_email
from app.models import User , PermissionGroups, group_required, Academy, TrainedIn
from app.staff import bp
from app.staff.forms import EditProfileForm, RemoveUserForm, AvatarUploadForm, EmailForm


@bp.route('/user/<name>')
@login_required
def user(name):
    """ End-Point to view User/Staff Profile """

    user = User.query.filter_by(name=name).first_or_404()
    academy = Academy.query.filter_by(id=user.academy_id).first()
    trained = TrainedIn.query.filter_by(teacher=user.id).all()
    avatar = None
    files = os.listdir(current_app.config['UPLOAD_PATH'] + 'avatars')

    for f in files:
        file_ext = os.path.splitext(f)[1]
        if str(user.id) + file_ext == f:
            avatar = f
    
    return render_template('staff/user.html', title="Profile", academy=academy, avatar=avatar, trained=trained, user=user)


@bp.route('/edit_user/<name>', methods=['GET', 'POST']) 
@login_required
@group_required(['Master', 'Upper Management', 'Management'])
def edit_user(name):
    """ End-Point to handle changes to User/Staff data """

    user = User.query.filter_by(name=name).first()
    academy = Academy.query.filter_by(id=user.academy_id).first()
    trained = TrainedIn.query.filter_by(teacher=user.id).all()

    if user.position == "Upper Management" or user.is_master():
        if not current_user.is_master() and current_user.position != "Upper Management":
            flash("You don't have permissions to edit Upper Management.")
            return redirect(url_for('staff.user', name=name))
    
    form = EditProfileForm(obj=user.id)
    position = current_user.position
    position_edit = user.position

    if current_user.is_master():
        position = 'Master'

    if form.validate_on_submit():
        if dict(form.position.choices).get(form.position.data) == "Upper Management":
            if not current_user.is_master() and current_user.position != "Upper Management":
                flash("You don't have permissions to set Upper Management.")
                return redirect(url_for('staff.user', name=name))

        academy_new = Academy.query.filter_by(name=dict(form.academy.choices).get(form.academy.data)).first()

        if not current_user.is_master() and current_user.position != "Upper Management":
            if current_user.academy_id != academy_new.id:
                flash('You can only edit profiles from your own academy.')
                return redirect(url_for('staff.user', name=name))

        if user.name != form.name.data:
            user.name = form.name.data
            db.session.commit()
        if user.phone != form.phone.data:
            user.phone = form.phone.data
            db.session.commit()
        if user.email != form.email.data:
            user.email = form.email.data
            send_confirmation_email(form.email.data)
            flash('Please check given email to confirm the email address.', 'success')
            db.session.commit()
        if user.position != form.position.data:
            permission_old = PermissionGroups.query.filter_by(group_name=user.position).first()
            permission_new = PermissionGroups.query.filter_by(group_name=form.position.data).first()
            user.remove_access(permission_old)
            user.add_access(permission_new)
            user.position = form.position.data  
            db.session.commit()
        if academy.name != academy_new.name:
            user.academy_id = academy_new.id
            db.session.commit()

        trained_new = form.trained.data
        # Add
        for t in trained_new:
            u = TrainedIn.query.filter_by(teacher=user.id).filter_by(name=t).first()
            if u is None:
                i = TrainedIn(name=t, teacher=user.id)
                db.session.add(i)
                db.session.commit()
        # Remove
        for t in trained: 
            if t.name not in trained_new:
                db.session.delete(t)
                db.session.commit()

        flash('User information updated')
        return redirect(url_for('staff.user', name=user.name))
    elif not form.is_submitted():
        form.name.data = user.name
        form.phone.data = user.phone
        form.email.data = user.email
        form.position.data = user.position
        form.academy.data = academy.name
        form.trained.data = [t.name for t in trained] 
    return render_template('staff/edit_user.html', title='Edit User',user=user, form=form, position=position, position_edit=position_edit)


@bp.route('/remove_user/<name>', methods=['GET', 'POST']) 
@login_required
@group_required(['Master', 'Upper Management', 'Management'])
def remove_user(name):
    """ End-point to handle removing User/Staff data """

    user = User.query.filter_by(name=name).first()
    academy = Academy.query.filter_by(id=user.academy_id).first()
    trained = TrainedIn.query.filter_by(teacher=user.id).all()
    form = RemoveUserForm()
    avatar = None
    files = os.listdir(current_app.config['UPLOAD_PATH'] + 'avatars')

    for f in files:
        file_ext = os.path.splitext(f)[1]
        if str(user.id) + file_ext == f:
            avatar = f

    if user.id == current_user.id:
        flash("You can't delete youself!")
        return redirect(url_for('staff.user', name=name))

    if not current_user.is_master() and current_user.position != "Upper Management":
        if current_user.academy_id != academy.id:
            flash('You can only delete profiles from your own academy.')
            return redirect(url_for('staff.user', name=name))

        if user.position == "Upper Management":
            flash('Managers cannot remove Upper Management')
            return redirect(url_for('staff.user', name=name))

    if form.validate_on_submit():
        if dict(form.affirmation.choices).get(form.affirmation.data) == 'Yes':
            db.session.delete(user)
            for t in trained:
                db.session.delete(t)
            flash('{} deleted!'.format(user.name))
            if avatar is not None:
                os.remove(os.path.join(current_app.config['UPLOAD_PATH'] + 'avatars/' + avatar))
            db.session.commit()
            return redirect(url_for('main.index'))
        else:
            flash('{} not deleted!'.format(user.name))
            return redirect(url_for('staff.user', name=name))

    return render_template('staff/remove_user.html', title='Remove User', user=user, form=form)


@bp.route('/upload/<name>', methods=['GET','POST'])
@login_required
def upload_file(name):
    """ End-point to handle custom avatar uploads """

    user = User.query.filter_by(name=name).first()
    form = AvatarUploadForm()
    files = os.listdir(current_app.config['UPLOAD_PATH'] + 'avatars')

    if form.validate_on_submit():
        uploaded_file = form.file.data
        filename = secure_filename(uploaded_file.filename)
        if uploaded_file.filename != '':
            file_ext = os.path.splitext(filename)[1]
            uploaded_file.save(os.path.join(current_app.config['UPLOAD_PATH'] + 'avatars' , str(user.id) + file_ext))
            flash('Upload Successful')
        return redirect(url_for('staff.user', name=user.name))

    return render_template('staff/upload.html', title='Upload Avatar', form=form, user=user, files=files)


@bp.route('/uploads/<filename>')
def upload(filename):
    """ End-point to handle displaying custom uploaded images """

    return send_from_directory(os.path.join(current_app.config['UPLOAD_PATH'], 'avatars'),filename=filename)


@bp.route('/email/<name>', methods=['GET','POST'])
@login_required
def email_user(name):
    """ End-point to handle user to user emails """

    user = User.query.filter_by(name=name).first()
    form = EmailForm()
    # todo: refine email system
    if form.validate_on_submit():
        send_user_email(
            subject=form.subject.data, 
            recipients=[user.email],
            body=form.body.data,
            user=user)
        flash('E-mail has been sent!')
        return redirect(url_for('main.index'))
    return render_template('staff/email_user.html', title="Send Email", user=user, form=form)


@bp.route('/view_staff/<academy>', methods=['GET'])
@login_required
def view_staff(academy):
    """ End-point to handle viewing all the staff members depending on academy """
    
    if academy == 'all':
        page = request.args.get('page', 1, type=int)
        academy = Academy.query.all()
        users = User.query.order_by(User.academy_id.asc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
        next_url = url_for('staff.view_staff', academy='all', page=users.next_num) \
        if users.has_next else None
        prev_url = url_for('staff.view_staff', academy='all', page=users.prev_num) \
        if users.has_prev else None
    else: 
        page = request.args.get('page', 1, type=int)
        academy = Academy.query.filter_by(name=academy).first()
        users = User.query.filter_by(academy_id=academy.id).order_by(User.academy_id.asc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
        next_url = url_for('staff.view_staff', academy=academy.name, page=users.next_num) \
        if users.has_next else None
        prev_url = url_for('staff.view_staff', academy=academy.name, page=users.prev_num) \
        if users.has_prev else None

    return render_template('staff/view_staff.html', title="View Staff", academy=academy, users=users.items, next_url=next_url, prev_url=prev_url)