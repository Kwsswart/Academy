import os
from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, current_app, abort, json, jsonify, make_response, session
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from wtforms.validators import ValidationError
from app import  db
from app.models import User, group_required, Academy, Lessons, Student, LengthOfClass, TypeOfClass, DaysDone, Step, StepMarks, Classes121, Class121, StepExpectedTracker, StepExpectedProgress, StepActualProgress, StepActualTracker, Studentonclass, Studentonclass2
from app.students import bp
from app.students.forms import CreateStudentForm, RemoveStudentForm, EditStudentForm, AdditionalClassForm, AdditionalClassForm2



@bp.route('/add_student', methods=['GET', 'POST'])
@login_required
@group_required(['Master', 'Upper Management', 'Management', 'Admin'])
def add_student():

    form = CreateStudentForm()


    if form.validate_on_submit():
        
        academy = Academy.query.filter_by(name=form.academy.data).first()
        
        if not current_user.is_master() and current_user.position != "Upper Management":
            if current_user.academy_id != academy.id:
                flash('You can only add people to your own academy.')
                return redirect(url_for('students.add_student'))

        if form.lesson.data == None:
            flash('Ensure class is chosen!')
            return redirect(url_for('add_student'))

        options_121 =[
            '121-General English',
            '121-Exam Class',
            '121-Business English',
            '121-Children', 
            'In-Company-121']

        
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
            lesson.amount_of_students = lesson.amount_of_students + 1
            db.session.commit()
            
            flash('Student Added')
            return redirect(url_for('students.student_profile', academy=academy.name, name=student.name))
               
    return render_template('students/add_student.html', title="Add Students", form=form)

# AJAX
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


@bp.route('/student_profile/<academy>/<name>', methods=['GET','POST'])
@login_required
def student_profile(academy, name):

    academy = Academy.query.filter_by(name=academy).first()
    student = Student.query.filter_by(name=name).join(Lessons).first()
    type_of_class = TypeOfClass.query.filter_by(id=student.lessons.type_of_class).first()
    editted_by = User.query.filter_by(id=student.user_id).first()

    step = None
    additional_lesson_1 = None
    additional_lesson_2 = None
    if type_of_class.name == 'Group General English':
        step = Step.query.filter_by(id=student.lessons.step_id).first()
    # add the extra classes
    if student.student_on_class:
        link = Studentonclass.query.filter_by(id=student.student_on_class).first()
        lesson = Lessons.query.filter_by(student_on_class=link.id).join(TypeOfClass).join(Academy).first()
        if lesson.TypeOfClass.name == 'Group General English':
            
            additional_lesson_1 = Lessons.query.filter_by(student_on_class=link.id).join(TypeOfClass).join(Step).join(Academy).first()
        else:
            additional_lesson_1 = lesson
        
    if student.student_on_class2:
        link = Studentonclass2.query.filter_by(id=student.student_on_class2).first()
        lesson2 = Lessons.query.filter_by(student_on_class=link.id).join(TypeOfClass).join(Academy).first()
        if lesson2.TypeOfClass.name == 'Group General English':
            additional_lesson_2 = Lessons.query.filter_by(student_on_class=link.id).join(TypeOfClass).join(Step).join(Academy).first()
        else:
            additional_lesson_2 = lesson


    return render_template('students/student_profile.html', 
        student=student, 
        academy=academy, 
        type_of_class=type_of_class,
        editted_by=editted_by,
        step=step, 
        additional_lesson_1=additional_lesson_1,
        additional_lesson_2=additional_lesson_2)


@bp.route('/students/<academy>', methods=['GET'])
@login_required
def students(academy):

    if academy == 'all':
        page = request.args.get('page', 1, type=int)

        academy = Academy.query.all()
        step = Step.query.all()
        students = Student.query.outerjoin(Lessons).group_by(Student.class_id, Student.id).order_by(Student.step_id.asc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
        
        next_url = url_for('students.students', academy='all', page=students.next_num) \
            if students.has_next else None
        prev_url = url_for('students.students', academy='all', page=students.prev_num) \
            if students.has_prev else None
    else: 
        page = request.args.get('page', 1, type=int)

        academy = Academy.query.filter_by(name=academy).first()
        step = Step.query.all()
        students = Student.query.filter_by(academy_id=academy.id).join(Step).join(Lessons).group_by(Student.class_id).order_by(Student.step_id.asc()).paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
        
        next_url = url_for('students.students', academy=academy.name, page=students.next_num) \
            if students.has_next else None
        prev_url = url_for('students.students', academy=academy.name, page=students.prev_num) \
            if students.has_prev else None
                
    
    return render_template('students/view_students.html', title="View Students", academy=academy, students=students.items,  step=step, next_url=next_url, prev_url=prev_url)



@bp.route('/remove_student/<academy>/<name>', methods=['GET', 'POST'])
@login_required
@group_required(['Master', 'Upper Management', 'Management'])
def remove_student(name, academy):

    academy = Academy.query.filter_by(name=academy).first()
    student = Student.query.filter_by(name=name).filter_by(academy_id=academy.id).first()
    lesson = Lessons.query.filter_by(id=student.class_id).first()

    form = RemoveStudentForm()

    if not current_user.is_master() and current_user.position != "Upper Management":
        if current_user.academy_id != academy.id:
            flash('You can only remove people from your own academy.')
            return redirect(url_for('students.student_profile', name=student.name, academy=academy.name))

    if form.validate_on_submit():
        if dict(form.affirmation.choices).get(form.affirmation.data) == 'Yes':
            lesson.amount_of_students = lesson.amount_of_students - 1
            db.session.delete(student)
            flash('{} deleted!'.format(student.name))
            db.session.commit()
            return redirect(url_for('main.index'))
        else:
            flash('{} not deleted!'.format(student.name))
            return redirect(url_for('students.student_profile', name=name, academy= academy.name))


    return render_template('students/remove_student.html', title="Remove Student", form=form, student=student, academy=academy)


@bp.route('/edit_student/<academy>/<name>', methods=['GET','POST'])
@login_required
@group_required(['Master', 'Upper Management', 'Management'])
def edit_student(name, academy):

    academy = Academy.query.filter_by(name=academy).first()
    student = Student.query.filter_by(name=name).filter_by(academy_id=academy.id).first()
    current_lesson = Lessons.query.filter_by(id=student.class_id).first()
    length_of_class = LengthOfClass.query.filter_by(id=current_lesson.length_of_class).first()
    type_of_class = TypeOfClass.query.filter_by(id=current_lesson.type_of_class).first()

    options_121 =[
            '121-General English',
            '121-Exam Class',
            '121-Business English',
            '121-Children', 
            'In-Company-121']

    step = None
    if type_of_class.name == 'Group General English':
        step = Step.query.filter_by(id=student.step_id).first()


    form = EditStudentForm(obj=student.id)

    form2 = AdditionalClassForm(obj=student.id)
    form3 = AdditionalClassForm2(obj=student.id)

    if not current_user.is_master() and current_user.position != "Upper Management":
        if current_user.academy_id != academy.id:
            flash('You can only remove people from your own academy.')
            return redirect(url_for('students.student_profile', name=student.name, academy=academy.name))

    if form.submit1.data and form.validate():
        
        if form.lesson.data == 'None':
            flash('You must have a lesson value')
            return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))
        if form.lesson.data == None:
            flash('You must have a lesson value')
            return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))
        if student.name != form.name.data:
            student.name = form.name.data
        if student.phone != form.phone.data:
            student.phone = form.phone.data
        if student.email != form.email.data:
            student.email = form.email.data
        if student.comment != form.comment.data:
            student.comment = form.comment.data
        student.user_id = current_user.id
        if academy.name != form.academy.data:
            new_academy = Academy.query.filter_by(name=form.academy.name).first()
            student.academy_id = new_academy.id
        if current_lesson.id != form.lesson.data:
            new_lesson = Lessons.query.filter_by(id=form.lesson.data).first()
            student.class_id = new_lesson.id
        if type_of_class.name != form.typeofclass.data:
            if form.typeofclass.data == 'Group General English':
                student.step_id = new_lesson.step_id
        if step:
            if step.name != form.step.data:
                step = Step.query.filter_by(name=form.step.data).first()
                student.step_id = step.id
    
        if form2.academy_.data and form2.typeofclass_.data and form2.lengthofclass_.data and form2.lesson_.data:

            if form2.lesson_.data == 'None':
                flash('You must have a lesson in order to add an additional lesson')
                return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))
            if form2.lesson_.data == None:
                flash('You must have a lesson in order to add an additional lesson')
                return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))
            # handling additional classes
            acad = Academy.query.filter_by(name=form2.academy_.data).first()
            length_of = LengthOfClass.query.filter_by(name=form2.lengthofclass_.data).first()
            type_of = TypeOfClass.query.filter_by(name=form2.typeofclass_.data).first()
            additional_lesson = Lessons.query.filter_by(id=form2.lesson_.data).first()

            if acad.name != 'Online' and acad.name != academy.name:
                flash('Student can only be part of two different academy classes if one academy is online!') 
                return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))

            if type_of.name == type_of_class.name and additional_lesson.id == current_lesson.id:
                flash('You cannot add them to a second class to the same class')
                return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))

            if form2.step_.data != None and form2.step_.data != form.step.data:
                
                upper_limit = int(form2.step_.data) + 2 
                lower_limit = int(form2.step_.data) - 2
                if  int(form2.step_.data) < lower_limit or int(form2.step_.data) > upper_limit:
                    flash('Please Keep the step levels in all classes as close to eachother as possible.')
                    return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))

            if additional_lesson.student_on_class:
                link = Studentonclass.query.filter_by(id=additional_lesson.student_on_class).first()
                student.student_on_class = link.id
                additional_lesson.amount_of_students = additional_lesson.amount_of_students + 1
                db.session.commit()
            else:
                link = Studentonclass()
                db.session.add(link)
                db.session.commit()
                additional_lesson.student_on_class = link.id
                student.student_on_class = link.id
                additional_lesson.amount_of_students = additional_lesson.amount_of_students + 1
                db.session.commit()

        if form3.academy3.data and form3.typeofclass3.data and form3.lengthofclass3.data and form3.lesson3.data:

            if form3.lesson3.data == 'None':
                flash('You must have a lesson in order to add second additional lesson.')
                return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))
            if form3.lesson3.data == None:
                flash('You must have a lesson in order to add second additional lesson.')
                return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))

            acad = Academy.query.filter_by(name=form3.academy3.data).first()
            length_of = LengthOfClass.query.filter_by(name=form3.lengthofclass3.data).first()
            type_of = TypeOfClass.query.filter_by(name=form3.typeofclass3.data).first()
            additional_lesson = Lessons.query.filter_by(id=form3.lesson3.data).first()

            if acad.name != 'Online' and acad.name != academy.name:
                flash('Student can only be part of two different academy classes if one academy is online!') 
                return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))
            
            if type_of.name == type_of_class.name and additional_lesson.id == current_lesson.id:
                flash('You cannot add them to a second class to the same class')
                return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))
                 
            if type_of.name == form2.typeofclass_.name and additional_lesson.id == form2.lesson_.data:
                flash('You cannot add them to a second class to the same class')
                return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))

            if form3.step3.data != None and form3.step3.data != form.step.data:
                
                upper_limit = int(form3.step3.data)+ 2 
                lower_limit = int(form3.step3.data) - 2
                if  int(form2.step_.data) < lower_limit or int(form2.step_.data) > upper_limit:
                    flash('Please Keep the step levels in all classes as close to eachother as possible.')
                    return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))


            if additional_lesson.student_on_class2:
                link = Studentonclass2.query.filter_by(id=additional_lesson.student_on_class2).first()
                student.student_on_class2 = link.id
                additional_lesson.amount_of_students = additional_lesson.amount_of_students + 1
                db.session.commit()
            else:
                link = Studentonclass2()
                db.session.add(link)
                db.session.commit()
                additional_lesson.student_on_class2 = link.id
                student.student_on_class2 = link.id
                additional_lesson.amount_of_students = additional_lesson.amount_of_students + 1
                db.session.commit()


        db.session.commit()

        flash('Student Editted')
        
        return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))

    elif not form.is_submitted():

        form.name.data = student.name
        form.phone.data = student.phone
        form.email.data = student.email
        form.comment.data = student.comment
        form.lengthofclass.data = length_of_class.name
        form.academy.data = academy.name
        form.typeofclass.data = type_of_class.name
        if step:
            form.step.data = step.name
        form.lesson.choices = [(current_lesson.id, '{} Students: {}/8 {}'.format(current_lesson.name, current_lesson.amount_of_students, current_lesson.time))]

        if student.student_on_class:

            link = Studentonclass.query.filter_by(id=student.student_on_class).first()
            lesson = Lessons.query.filter_by(student_on_class=link.id).first()
            acad = Academy.query.filter_by(id=lesson.academy_id).first()
            length_of = LengthOfClass.query.filter_by(id=lesson.length_of_class).first()
            type_of = TypeOfClass.query.filter_by(id=lesson.type_of_class).first()

            if type_of.name == 'Group General English':
                step_additional = Step.query.filter_by(id=lesson.step_id).first()
                form2.step_.data = step_additional.name

            form2.lengthofclass_.data = length_of.name
            form2.academy_.data = acad.name
            form2.typeofclass_.data = type_of.name
            form2.lesson_.choices = [(lesson.id, '{} Students: {}/8 {}'.format(lesson.name, lesson.amount_of_students, lesson.time))]
            
        if student.student_on_class2:

            link = Studentonclass.query.filter_by(id=student.student_on_class2).first()
            lesson = Lessons.query.filter_by(student_on_class=link.id).first()
            acad = Academy.query.filter_by(id=lesson.academy_id).first()
            length_of = LengthOfClass.query.filter_by(id=lesson.length_of_class).first()
            type_of = TypeOfClass.query.filter_by(id=lesson.type_of_class).first()

            if type_of.name == 'Group General English':
                step_additional = Step.query.filter_by(id=lesson.step_id).first()
                form3.step3.data = step_additional.name

            form3.lengthofclass3.data = length_of.name
            form3.academy3.data = acad.name
            form3.typeofclass3.data = type_of.name
            form3.lesson3.choices = [(lesson.id, '{} Students: {}/8 {}'.format(lesson.name, lesson.amount_of_students, lesson.time))]
            

    return render_template('students/edit_student.html', title="Edit Student", form=form, form2=form2, form3=form3, student=student, academy=academy)