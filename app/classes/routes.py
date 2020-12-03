import os
import json
import math
from datetime import datetime, date
from flask import render_template, flash, redirect, request, url_for, current_app, abort, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from wtforms.validators import ValidationError
from app import  db
from app.models import User, group_required, Academy, Lessons, Student, LengthOfClass, TypeOfClass, DaysDone, Step, StepMarks, Classes121, Class121, StepExpectedTracker, StepExpectedProgress, StepActualProgress, StepActualTracker, Studentonclass, Studentonclass2, CustomInsert
from app.classes import bp
from app.classes.forms import CreateClassForm, AttendanceForm, StepProgressForm, InsertCustom
from app.classes.helpers import get_name


@bp.route('/create_class', methods=['GET', 'POST'])
@group_required(['Master', 'Upper Management', 'Management'])
@login_required
def create_class():
    """ End-point to handle creating the classes """

    form = CreateClassForm()

    if form.validate_on_submit():
        academy = Academy.query.filter_by(name=dict(form.academy.choices).get(form.academy.data)).first()
        class_type = dict(form.typeofclass.choices).get(form.typeofclass.data)
        if not current_user.is_master() and current_user.position != "Upper Management":
            if current_user.academy_id != academy.id:
                flash('You can only add classes to your own academy.')
                return redirect(url_for('classes.create_class'))

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
            return redirect(url_for('classes.view_class', name=lesson.name, academy=academy.name))
        elif class_type == 'Group Exam Class':
            # todo: input class system
            name = get_name(name=None, days=form.daysdone.data, time=form.time.data, types=class_type, academy=academy.name)
            print(name)
            return redirect(url_for('classes.view_class', name=lesson.name, academy=academy.name))
    return render_template('class/create_class.html', title="Create Class", form=form)


@bp.route('/classes/<academy>', methods=['GET'])
@login_required
def classes(academy):
    """ End-point to handle displaying the classes """
    
    if academy == 'all':
        page = request.args.get('page', 1, type=int)
        academy1 = Academy.query.all()
        groups = Lessons.query.outerjoin(LengthOfClass).outerjoin(Academy).group_by(Lessons.academy_id, Lessons.id).order_by(Lessons.academy_id.asc()).order_by(Lessons.step_id.asc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
        step = Step.query.all()
        days = DaysDone.query.join(Lessons).all()
        next_url = url_for('classes.classes', academy='all', page=groups.next_num) \
        if groups.has_next else None
        prev_url = url_for('classes.classes', academy='all', page=groups.prev_num) \
        if groups.has_prev else None   
    else: 
        page = request.args.get('page', 1, type=int)
        academy1 = Academy.query.filter_by(name=academy).first()
        groups = Lessons.query.filter_by(academy_id=academy1.id).outerjoin(LengthOfClass).outerjoin(Academy).order_by(Lessons.step_id.asc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
        days = DaysDone.query.join(Lessons).all()
        step = Step.query.all() 
        next_url = url_for('classes.classes', academy=academy1.name, page=groups.next_num) \
        if groups.has_next else None
        prev_url = url_for('classes.classes', academy=academy1.name, page=groups.prev_num) \
        if groups.has_prev else None
    return render_template('class/classes.html', title="View Classes", academy=academy1, groups=groups.items, days=days, step=step, next_url=next_url, prev_url=prev_url)


@bp.route('/view_class/<name>/<academy>', methods=['GET', 'POST'])
@login_required
def view_class(name, academy):
    """ End-point to handle displaying the individual class information & updating the class progress. """

    academy = Academy.query.filter_by(name=academy).first()
    lesson = Lessons.query.filter_by(name=name).filter_by(academy_id=academy.id).join(Step).join(LengthOfClass).join(TypeOfClass).first()
    users = User.query.all()
    students = Student.query.filter_by(class_id=lesson.id).order_by(Student.id.asc()).all()
    studentcount = Student.query.filter_by(class_id=lesson.id).count()
    students1 = None
    students2 = None
    expected_progress = None
    actual_progress = None
    current_last_page = None
    custom_progress = CustomInsert.query.filter_by(lesson_id=lesson.id).join(User).order_by(CustomInsert.datetime.asc()).first()
    forms = []
    update_form = StepProgressForm()

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
   
    student_ids = [f'{s.id}'for s in students]
    for i in range(studentcount):
        forms.append(AttendanceForm())

    if lesson.TypeOfClass.name == 'Group General English':
        expected_tracker = StepExpectedTracker.query.filter_by(length_of_class=lesson.LengthOfClass.id) \
            .filter_by(step_id=lesson.step.id).first()
        expected_progress = StepExpectedProgress.query.filter_by(step_expected_id=expected_tracker.id) \
            .order_by(StepExpectedProgress.class_number.desc()).all()
        actual_tracker = StepActualTracker.query.filter_by(length_of_class=lesson.LengthOfClass.id) \
            .filter_by(step_id=lesson.step.id).first()
        actual_progress = StepActualProgress.query.filter_by(step_actual_id=actual_tracker.id) \
            .filter_by(lesson_id=lesson.id).order_by(StepActualProgress.class_number.desc()).all()
        actual_progress_page = StepActualProgress.query.filter_by(step_actual_id=actual_tracker.id) \
            .filter_by(lesson_id=lesson.id).order_by(StepActualProgress.class_number.desc()).first()
        if actual_progress_page != None:
            current_last_page = actual_progress_page.last_page
            if custom_progress != None:
                if custom_progress.datetime < actual_progress_page.datetime:
                    custom_progress = None
        
    if update_form.validate_on_submit():
        if lesson.TypeOfClass.name == 'Group General English':
            if actual_progress_page != None and actual_progress_page.datetime.date() == date.today():
                if lesson.LengthOfClass.name != '2 Hours' or lesson.LengthOfClass.name != '2,5 Hours':
                    flash('Progress has already been updated today if you need to edit the progress look into editing it.')
                    return redirect(url_for('classes.view_class', name=lesson.name, academy=academy.name))

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
                step_actual_id=actual_tracker.id,
                lesson_id=lesson.id)
            db.session.add(new)
            db.session.commit()

            non_validate = ['REVISION', 'GRAMMAR REVIEW', 'FINISH BOOK', 'EXAM PREP', 'END OF STEP EXAM', 'GO THROUGH EXAM', "SPEAKER'S CORNER"]

            # ASK CINDY: last page limits message dos or automatically push 1 lesson back or forward?
            if expected_progress.class_number % 2 == 0 and lesson.LengthOfClass.name == '2 Hours' or expected_progress.class_number % 2 == 0 and lesson.LengthOfClass.name == '2,5 Hours':
                # todo: Decide whether to only message managment and leave for them to do or to set back.
                if custom_progress != None and expected.last_page not in non_validate:
                    lp_upper = expected_progress.last_page + 15
                    lp_lower = expected_progress.last_page - 15
                    if new.last_page >= lp_upper:
                        # message dos
                        message = "The last page for class is more than or equal to 15 pages more than expected"
                    elif new.last_page <= lp_lower:
                        # message dos
                        message = " The last page for class is more than or equal to 15 pages less than expected"

                    # todo: Decide whether to push back or foward automatically
                    previous_expected = StepExpectedProgress.query.filter_by(step_expected_id=expected_tracker.id).filter_by(class_number=expected_progress.class_number - 2).first()
                    next_expected = StepExpectedProgress.query.filter_by(step_expected_id=expected_tracker.id).filter_by(class_number=expected_progress.class_number + 2).first()
                    if previous_expected is not None:
                        if int(update_form.last_page.data) >= int(previous_expected.last_page) - 10:
                            # set expected progress here
                            # lesson.class_number = previous_expected.class_number
                            example = 'example'

            if lesson.LengthOfClass.name == '1 Hour' or lesson.LengthOfClass.name == '1,5 Hours':
                # todo: Decide whether to only message managment and leave for them to do or to set back.
                # todo: make for grammar review exam, revision, custom so not to check page for them
                if custom_progress != None and expected.last_page not in non_validate:
                    lp_upper = int(expected_progress.last_page) + 15
                    lp_lower = int(expected_progress.last_page) - 15
                    if new.last_page >= lp_upper:
                        # message dos
                        message = "The last page for class is more than or equal to 15 pages more than expected"
                    elif new.last_page <= lp_lower:
                        # message dos
                        message = " The last page for class is more than or equal to 15 pages less than expected"

                    # todo: Decide whether to push back or foward automatically
                    previous_expected = StepExpectedProgress.query.filter_by(step_expected_id=expected_tracker.id).filter_by(class_number=expected_progress.class_number - 1).first()
                    next_expected = StepExpectedProgress.query.filter_by(step_expected_id=expected_tracker.id).filter_by(class_number=expected_progress.class_number + 1).first()
                    if previous_expected is not None:
                        if int(update_form.last_page.data) >= int(previous_expected.last_page) - 10:
                            # set expected progress here
                            # lesson.class_number = previous_expected.class_number
                            todo = 'todo'
                # todo: Notify if finished book or close to finishing book
        # todo: check if class_number changes with the custom progress and if yes change so that doesn't
        if custom_progress == None:
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
        custom_progress=custom_progress,
        step=json.dumps(lesson.step.name),
        st=student_ids)


@bp.route('/attendance/<name>/<lesson>', methods=['POST'])
@login_required
def attendance(name, lesson):
    """ End-point to handle up-date attendance for students on progress submission """

    student = Student.query.filter_by(id=name).first()
    lesson = Lessons.query.filter_by(id=lesson).join(TypeOfClass).first()
    form = AttendanceForm()

    if form.validate_on_submit():
        # todo: Separate between exams, kids, companies, 121s using (if lesson.TypeOfClass.name == 'Group General English')
        stepmarks = StepMarks.query.filter_by(student_id=student.id).filter_by(lesson_id=lesson.id).order_by(StepMarks.datetime.desc()).first()

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
            elif stepmarks.datetime.date() == date.today():
                # todo: re-evaluate the way comparing above
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
                # todo: check if student has recieved 3 for the consecutive three times to email dos
                db.session.commit() 
        else:
            student.days_missed = student.days_missed + 1
            db.session.commit()
            if student.days_missed >= 3:
                # todo: message the dos here
                print('Over the limit.')

        return jsonify(data={'message': 'recieved {}'.format(student.name)})
    return jsonify(data=form.errors)


@bp.route('/edit_submitted_progress/<progress_id>/<lesson_id>', methods=['GET', 'POST'])
@login_required
def edit_submitted_progress(progress_id, lesson_id):
    """ End-point to edit the previously submitted progress """

    progress = StepActualProgress.query.filter_by(id=progress_id).first()
    lesson = Lessons.query.filter_by(id=lesson_id).join(Academy).join(Step).first()
    form = StepProgressForm()

    if not current_user.is_master() and current_user.position != "Upper Management" or current_user.position != "Management":
        if progress.user_id != current_user.id:
            flash("You cannot edit somebody else's submitted progress")
            return redirect(url_for('classes.view_class', name=lesson.name, academy=lesson.academy.name))

    if form.validate_on_submit():
        progress.lesson_number = form.lesson_number.data
        progress.last_page = form.last_page.data 
        progress.last_word = form.last_word.data
        progress.exercises = form.exercises.data 
        progress.comment = form.comment.data
        progress.user_id = current_user.id

        db.session.commit()
        return redirect(url_for('classes.view_class', name=lesson.name, academy=lesson.academy.name))
        # run checks to see how far off the last page and number are just in case as in the original submissions
    else:
        form.lesson_number.data = progress.lesson_number
        form.last_page.data = progress.last_page
        form.last_word.data = progress.last_word
        form.exercises.data = progress.exercises
        form.comment.data = progress.comment

    return render_template('class/edit_submitted_progress.html', title="Edit Submitted Progress", form=form, lesson=lesson, progress=progress, step=lesson.step.name)


@bp.route('/insert_custom/<class_id>', methods=['GET', 'POST'])
@group_required(['Master', 'Upper Management', 'Management'])
@login_required
def insert_custom(class_id):
    """ End-point to insert custom progress """

    lesson = Lessons.query.filter_by(id=class_id).join(Academy).first()
    form = InsertCustom()
    
    if form.validate_on_submit():
        custom = CustomInsert(
            message=form.message.data,
            exercises=form.exercises.data,
            user_id=current_user.id,
            lesson_id=lesson.id
        )
        db.session.add(custom)
        db.session.commit()
        flash('Custom Progress Inserted.')
        return redirect(url_for('classes.view_class', name=lesson.name, academy=lesson.academy.name))

    return render_template('class/insert_custom.html', title="Insert Custom Progress", lesson=lesson, form=form)


@bp.route('/edit_custom/<custom_id>', methods=['POST'])
@group_required(['Master', 'Upper Management', 'Management'])
@login_required
def edit_custom(custom_id):
    """ End-point to edit previously created custom progress """

    custom = CustomInsert.query.filter_by(id=custom_id).first()
    lesson = Lessons.query.filter_by(id=custom.lesson_id).join(Academy).first()
    form = InsertCustom()
    
    if form.validate_on_submit():
        custom.message = form.message.data
        custom.exercises = form.exercises.data 
        custom.user_id = current_user.id 
        db.session.commit()
        flash('Custom Progress Editted.')
        return redirect(url_for('classes.view_class', name=lesson.name, academy=lesson.academy.name))
    else:
        form.message.data = custom.message
        form.exercises.data = custom.exercises

    return render_template('class/insert_custom.html', title="Edit Custom Progress", lesson=lesson, form=form)


@bp.route('/remove_custom/<custom_id>', methods=['GET', 'POST'])
@group_required(['Master', 'Upper Management', 'Management'])
@login_required
def remove_custom(custom_id):
    """ End-point to remove custom progress """

    custom = CustomInsert.query.filter_by(id=custom_id).first()
    lesson = Lessons.query.filter_by(id=custom.lesson_id).join(Academy).first()
    db.session.delete(custom)
    db.session.commit()
    flash('Custom Progress Removed.')

    return redirect(url_for('classes.view_class', name=lesson.name, academy=lesson.academy.name))


@bp.route('/move_class/<move>/<lesson>', methods=['GET'])
@group_required(['Master', 'Upper Management', 'Management'])
@login_required
def move_class(move, lesson):
    """ End-point to handle moving the class progress back or forward """

    lesson = Lessons.query.filter_by(id=lesson).join(Academy).first()
    # todo: double check this once done
    if move == "FORWARD":
        lesson.class_number = lesson.class_number + 1
        db.session.commit()
    elif move == "BACKWARDS":
        lesson.class_number = lesson.class_number - 1
        db.session.commit()

    return redirect(url_for('classes.view_class', name=lesson.name, academy=lesson.academy.name))
    

@bp.route('/no_show/<class_id>', methods=['GET'])
@login_required
def no_show(class_id):
    """ End-point to handle submission of no show lessons """
    # todo: check this
    lesson = Lessons.query.filter_by(id=class_id).join(Academy).join(LengthOfClass).join(Step).join(TypeOfClass).first()
    students = Student.query.filter_by(class_id=class_id).all()
    link_1 = None
    link_2 = None
    if lesson.student_on_class != None:
        link_1 = Student.query.filter_by(student_on_class=lesson.student_on_class).all()
    if lesson.student_on_class2 != None:
        link_2 = Student.query.filter_by(student_on_class2=lesson.student_on_class2).all()
    actual_tracker = StepActualTracker.query.filter_by(length_of_class=lesson.LengthOfClass.id) \
        .filter_by(step_id=lesson.step.id).first()
    previous_progress = StepActualProgress.query.filter_by(lesson_id=lesson.id) \
        .filter_by(step_actual_id=actual_tracker.id).filter_by(class_number=lesson.class_number - 1).first()
    expected_tracker = StepExpectedTracker.query.filter_by(length_of_class=lesson.LengthOfClass.id) \
        .filter_by(step_id=lesson.step.id).first()
    expected_progress = StepExpectedProgress.query.filter_by(step_expected_id=expected_tracker.id) \
        .order_by(StepExpectedProgress.class_number.desc()).all()
    actual_progress_page = StepActualProgress.query.filter_by(step_actual_id=actual_tracker.id) \
            .filter_by(lesson_id=lesson.id).order_by(StepActualProgress.class_number.desc()).first()
        
    if actual_progress_page != None and actual_progress_page.datetime.date() == date.today():
        flash('Progress has already been updated today if you need to edit the progress look into editing it.')
        return redirect(url_for('classes.view_class', name=lesson.name, academy=lesson.academy.name))

    for student in students:
        student.days_missed = student.days_missed + 1
        db.session.commit()
    if link_1 != None:
        for student in link_1:
            student.days_missed = student.days_missed + 1
            db.session.commit()
    if link_2 != None:
        for student in link_2:
            student.days_missed = student.days_missed + 1
            db.session.commit()
    if previous_progress != None:
        new = StepActualProgress(
            class_number=lesson.class_number, 
            lesson_number=previous_progress.lesson_number, 
            last_page=previous_progress.last_page,
            last_word="NO SHOW!",
            exercises="NO SHOW!",
            comment="NO SHOW!",
            user_id=current_user.id,
            step_actual_id=actual_tracker.id,
            lesson_id=lesson.id)
    else:
        for expected in expected_progress:
            if expected.class_number == lesson.class_number:
                expected_progress = expected
        new = StepActualProgress(
            class_number=lesson.class_number, 
            lesson_number=expected.lesson_number, 
            last_page=expected.last_page,
            last_word="NO SHOW!",
            exercises="NO SHOW!",
            comment="NO SHOW!",
            user_id=current_user.id,
            step_actual_id=actual_tracker.id,
            lesson_id=lesson.id)
    db.session.add(new)
    db.session.commit()
    flash('Submitted No Show')
    return redirect(url_for('classes.view_class', name=lesson.name, academy=lesson.academy.name))


@bp.route('/remove_class/<class_id>')
@group_required(['Master', 'Upper Management', 'Management'])
@login_required
def remove_class(class_id):
    """ End-point to handle removal of classes """

    lesson = Lessons.query.filter_by(id=class_id).first()
    academy = Academy.query.filter_by(id=lesson.academy_id).first()
    if lesson.has_students():
        flash('Please ensure students are either moved to another class or removed from system first.')
        return redirect(url_for('classes.view_class', name=lesson.name, academy=academy.name))
    
    # todo: implement removal email here, with lesson details last page and word just in case needing to redo to dos

    db.session.delete(lesson)
    db.session.commit()
    flash('Class Group has been removed from the system.')
    
    return redirect(url_for('classes.classes', academy=academy.name))