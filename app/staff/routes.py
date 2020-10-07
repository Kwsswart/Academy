import os
from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, current_app, abort, send_from_directory, send_file
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from wtforms.validators import ValidationError
from app import  db
from app.utils import validate_image
from app.models import User , PermissionGroups, group_required, Academy, TrainedIn
from app.staff import bp
from app.staff.forms import EditProfileForm, RemoveUserForm, AvatarUploadForm

@bp.route('/user/<name>')
@login_required
def user(name):

    user = User.query.filter_by(name=name).first_or_404()
    academy = Academy.query.filter_by(id=user.academy_id).first()
    trained = TrainedIn.query.filter_by(teacher=user.id).all()
    
    return render_template('staff/user.html', title="Profile", user=user, academy=academy, trained=trained)

@bp.route('/edit_user/<name>', methods=['GET', 'POST']) #make it click and save the name of use user here
@login_required
@group_required(['Master', 'Upper Management', 'Management'])
def edit_user(name):

    user = User.query.filter_by(name=name).first()
    academy = Academy.query.filter_by(id=user.academy_id).first()
    trained = TrainedIn.query.filter_by(teacher=user.id).all()
    
    form = EditProfileForm(obj=user.id)

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

        # Apply changes
        if user.name != form.name.data:
            user.name = form.name.data
            db.session.commit()

        if user.phone != form.phone.data:
            user.phone = form.phone.data
            db.session.commit()

        if user.email != form.email.data:
            user.email = form.email.data
            db.session.commit()

        if user.position != form.position.data and not user.is_master:
            permission_old = PermissionGroups.query.filter_by(group_name=user.position).first()
            permission_new = PermissionGroups(group_name=dict(form.position.choices).get(form.position.data))
            user.remove_access(permission_old)
            user.add_access(permission_new)
            user.position = form.position.data  
            db.session.commit()
            
        if academy.name != academy_new.name:
            user.academy_id = academy_new.id
            db.session.commit()

        trained_new = form.trained.data
        for t in trained_new:
            u = TrainedIn.query.filter_by(teacher=user.id).filter_by(name=t).first()
            if u is None:
                i = TrainedIn(name=t, teacher=user.id)
                db.session.add(i)
                db.session.commit()
        # remove training not clicked.
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
        
    return render_template('staff/edit_user.html', title='Edit User',user=user, form=form)


@bp.route('/remove_user/<name>', methods=['GET', 'POST']) 
@login_required
@group_required(['Master', 'Upper Management', 'Management'])
def remove_user(name):

    user = User.query.filter_by(name=name).first()
    academy = Academy.query.filter_by(id=user.academy_id).first()
    trained = TrainedIn.query.filter_by(teacher=user.id).all()

    form = RemoveUserForm()

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
            db.session.commit()
            return redirect(url_for('main.index'))
        else:
            flash('{} not deleted!'.format(user.name))
            return redirect(url_for('staff.user', name=name))

    return render_template('staff/remove_user.html', title='Remove User', user=user, form=form)



@bp.route('/upload/<name>', methods=['GET','POST'])
@login_required
def upload_file(name):

    user = User.query.filter_by(name=name).first()
    form = AvatarUploadForm()
    print(user.id)
    files = os.listdir(current_app.config['UPLOAD_PATH'] + 'avatars')

    if form.validate_on_submit():
        uploaded_file = form.file.data
        filename = secure_filename(uploaded_file.filename)
        if uploaded_file.filename != '':
            file_ext = os.path.splitext(filename)[1]
            uploaded_file.save(os.path.join(current_app.config['UPLOAD_PATH'] + 'avatars' , str(user.id) + file_ext))

        return redirect(url_for('staff.upload_file', name=user.name))

    return render_template('staff/upload.html', title='Upload Avatar', form=form, user=user, files=files)

@bp.route('/uploads/<filename>')
def upload(filename):
    print(os.path.join(current_app.config['UPLOAD_PATH'], 'avatars/') + filename)
    return send_from_directory(os.path.join(current_app.config['UPLOAD_PATH'], 'avatars'),filename=filename)


