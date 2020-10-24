import os
from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, current_app, abort, send_from_directory, send_file
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from wtforms.validators import ValidationError
from app import  db
from app.models import User, group_required, Academy, Lessons, Student, LengthOfClass, TypeOfClass, DaysDone, Step, StepMarks, Classes121, Class121, StepExpectedTracker, StepExpectedProgress, StepActualProgress, StepActualTracker
from app.classes import bp
from app.classes.forms import CreateClassForm, AttendanceForm, StepProgressForm


@bp.route('/create_class', methods=['GET', 'POST'])
@group_required(['Master', 'Upper Management', 'Management'])
@login_required
def create_class():

    form = CreateClassForm()

    if form.validate_on_submit():

        academy = Academy.query.filter_by(name=dict(form.academy.choices).get(form.academy.data)).first()

        if not current_user.is_master() and current_user.position != "Upper Management":
            if current_user.academy_id != academy.id:
                flash('You can only add classes to your own academy.')
                return redirect(url_for('classes.create_class'))

        class_type = dict(form.typeofclass.choices).get(form.typeofclass.data)

        # Adding General English Class
        if class_type == 'Group General English':

            if form.lengthofclass.data == '30 Minutes':
                flash('General English Group class cannot be 30 minutes long')
                return redirect(url_for('classes.create_class'))

            length_of_class = LengthOfClass.query.filter_by(name=dict(form.lengthofclass.choices).get(form.lengthofclass.data)).first()
            step = Step.query.filter_by(name=form.step.data).first()
            expectedtracker = StepExpectedTracker.query.filter_by(length_of_class=length_of_class.id).filter_by(step_id=step.id).first()
            type_of_class = TypeOfClass.query.filter_by(name=dict(form.typeofclass.choices).get(form.typeofclass.data)).first()
            class_number = StepExpectedProgress.query.filter_by(lesson_number=form.startat.data).filter_by(step_expected_id=expectedtracker.id).order_by(StepExpectedProgress.class_number.asc()).first()
            
            actualtracker = StepActualTracker(length_of_class=length_of_class.id, step_id=step.id)
            db.session.add(actualtracker)
            db.session.commit()

            lesson = Lessons(
                name=form.name.data,
                time=str(form.time.data),
                comment=form.comment.data,
                amount_of_students=0,
                class_number=class_number.class_number,
                user_id=current_user.id,
                length_of_class=length_of_class.id,
                academy_id=academy.id,
                step_id=step.id,
                type_of_class=type_of_class.id,
                step_expected_id=expectedtracker.id, 
                step_actual_id=actualtracker.id        
            )
            db.session.add(lesson)
            db.session.commit()

            days = form.daysdone.data

            for t in days:
                i = DaysDone(name=t, lessons=lesson.id)
                db.session.add(i)
                db.session.commit()

            flash('Class Added.')
            return redirect(url_for('classes.classes', academy=academy.name))

        return redirect(url_for('classes.classes', academy=academy.name))

    return render_template('class/create_class.html', form=form)


@bp.route('/classes/<academy>', methods=['GET'])
@login_required
def classes(academy):
    if academy == 'all':
        return 'todo'
    else: 
        academy = Academy.query.filter_by(name=academy).first()
    
        groups = Lessons.query.filter_by(academy_id=academy.id).join(Step).join(LengthOfClass).group_by(Lessons.step_id).order_by(Lessons.step_id.asc()).all()
        days = DaysDone.query.join(Lessons).all()
        
    
        return render_template('class/classes.html', academy=academy, groups=groups, days=days)


@bp.route('/view_class/<name>/<academy>', methods=['GET', 'POST'])
@login_required
def view_class(name, academy):
    print(academy)
    academy = Academy.query.filter_by(name=academy).first()
    lesson = Lessons.query.filter_by(name=name).filter_by(academy_id=academy.id).join(Step).join(LengthOfClass).first()
    
    expected_tracker = StepExpectedTracker.query.filter_by(length_of_class=lesson.LengthOfClass.id).filter_by(step_id=lesson.step.id).first()
    expected_progress = StepExpectedProgress.query.filter_by(step_expected_id=expected_tracker.id).order_by(StepExpectedProgress.class_number.desc()).all()

    actual_tracker = StepActualTracker.query.filter_by(length_of_class=lesson.LengthOfClass.id).filter_by(step_id=lesson.step.id).first()
    actual_progress = StepActualProgress.query.filter_by(step_actual_id=actual_tracker.id).order_by(StepActualProgress.class_number.desc()).all()


    attendance = AttendanceForm()

    update_form = StepProgressForm()

    student = [
        {
            'id': 1,
            'name': 'Kieron',
            'days_missed': 1
        }
    ]

    return render_template(
        'class/view_class.html', 
        lesson=lesson, 
        academy=academy, 
        expected=expected_progress, 
        actual_progress=actual_progress,
        attendance=attendance,
        update_form=update_form,
        student=student)