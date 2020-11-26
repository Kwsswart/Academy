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
from app.students.helpers import get_name


@bp.route('/add_student', methods=['GET', 'POST'])
@login_required
@group_required(['Master', 'Upper Management', 'Management', 'Admin'])
def add_student():
    """ Handle adding new students """

    form = CreateStudentForm()

    if form.validate_on_submit():
        academy = Academy.query.filter_by(name=form.academy.data).first()
        options_121 =['121-General English', '121-Exam Class', '121-Business English', '121-Children', 'In-Company-121']
        type_of_class = TypeOfClass.query.filter_by(name=form.typeofclass.data).first()

        if not current_user.is_master() and current_user.position != "Upper Management":
            if current_user.academy_id != academy.id: # todo: adjust to utilize method has_academy_access 
                flash('You can only add people to your own academy.')
                return redirect(url_for('students.add_student'))

        if form.lesson.data == None:
            flash('Ensure class is chosen!')
            return redirect(url_for('add_student'))

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
                step_id = step.id)
            db.session.add(student)
            lesson.amount_of_students = lesson.amount_of_students + 1
            db.session.commit()
            flash('Student Added')
            return redirect(url_for('students.student_profile', academy=academy.name, name=student.name))

        elif form.typeofclass.data in options_121:
            # todo: Implement the 121 classes
            lesson_name = get_name(name= form.name.data, academy=academy.id, types=form.typeofclass.data, companyname=form.companyname.data)
    return render_template('students/add_student.html', title="Add Students", form=form)


@bp.route('/get_classes', methods=['POST'])
def get_classes():
    """ End-point for the ajax call to get available classes """

    form = CreateStudentForm()
    
    if form.submit():
        academy = Academy.query.filter_by(name=form.academy.data).first()
        length_of = LengthOfClass.query.filter_by(name=form.lengthofclass.data).first()
        type_of_class = TypeOfClass.query.filter_by(name=form.typeofclass.data).first()
        step = Step.query.filter_by(name=form.step.data).first()
        choices = []

        if form.typeofclass.data == 'Group General English':
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


@bp.route('/get_classes_edit/<student>', methods=['POST'])
def get_classes_edit(student):
    """ End-point for the ajax call to get available classes in the edit """
    
    student = Student.query.filter_by(id=student).first()
    form = EditStudentForm(obj=student.id)
    
    if form.submit():
        academy = Academy.query.filter_by(name=form.academy.data).first()
        length_of = LengthOfClass.query.filter_by(name=form.lengthofclass.data).first()
        type_of_class = TypeOfClass.query.filter_by(name=form.typeofclass.data).first()
        step = Step.query.filter_by(name=form.step.data).first()
        choices = []

        if form.typeofclass.data == 'Group General English':
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
    """ End-point to view student profile """

    academy = Academy.query.filter_by(name=academy).first()
    student = Student.query.filter_by(name=name).join(Lessons).first()
    type_of_class = TypeOfClass.query.filter_by(id=student.lessons.type_of_class).first()
    editted_by = User.query.filter_by(id=student.user_id).first()
    step = None
    additional_lesson_1 = None
    additional_lesson_2 = None

    if type_of_class.name == 'Group General English':
        step = Step.query.filter_by(id=student.lessons.step_id).first()
    # todo: Implement handling for the extra classes
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
    # todo: Assess how this will work with multiple different classes of exam, step, 121, etc
    return render_template('students/student_profile.html', 
        title="Student Profile",
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
    """ End-point to view a list of students depending on academy """

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
    """ End-point to handle removing student data from the database """

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
@group_required(['Master', 'Upper Management', 'Management', 'Admin'])
def edit_student(name, academy):
    """ End-point to handle changes to student information """

    academy = Academy.query.filter_by(name=academy).first()
    student = Student.query.filter_by(name=name).filter_by(academy_id=academy.id).first()
    current_lesson = Lessons.query.filter_by(id=student.class_id).first()
    length_of_class = LengthOfClass.query.filter_by(id=current_lesson.length_of_class).first()
    type_of_class = TypeOfClass.query.filter_by(id=current_lesson.type_of_class).first()
    options_121 =['121-General English', '121-Exam Class', '121-Business English', '121-Children', 'In-Company-121']
    step = None

    if not current_user.is_master() and current_user.position != "Upper Management":
        if current_user.academy_id != academy.id:
            flash('You can only remove people from your own academy.')
            return redirect(url_for('students.student_profile', name=student.name, academy=academy.name))
    
    if type_of_class.name == 'Group General English':
        step = Step.query.filter_by(id=student.step_id).first()
        # todo: add conditionals for different class types

    form = EditStudentForm(obj=student.id)
    form2 = AdditionalClassForm(obj=student.id)
    form3 = AdditionalClassForm2(obj=student.id)

    # Fill current form details
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
            form2.step.data = step_additional.name
            # todo: add conditionals for different class types
        form2.lengthofclass.data = length_of.name
        form2.academy.data = acad.name
        form2.typeofclass.data = type_of.name
        form2.lesson_.choices = [(lesson.id, '{} Students: {}/8 {}'.format(lesson.name, lesson.amount_of_students, lesson.time))]
            
    if student.student_on_class2:
        link = Studentonclass.query.filter_by(id=student.student_on_class2).first()
        lesson = Lessons.query.filter_by(student_on_class2=link.id).first()
        acad = Academy.query.filter_by(id=lesson.academy_id).first()
        length_of = LengthOfClass.query.filter_by(id=lesson.length_of_class).first()
        type_of = TypeOfClass.query.filter_by(id=lesson.type_of_class).first()

        if type_of.name == 'Group General English':
            step_additional = Step.query.filter_by(id=lesson.step_id).first()
            form3.step.data = step_additional.name
            # todo: add conditionals for different class types
        form3.lengthofclass.data = length_of.name
        form3.academy.data = acad.name
        form3.typeofclass.data = type_of.name
        form3.lesson3.data = [(lesson.id, '{} Students: {}/8 {}'.format(lesson.name, lesson.amount_of_students, lesson.time))]
    
    if form.validate_on_submit():
        if form.typeofclass.data == 'Group General English':
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
            if academy.name != form.academy.data:
                new_academy = Academy.query.filter_by(name=form.academy.name).first()
                student.academy_id = new_academy.id
            if current_lesson.id != form.lesson.data:
                new_lesson = Lessons.query.filter_by(id=form.lesson.data).first()
                student.class_id = new_lesson.id
            if type_of_class.name != form.typeofclass.data:
                if form.typeofclass.data == 'Group General English':
                    student.step_id = new_lesson.step_id
                    # todo: add conditionals for different class types
            if step:
                if step.name != form.step.data:
                    step = Step.query.filter_by(name=form.step.data).first()
                    student.step_id = step.id
            student.user_id = current_user.id
            
        elif form.typeofclass.data in options_121:
            # todo: implement 121 classes here
            lesson_name = get_name(name=form.name.data, academy=academy.id, types=form.typeofclass.data, companyname=form.companyname.data)
        db.session.commit()
        flash('Student Editted')
        return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))        
    return render_template(
        'students/edit_student.html', 
        title="Edit Student", 
        form=form, 
        form2=form2, 
        form3=form3, 
        student=student, 
        student_id=student.id, 
        academy=academy)


@bp.route('/additional_form/<student>', methods=['POST'])
@login_required
@group_required(['Master', 'Upper Management', 'Management', 'Admin'])
def additional_form(student):
    """ End-point to handle adding/editting additional classes """

    form = AdditionalClassForm()
    options_121 =['121-General English', '121-Exam Class', '121-Business English', '121-Children', 'In-Company-121']
    
    if form.validate_on_submit():
        student = Student.query.filter_by(id=student).join(Step).first()
        academy = Academy.query.filter_by(id=student.academy_id).first()
        step = None
        original_lesson = Lessons.query.filter_by(id=student.class_id).join(TypeOfClass).first()
    
        if form.typeofclass.data == 'Group General English':
            step = student.step.name
            if form.lesson_.data == 'None':
                flash('You must have a lesson in order to add an additional lesson')
                return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))
            if step:
                if form.step.data != step:
                    if int(form.step.data) <= int(step) - 3 or int(form.step.data) >= int(step) + 3:
                        flash('You cannot place a student in such a different step to their level')
                        return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))

            acad = Academy.query.filter_by(name=form.academy.data).first()
            length_of = LengthOfClass.query.filter_by(name=form.lengthofclass.data).first()
            type_of = TypeOfClass.query.filter_by(name=form.typeofclass.data).first()
            additional_lesson = Lessons.query.filter_by(id=form.lesson_.data).first()

            if acad.name != 'Online' and acad.name != academy.name:
                flash('Student can only be part of two different academy classes if one academy is online!') 
                return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))

            if type_of.name == original_lesson.TypeOfClass.name and additional_lesson.id == original_lesson.id:
                flash('You cannot add them to a second class to the same class')
                return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))

            # changing additional classes
            if student.student_on_class:
                original_link = Studentonclass.query.filter_by(id=student.student_on_class).first()
                original_additional = Lessons.query.filter_by(student_on_class=original_link.id).first()
                original_additional.amount_of_students = original_additional.amount_of_students - 1
                if additional_lesson.student_on_class:
                    link = Studentonclass.query.filter_by(id=additional_lesson.student_on_class).first()
                    student.student_on_class = link.id
                    additional_lesson.amount_of_students = additional_lesson.amount_of_students + 1
                    db.session.commit()
                    flash('Additional Class Editted Successfully')
                    return redirect(url_for('students.edit_student', name=student.name, academy=academy.name)) 
                else:
                    link = Studentonclass()
                    db.session.add(link)
                    db.session.commit()
                    additional_lesson.student_on_class = link.id
                    student.student_on_class = link.id
                    additional_lesson.amount_of_students = additional_lesson.amount_of_students + 1
                    db.session.commit()
                    flash('Additional Class Editted Successfully')
                    return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))
            else: 
                if additional_lesson.student_on_class:
                    link = Studentonclass.query.filter_by(id=additional_lesson.student_on_class).first()
                    student.student_on_class = link.id
                    additional_lesson.amount_of_students = additional_lesson.amount_of_students + 1
                    db.session.commit()
                    flash('Additional Class Added Successfully')
                    return redirect(url_for('students.edit_student', name=student.name, academy=academy.name)) 
                else:
                    link = Studentonclass()
                    db.session.add(link)
                    db.session.commit()
                    additional_lesson.student_on_class = link.id
                    student.student_on_class = link.id
                    additional_lesson.amount_of_students = additional_lesson.amount_of_students + 1
                    db.session.commit()
                    flash('Additional Class Added Successfully')
                    return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))
        # todo: add conditionals for different class types
        elif form.typeofclass.data in options_121:
            # todo: implement 121 classes here
            lesson_name = get_name(name=form.name.data, academy=academy.id, types=form.typeofclass.data, companyname=form.companyname_.data)
        

@bp.route('/get_classes_add1', methods=['POST'])
def get_classes_add1():
    """ End-point for ajax call to get available classes """

    form = AdditionalClassForm()
    academy = Academy.query.filter_by(name=form.academy.data).first()
    length_of = LengthOfClass.query.filter_by(name=form.lengthofclass.data).first()
    type_of_class = TypeOfClass.query.filter_by(name=form.typeofclass.data).first()
    step = Step.query.filter_by(name=form.step.data).first()
    choices = []

    if form.typeofclass.data == 'Group General English':
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


@bp.route('/additional_form2/<student>', methods=['POST'])
@login_required
@group_required(['Master', 'Upper Management', 'Management', 'Admin'])
def additional_form2(student):
    """ End-point to handle adding/editting additional classes """

    form = AdditionalClassForm2()
    options_121 =['121-General English', '121-Exam Class', '121-Business English', '121-Children', 'In-Company-121']
       
    if form.validate_on_submit():
        student = Student.query.filter_by(id=student).join(Step).first()
        academy = Academy.query.filter_by(id=student.academy_id).first()
        step = None
        original_lesson = Lessons.query.filter_by(id=student.class_id).join(TypeOfClass).join(Step).first()
        original_additional = None

        if student.student_on_class:
            link = Studentonclass.query.filter_by(id=student.student_on_class).first()
            original_additional = Lessons.query.filter_by(student_on_class=link.id).join(TypeOfClass).join(Step).first()

        if form.typeofclass.data == 'Group General English':
            step = student.step.name
            if form.lesson3.data == 'None':
                flash('You must have a lesson in order to add second additional lesson.')
                return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))
            if form.lesson3.data == None:
                flash('You must have a lesson in order to add second additional lesson.')
                return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))

            acad = Academy.query.filter_by(name=form.academy.data).first()
            length_of = LengthOfClass.query.filter_by(name=form.lengthofclass.data).first()
            type_of = TypeOfClass.query.filter_by(name=form.typeofclass.data).first()
            additional_lesson = Lessons.query.filter_by(id=form.lesson3.data).first()

            if acad.name != 'Online' and acad.name != academy.name:
                flash('Student can only be part of two different academy classes if one academy is online!') 
                return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))
        
            if type_of.name == original_lesson.TypeOfClass.name and additional_lesson.id == original_lesson.id:
                flash('You cannot add them to a second class to the same class')
                return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))

            if type_of.name == original_additional.TypeOfClass.name and additional_lesson.id == original_additional.id:
                flash('You cannot add them to a second class to the same class')
                return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))

            if step:
                if form.step.data != None and form.step.data != int(step) or original_additional.step.name != None and form.step.data != original_additional.step.name:
                    if int(original_lesson.step.name) <= int(step) - 3 or int(original_lesson.step.name) >= int(step) + 3:
                        flash('Please Keep the step levels in all classes as close to eachother as possible.')
                        return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))
            # changing additional classes
            if student.student_on_class2:
                original_link = Studentonclass2.query.filter_by(id=student.student_on_class2).first()
                original_additional = Lessons.query.filter_by(student_on_class2=original_link.id).first()
                original_additional.amount_of_students = original_additional.amount_of_students - 1
                if additional_lesson.student_on_class2:
                    link = Studentonclass2.query.filter_by(id=additional_lesson.student_on_class2).first()
                    student.student_on_class2 = link.id
                    additional_lesson.amount_of_students = additional_lesson.amount_of_students + 1
                    db.session.commit()
                    flash('Additional Class Editted Successfully')
                    return redirect(url_for('students.edit_student', name=student.name, academy=academy.name)) 
                else:
                    link = Studentonclass2()
                    db.session.add(link)
                    db.session.commit()

                    additional_lesson.student_on_class2 = link.id
                    student.student_on_class2 = link.id
                    additional_lesson.amount_of_students = additional_lesson.amount_of_students + 1
                    db.session.commit()
                    flash('Additional Class Editted Successfully')
                    return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))
            else: 
                if additional_lesson.student_on_class2:
                    link = Studentonclass2.query.filter_by(id=additional_lesson.student_on_class2).first()
                    student.student_on_class2 = link.id
                    additional_lesson.amount_of_students = additional_lesson.amount_of_students + 1
                    db.session.commit()
                    flash('Additional Class Added Successfully')
                    return redirect(url_for('students.edit_student', name=student.name, academy=academy.name)) 
                else:
                    link = Studentonclass2()
                    db.session.add(link)
                    db.session.commit()

                    additional_lesson.student_on_class2 = link.id
                    student.student_on_class2 = link.id
                    additional_lesson.amount_of_students = additional_lesson.amount_of_students + 1
                    db.session.commit()
                    flash('Additional Class Added Successfully')
                    return redirect(url_for('students.edit_student', name=student.name, academy=academy.name))
        # todo: Add conditionals for different class types
        elif form.typeofclass.data in options_121:
            # todo: Implement 121 class.
            lesson_name = get_name(name=form.name.data, academy=academy.id, types=form.typeofclass.data, companyname=form.companyname3.data)
        


@bp.route('/get_classes_add2', methods=['POST'])
def get_classes_add2():
    """ End-point for ajax call to get available classes """

    form = AdditionalClassForm2()
    academy = Academy.query.filter_by(name=form.academy.data).first()
    length_of = LengthOfClass.query.filter_by(name=form.lengthofclass.data).first()
    type_of_class = TypeOfClass.query.filter_by(name=form.typeofclass.data).first()
    step = Step.query.filter_by(name=form.step.data).first()
    choices = []

    if form.typeofclass.data == 'Group General English':
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