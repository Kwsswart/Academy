import os
import json
import math
from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, current_app, abort, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from wtforms.validators import ValidationError
from app import  db
from app.models import User, group_required, Academy, Lessons, Student, LengthOfClass, TypeOfClass, DaysDone, Step, StepMarks, Classes121, Class121, StepExpectedTracker, StepExpectedProgress, StepActualProgress, StepActualTracker, Studentonclass, Studentonclass2
from app.classes import bp
from app.classes.forms import CreateClassForm, AttendanceForm, StepProgressForm, InsertCustom
from app.classes.helpers import get_name


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
            
            if length_of_class.name == '2 Hours' or length_of_class.name == '2,5 Hours':
                if class_number.class_number != 1:
                    number = int(class_number.class_number) - 1
                    actual_class_number = StepExpectedProgress.query.filter_by(step_expected_id=expectedtracker.id).filter_by(class_number=number).first()
                    class_number = actual_class_number

            actualtracker = StepActualTracker(length_of_class=length_of_class.id, step_id=step.id)
            db.session.add(actualtracker)
            db.session.commit()

            name = get_name(name=None, days=form.daysdone.data, time=form.time.data, types=class_type, academy=academy.name)
            
            lesson = Lessons(
                name=name,
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
        
        elif class_type == 'Group Exam Class':
            print('hi')
            name = get_name(name=None, days=form.daysdone.data, time=form.time.data, types=class_type, academy=academy.name)
            print(name)
        return redirect(url_for('classes.classes', academy=academy.name))

    return render_template('class/create_class.html', title="Create Class", form=form)


@bp.route('/classes/<academy>', methods=['GET'])
@login_required
def classes(academy):
    
    if academy == 'all':
        page = request.args.get('page', 1, type=int)
        academy1 = Academy.query.all()
        groups = Lessons.query.outerjoin(LengthOfClass).outerjoin(Academy).group_by(Lessons.academy_id, Lessons.id).order_by(Lessons.academy_id.asc()).order_by(Lessons.step_id.asc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
        next_url = url_for('classes.classes', academy='all', page=groups.next_num) \
        if groups.has_next else None
        prev_url = url_for('classes.classes', academy='all', page=groups.prev_num) \
        if groups.has_prev else None

        step = Step.query.all()
        days = DaysDone.query.join(Lessons).all()
    else: 
        page = request.args.get('page', 1, type=int)

        academy1 = Academy.query.filter_by(name=academy).first()
        groups = Lessons.query.filter_by(academy_id=academy1.id).outerjoin(LengthOfClass).outerjoin(Academy).order_by(Lessons.step_id.asc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
        next_url = url_for('classes.classes', academy=academy1.name, page=groups.next_num) \
        if groups.has_next else None
        prev_url = url_for('classes.classes', academy=academy1.name, page=groups.prev_num) \
        if groups.has_prev else None
        
        days = DaysDone.query.join(Lessons).all()
        step = Step.query.all()        
    
    return render_template('class/classes.html', title="View Classes", academy=academy1, groups=groups.items, days=days, step=step, next_url=next_url, prev_url=prev_url)


@bp.route('/view_class/<name>/<academy>', methods=['GET', 'POST'])
@login_required
def view_class(name, academy):

    academy = Academy.query.filter_by(name=academy).first()
    lesson = Lessons.query.filter_by(name=name).filter_by(academy_id=academy.id).join(Step).join(LengthOfClass).join(TypeOfClass).first()
    users = User.query.all()
    students = Student.query.filter_by(class_id=lesson.id).order_by(Student.id.asc()).all()
    studentcount = Student.query.filter_by(class_id=lesson.id).count()
    students1 = None
    students2 = None

    if lesson.student_on_class:
        link_1 = Studentonclass.query.filter_by(id=lesson.student_on_class).first()
        students1 = Student.query.filter_by(student_on_class=link_1.id).order_by(Student.id.asc()).all()
        count = Student.query.filter_by(student_on_class=link_1.id).count()
        studentcount = studentcount + count
    if lesson.student_on_class2:
        link_2 = Studentonclass2.query.filter_by(id=lesson.student_on_class2).first()
        students2 = Student.query.filter_by(student_on_class2=link_2.id).order_by(Student.id.asc()).all()
        count = Student.query.filter_by(student_on_class2=link_2.id).count()
        studentcount = studentcount + count
    if students1 is not None:
        students = students + students1
    if students2 is not None:
        students = students + students2
   
    expected_progress = None
    actual_progress = None
    student_ids = [f'{s.id}'for s in students]
    current_last_page = None
    

    if lesson.TypeOfClass.name == 'Group General English':
     
        expected_tracker = StepExpectedTracker.query.filter_by(length_of_class=lesson.LengthOfClass.id).filter_by(step_id=lesson.step.id).first()
        expected_progress = StepExpectedProgress.query.filter_by(step_expected_id=expected_tracker.id).order_by(StepExpectedProgress.class_number.desc()).all()
        actual_tracker = StepActualTracker.query.filter_by(length_of_class=lesson.LengthOfClass.id).filter_by(step_id=lesson.step.id).first()
        actual_progress = StepActualProgress.query.filter_by(step_actual_id=actual_tracker.id).order_by(StepActualProgress.class_number.desc()).all()
        actual_progress_page = StepActualProgress.query.filter_by(step_actual_id=actual_tracker.id).order_by(StepActualProgress.class_number.desc()).first()
        if actual_progress_page != None:
            current_last_page = actual_progress_page.last_page
        
    forms = []
    for i in range(studentcount):
        forms.append(AttendanceForm())
    update_form = StepProgressForm()

    if update_form.validate_on_submit():

        if lesson.TypeOfClass.name == 'Group General English':
            
            
            for i in expected_progress:
                if i.class_number == lesson.class_number:
                    expected_progress = i
            if expected_progress.class_number % 2 == 0 and lesson.LengthOfClass.name == '2 Hours' or lesson.LengthOfClass.name == '2,5 Hours':
                if int(update_form.lesson_number.data) < expected_progress.lesson_number - 1:
                    flash('Lesson number cannot be that low?')
                    return redirect(url_for('classes.view_class', name=lesson.name, academy=academy.name))
     
            if actual_tracker == None:
                actual_tracker = StepActualTracker(length_of_class=lesson.length_of_class, step_id=lesson.step_id)
                db.session.add(actual_tracker)
                db.session.commit()

            new = StepActualProgress(
                class_number=lesson.class_number, 
                lesson_number=update_form.lesson_number.data, 
                last_page=update_form.last_page.data,
                last_word=update_form.last_word.data,
                exercises=update_form.exercises.data,
                comment=update_form.comment.data,
                user_id=current_user.id,
                step_actual_id=actual_tracker.id)

            db.session.add(new)
            db.session.commit()

            # last page limits message dos or automatically push 1 lesson back or forward? ask cindy?
            if expected_progress.class_number % 2 == 0 and lesson.LengthOfClass.name == '2 Hours' or expected_progress.class_number % 2 == 0 and lesson.LengthOfClass.name == '2,5 Hours':
                lp_upper = expected_progress.last_page + 15
                lp_lower = expected_progress.last_page - 15
                if new.last_page >= lp_upper:
                    # message dos
                    message = "The last page for class is more than or equal to 15 pages more than expected"
                elif new.last_page <= lp_lower:
                    # message dos
                    message = " The last page for class is more than or equal to 15 pages less than expected"

                #if push back or forward:

                previous_expected = StepExpectedProgress.query.filter_by(step_expected_id=expected_tracker.id).filter_by(class_number=expected_progress.class_number - 2).first()
                next_expected = StepExpectedProgress.query.filter_by(step_expected_id=expected_tracker.id).filter_by(class_number=expected_progress.class_number + 2).first()
                if previous_expected is not None:
                    if int(update_form.last_page.data) >= int(previous_expected.last_page) - 10:
                        # set expected progress here
                        # lesson.class_number = previous_expected.class_number
                        example = 'example'

            if lesson.LengthOfClass.name == '1 Hour' or lesson.LengthOfClass.name == '1,5 Hours':
                lp_upper = expected_progress.last_page + 15
                lp_lower = expected_progress.last_page - 15
                if new.last_page >= lp_upper:
                    # message dos
                    message = "The last page for class is more than or equal to 15 pages more than expected"
                elif new.last_page <= lp_lower:
                    # message dos
                    message = " The last page for class is more than or equal to 15 pages less than expected"

                #if push back or forward:f
                previous_expected = StepExpectedProgress.query.filter_by(step_expected_id=expected_tracker.id).filter_by(class_number=expected_progress.class_number - 1).first()
                next_expected = StepExpectedProgress.query.filter_by(step_expected_id=expected_tracker.id).filter_by(class_number=expected_progress.class_number + 1).first()
                if previous_expected is not None:
                    if int(update_form.last_page.data) >= int(previous_expected.last_page) - 10:
                        # set expected progress here
                        # lesson.class_number = previous_expected.class_number
                        example = 'example'


        lesson.class_number = lesson.class_number + 1
        db.session.commit()
        flash('Progress updated')
        return redirect(url_for('classes.view_class', name=lesson.name, academy=academy.name))

    return render_template(
        'class/view_class.html', 
        title="View Class",
        lesson=lesson, 
        users= users,
        academy=academy, 
        expected=expected_progress, 
        actual_progress=actual_progress,
        studentcount=studentcount,
        update_form=update_form,
        students=students,
        forms=forms,
        current_last_page=current_last_page,
        # Adding for js functionality
        step= json.dumps(lesson.step.name),
        st=student_ids)


@bp.route('/attendance/<name>/<lesson>', methods=['POST'])
@login_required
def attendance(name, lesson):
    ''' Check the attendance for each student and up-to-date. '''

    student = Student.query.filter_by(id=name).first()
    lesson = Lessons.query.filter_by(id=lesson).join(TypeOfClass).first()

    form = AttendanceForm()

    if form.validate_on_submit():
        # use if lesson.TypeOfClass.name == 'Group General English': to separate marking 121s exam classes, kids or step
        stepmarks = StepMarks.query.filter_by(student_id=student.id).filter_by(lesson_id=lesson.id).order_by(StepMarks.datetime.desc()).first()
        current_datetime = datetime.utcnow()

        if form.attended.data == 'Yes':
            student.days_missed = 0
            
            if stepmarks == None:
                mark = StepMarks(
                    mark = form.score.data,
                    end_of_step_writing = form.writing.data,
                    end_of_step_speaking = form.speaking.data,
                    student_id= student.id,
                    user_id=current_user.id,
                    lesson_id=lesson.id
                )
                db.session.add(mark)
                db.session.commit()
                student.mark_average = mark.mark
                db.session.commit()

            elif stepmarks.datetime.day == current_datetime.day and stepmarks.datetime.month == current_datetime.month and stepmarks.datetime.year == current_datetime.year:
                print('Already been submitted')
                                
            else:
               
                mark = StepMarks(
                    mark = form.score.data,
                    end_of_step_writing = form.writing.data,
                    end_of_step_speaking = form.speaking.data,
                    student_id= student.id,
                    user_id=current_user.id,
                    lesson_id=lesson.id
                )
                db.session.add(mark)
                db.session.commit()
                marks = StepMarks.query.filter_by(student_id=student.id).filter_by(lesson_id=lesson.id).all()
                total = 0 
                count = 0
                for m in marks:
                    total = total + m.mark 
                    count = count + 1

                student.mark_average = round(total/count,1)
                db.session.commit()
                
            
        else:
            student.days_missed = student.days_missed + 1
            db.session.commit()

            if student.days_missed >= 3:
                # message the dos here
                print('Over the limit.')
            

        return jsonify(data={'message': 'recieved {}'.format(student.name)})
    
    return jsonify(data=form.errors)


@bp.route('/insert_custom/<class_id>', methods=['GET', 'POST'])
@group_required(['Master', 'Upper Management', 'Management'])
@login_required
def insert_custom(class_id):

    lesson = Lessons.query.filter_by(id=class_id).first()

    form = InsertCustom()
    
    if form.validate_on_submit():
        hi = "hi"

    return render_template('class/insert_custom.html', lesson=lesson, form=form)