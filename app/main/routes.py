
from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, current_app
from flask_login import current_user, login_user, logout_user, login_required
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

    # todo: Display Announcments order by date and add to check for the ones with for_all as True
    user_announcements = Announcement.query.filter_by(academy_id=current_user.id).all()
    
    return render_template('index.html', title='Home')


@bp.route('/make_announcement', methods=['GET', 'POST'])
@group_required(['Master', 'Upper Management', 'Management'])
@login_required
def make_announcement():
    """ End-Point handling making announcements """
    # todo: implement the announcement feature : Check the academy of user to ensure they can announce for their academy

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
        
        announcement = Announcement(
            subject = form.subject.data,
            message = form.message.data,
            for_all = form.for_all.data,
            user_id = current_user.id,
            academy_id = current_user.academy_id
        )
        
        db.session.add(announcement)
        db.session.commit()
        flash('Announcement has been sent!')
        return redirect(url_for('main.index'))
        
    return render_template('make_announcement.html', title='Make Announcement', form=form)
