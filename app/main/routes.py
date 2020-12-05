
from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, current_app
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import or_
from werkzeug.urls import url_parse
from wtforms.validators import ValidationError
from app import  db
from app.models import User , PermissionGroups, group_required, Academy, TrainedIn, Announcement
from app.main import bp
from app.main.forms import AnnouncementForm


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    """ End-Point handling displaying announcements directed at all academies or the individuals academy """

    page = request.args.get('page', 1, type=int)
    user_announcements = Announcement.query.filter(or_(Announcement.user_id==current_user.id, Announcement.academy_id==current_user.academy_id, Announcement.for_all==True)).order_by(Announcement.datetime.desc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('main.index', page=user_announcements.next_num) \
        if user_announcements.has_next else None
    prev_url = url_for('classes.classes', page=user_announcements.prev_num) \
        if user_announcements.has_prev else None
    return render_template('index.html', title='Home', announcements=user_announcements.items, next_url=next_url, prev_url=prev_url)


@bp.route('/make_announcement', methods=['GET', 'POST'])
@group_required(['Master', 'Upper Management', 'Management'])
@login_required
def make_announcement():
    """ End-Point handling making announcements """
    
    form = AnnouncementForm()
    academy = Academy.query.filter_by(id=current_user.academy_id).first()

    if form.validate_on_submit():
        if not current_user.is_master() and current_user.position != "Upper Management":
            if dict(form.academy.choices).get(form.academy.data) != academy.name:
                flash("You don't have permissions to make announcements to academies other than your own.")
                return redirect(url_for('main.make_announcement'))
            if form.for_all.data == True:
                flash("You don't have permissions to make announcements to academies other than your own.")
                return redirect(url_for('main.make_announcement'))
        academy = Academy.query.filter_by(name=dict(form.academy.choices).get(form.academy.data)).first()
        announcement = Announcement(
            subject = form.subject.data,
            message = form.message.data,
            for_all = form.for_all.data,
            user_id = current_user.id,
            academy_id = academy.id
        )
        
        db.session.add(announcement)
        db.session.commit()
        flash('Announcement has been sent!')
        return redirect(url_for('main.index'))
        
    return render_template('make_announcement.html', title='Make Announcement', what='Make', form=form)


@bp.route('/edit_announcement/<announcement_id>', methods=['GET', 'POST'])
@group_required(['Master', 'Upper Management', 'Management'])
@login_required
def edit_announcement(announcement_id):
    """ End-Point to Handle Editing Announcements """
    
    form = AnnouncementForm()
    announcement = Announcement.query.filter_by(id=announcement_id).first()
    academy = Academy.query.filter_by(id=current_user.academy_id).first()

    if form.validate_on_submit():
        if not current_user.is_master() and current_user.position != "Upper Management":
            if dict(form.academy.choices).get(form.academy.data) != academy.name:
                flash("You don't have permissions to make announcements to academies other than your own.")
                return redirect(url_for('main.make_announcement'))
            if form.for_all.data == True:
                flash("You don't have permissions to make announcements to academies other than your own.")
                return redirect(url_for('main.make_announcement'))
        
        announcement.subject = form.subject.data,
        announcement.message = form.message.data,
        announcement.for_all = form.for_all.data,
        db.session.commit()
        flash('Announcement has been editted!')
        return redirect(url_for('main.index'))
    else:
        form.subject.data = announcement.subject
        form.message.data = announcement.message
        form.for_all.data = announcement.for_all

    return render_template('make_announcement.html', title='Edit Announcement', what= 'Edit', form=form)


@bp.route('/remove_announcement/<announcement_id>', methods=['GET', 'POST'])
@group_required(['Master', 'Upper Management', 'Management'])
@login_required
def remove_announcement(announcement_id):
    """ End-Point to Handle Removing Announcements """
    
    announcement = Announcement.query.filter_by(id=announcement_id).first()
    db.session.delete(announcement)
    db.session.commit()
    flash('Announcement Removed!')
    return redirect(url_for('main.index'))