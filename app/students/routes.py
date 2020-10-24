import os
from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, current_app, abort, json, jsonify, make_response, session
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from wtforms.validators import ValidationError
from app import  db
from app.models import User, group_required, Academy, Lessons, Student, LengthOfClass, TypeOfClass, DaysDone, Step, StepMarks, Classes121, Class121, StepExpectedTracker, StepExpectedProgress, StepActualProgress, StepActualTracker
from app.students import bp
from app.students.forms import CreateStudentForm



@bp.route('/add_student', methods=['GET', 'POST'])
@login_required
@group_required(['Master', 'Upper Management', 'Management', 'Admin'])
def add_student():

    form = CreateStudentForm()


    if form.validate_on_submit():
        
        if form.lesson.data == None:
            flash('Ensure class is chosen!')
            return redirect(url_for('add_student'))

        academy = Academy.query.filter_by(name=form.academy.data).first()
        type_of_class = TypeOfClass.query.filter_by(name=form.typeofclass.data).first()

        if type_of_class.name == 'Group General English':

            lesson = Lessons.query.filter_by(id=form.lesson.data).first()
            step = Step.query.filter_by(name=form.step.data).first()

            student = Student(
                name = form.name.data,
                phone = form.phone.data,
                email = form.email.data,
                days_missed = 0,
                comment = form.comment.data,
                user_id = current_user.id,
                class_id = lesson.id,
                academy_id =academy.id,
                step_id = step.id
            )
            db.session.add(student)
            db.session.commit()
            flash('Student Added')
            return redirect(url_for('student_profile.html', name=student))
               
    return render_template('students/add_student.html', form=form)

@bp.route('/get_classes', methods=['POST'])
@login_required
def get_classes():
 
    academy = Academy.query.filter_by(name=request.form.get('academy')).first()
    length_of = LengthOfClass.query.filter_by(name=request.form.get('length_of_class')).first()
    type_of_class = TypeOfClass.query.filter_by(name=request.form.get('type_of_class')).first()
    step = Step.query.filter_by(name=request.form.get('step')).first()

    choices = []

    if request.form.get('type_of_class') == 'Group General English':

        lessons = Lessons.query.filter_by(academy_id=academy.id)\
            .filter_by(length_of_class=length_of.id)\
            .filter_by(type_of_class=type_of_class.id)\
            .filter_by(step_id=step.id).all()
        
        for i in lessons:
            if i.amount_of_students < 8:
                    
                choice_final = {
                    'lesson_id': i.id,
                    'lesson_name': i.name,
                    'amount_of_students': i.amount_of_students,
                    'lesson_time': i.time
                }
                choices.append(choice_final)
    
    return jsonify(choices)


@bp.route('/student_profile', methods=['GET','POST'])
@login_required
def student_profile():
    return render_template('students/student_profile.html')