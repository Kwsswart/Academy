from datetime import datetime
from hashlib import md5
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import natural_keys
from app import db, login

class UnauthorisedAccessError(Exception):
    """ User does not have access priviledges """


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


user_permissions = db.Table('user_permissions',
                            db.Column('user_id',
                                    db.Integer,
                                    db.ForeignKey('user.id',
                                                ondelete='CASCADE'),
                                    index=True),
                            db.Column('permission_id',
                                    db.Integer,
                                    db.ForeignKey('permission_groups.id',
                                                ondelete='CASCADE'),
                                    index=True)
                            )


class PermissionGroups(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(40))

    def __repr__(self):
        return '<Permission Group : {} >'.format(self.group_name)

    @staticmethod
    def get_all_groups():
        groups = PermissionGroups.query.all()
        groups.sort(key=lambda x: x.group_name)
        return groups


# Teachers
class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(255), index=True, unique=True)
    phone = db.Column(db.String(20), index=True)
    email = db.Column(db.String(120), index=True)
    position = db.Column(db.String(20), index=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    email_confirmation_sent_on = db.Column(db.DateTime, nullable=True)
    email_confirmed = db.Column(db.Boolean, nullable=True, default=False)
    email_confirmed_on = db.Column(db.DateTime, nullable=True)

    academy_id = db.Column(db.Integer, db.ForeignKey('academy.id'))

    trained_in = db.relationship('TrainedIn', backref='TrainedIn', lazy='dynamic')

    access_groups = db.relationship(
                        'PermissionGroups', secondary=user_permissions,
                        backref=db.backref('user_permissions', lazy='dynamic'),
                        lazy='dynamic')

    lessons = db.relationship('Lessons', backref='teacher', lazy='dynamic')
    student = db.relationship('Student', backref='teacher', lazy='dynamic')
    class121 = db.relationship('Class121', backref='teacher', lazy='dynamic')
    step_actual = db.relationship('StepActualProgress', backref='teacher', lazy='dynamic')

    def __repr__(self):
        return '<User {}, {}, {}, {}, {} >'.format(self.username, self.name, self.phone, self.email, self.position)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_access(self, access_group):
        """ Add new access group priviledge to user """

        if not self.has_auth_access(access_group):
            self.access_groups.append(access_group)

    def remove_access(self, access_group):
        """ Remove access group priviledge from user """

        if self.has_auth_access(access_group):
            self.access_groups.remove(access_group)

    def has_auth_access(self, access_group):
        """ Check if user is a member of one of the required access groups """
        
        return self.access_groups.filter(
                                user_permissions.c.permission_id == access_group.id
                                ).count() > 0

    def is_master(self):
        """ Check for master """ 

        master_access = (PermissionGroups.query
                                .filter_by(group_name="Master")
                                .first())
        if self.has_auth_access(master_access):
            return True
        else:
            return False
   
    def has_academy_access(self, acad_id):
        """ Check whether user has authorisation to make edits in this academy """ 

        master_access = (PermissionGroups.query
                                        .filter_by(group_name="Master")
                                        .first())
        if self.has_auth_access(master_access):
            return True
        
        academy = Academy.query.filter_by(name=acad_id).first()
        if academy.id == self.academy_id:
            return True
        else:
            return False

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
        
    @staticmethod
    def get_user_permissions():
        permissions = User.query.all()
        permissions.sort(key=lambda x: natural_keys(x.username))
        return permissions


class Academy(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)

    teacher = db.relationship('User', backref='academy', lazy='dynamic')
    lessons = db.relationship('Lessons', backref='academy', lazy='dynamic')
    student = db.relationship('Student', backref='academy', lazy='dynamic')

    def __repr__(self):
        return '<Academy {}>'.format(self.name)

    def get_all_academies(self):
        academies = Academy.query.all()
        return academies


class TrainedIn(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))

    teacher = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Trained In : {} >'.format(self.name)

    @staticmethod
    def get_all_groups():
        groups = TrainedIn.query.all()
        groups.sort(key=lambda x: x.name)
        return groups


def check_user_group(required_groups):

    """
    Traverse list of required access groups to check for one or more matches
    """
    if current_user.is_anonymous:
        raise UnauthorisedAccessError

    # check for master
    master_group = (PermissionGroups.query 
                                    .filter_by(group_name='Master')
                                    .first())
    if master_group in current_user.access_groups:
        return True
    access = [current_user.has_auth_access(PermissionGroups.query.filter_by(
                                                            group_name=group).first())
            for group in required_groups]
    if not any(access):
        raise UnauthorisedAccessError


def group_required(*groups):

    """
    Decorate a function to require the user to have atleast one of the groups
    """
    
    def decorator(func):
        @wraps(func)
        def check_auth(*args, **kwargs):
            check_user_group(*groups)

            return func (*args, **kwargs)
        
        return check_auth

    return decorator


class Lessons(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    time = db.Column(db.String(128), index=True)
    comment = db.Column(db.String(500))
    amount_of_students = db.Column(db.Integer)
    class_number = db.Column(db.Integer)

    # relationship
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    length_of_class = db.Column(db.Integer, db.ForeignKey('length_of_class.id'))
    academy_id = db.Column(db.Integer, db.ForeignKey('academy.id'))
    step_id = db.Column(db.Integer, db.ForeignKey('step.id'))
    type_of_class = db.Column(db.Integer, db.ForeignKey('type_of_class.id'))
    classes121_id = db.Column(db.Integer, db.ForeignKey('classes121.id'))
    student_on_class = db.Column(db.Integer, db.ForeignKey('studentonclass.id'))
    student_on_class2 = db.Column(db.Integer, db.ForeignKey('studentonclass2.id'))

    step_expected_id = db.Column(db.Integer, db.ForeignKey('step_expected_tracker.id'))
    step_actual_id = db.Column(db.Integer, db.ForeignKey('step_actual_tracker.id'))

    days_done = db.relationship('DaysDone', backref='DaysDone', lazy='dynamic')
    student = db.relationship('Student', backref='lessons', lazy='dynamic')

    

    def __repr__(self):
        return '<Lesson {}, {}, {}, {}>'.format(self.name, self.time, self.comment, self.amount_of_students)

# many to many relationships student to academy and class

class Studentonclass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student = db.relationship('Student', backref='Studentonclass', lazy='dynamic')
    lesson = db.relationship('Lessons', backref='Studentofclass', lazy='dynamic')

class Studentonclass2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student = db.relationship('Student', backref='Studentonclass2', lazy='dynamic')
    lesson = db.relationship('Lessons', backref='Studentofclass2', lazy='dynamic')

class Student(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True, unique=True)
    phone = db.Column(db.String(20), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    days_missed = db.Column(db.Integer)
    comment = db.Column(db.String(500))

    # relationship
    student_on_class = db.Column(db.Integer, db.ForeignKey('studentonclass.id'))
    student_on_class2 = db.Column(db.Integer, db.ForeignKey('studentonclass2.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('lessons.id'))
    academy_id = db.Column(db.Integer, db.ForeignKey('academy.id'))
    step_id = db.Column(db.Integer, db.ForeignKey('step.id'))

    step_marks = db.relationship('StepMarks', backref='student', lazy='dynamic')


    def __repr__(self):
        return '<Student {}, {}, {}, {}, {}>'.format(self.name, self.phone, self.email, self.days_missed, self.comment)


class LengthOfClass(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)

    lessons = db.relationship('Lessons', backref='LengthOfClass', lazy='dynamic')
    classes121 = db.relationship('Classes121', backref='LengthOfClass', lazy='dynamic')
    step_expected = db.relationship('StepExpectedTracker', backref='LengthOfClass', lazy='dynamic')
    step_actual = db.relationship('StepActualTracker', backref='LengthOfClass', lazy='dynamic')

    def __repr__(self):
        return '<Length {}>'.format(self.name)

    def get_all_academies(self):
        length = LengthOfClass.query.all()
        return length


class TypeOfClass(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    
    lessons = db.relationship('Lessons', backref='TypeOfClass', lazy='dynamic')

    def __repr__(self):
        return '<TypeOfClass {} >'.format(self.name)

    def get_all_types(self):
        types = TypeOfClass.query.all()
        return types

class DaysDone(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))

    lessons = db.Column(db.Integer, db.ForeignKey('lessons.id'))

    def __repr__(self):
        return '<Days Done : {} {}>'.format(self.name, self.lessons)

    @staticmethod
    def get_all_groups():
        groups = DaysDone.query.all()
        groups.sort(key=lambda x: x.name)
        return groups


class Step(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)

    lessons = db.relationship('Lessons', backref='step', lazy='dynamic')
    student = db.relationship('Student', backref='step', lazy='dynamic')
    step_expected = db.relationship('StepExpectedTracker', backref='step', lazy='dynamic')
    step_actual = db.relationship('StepActualTracker', backref='step', lazy='dynamic')

    def __repr__(self):
        return '<Step {}>'.format(self.name)

    def get_all_steps(self):
        steps = Step.query.all()
        return steps


class StepMarks(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    mark = db.Column(db.Integer)
    end_of_step_writing = db.Column(db.Integer)
    end_of_step_speaking = db.Column(db.Integer)
    comment = db.Column(db.String(500))

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    
    def __repr__(self):
        return '<Mark: {}, end_of_step_writing: {}, end_of_step_speaking: {} >'.format(self.mark, self.end_of_step_writing, self.end_of_step_speaking)


# connections to classes

class Classes121(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    TypeOfClass = db.Column(db.String(20))

    length_of_class = db.Column(db.Integer, db.ForeignKey('length_of_class.id'))

    class121 = db.relationship('Class121', backref='Classes121', lazy='dynamic')
    lesson = db.relationship('Lessons', backref='Classes121', lazy='dynamic')

    def __repr__(self):
        return '<Type: {}>'.format(self.TypeOfClass)


class StepExpectedTracker(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    length_of_class = db.Column(db.Integer, db.ForeignKey('length_of_class.id'))
    step_id = db.Column(db.Integer, db.ForeignKey('step.id'))

    step_expected_progress = db.relationship('StepExpectedProgress', backref='StepExpectedTracker', lazy='dynamic')
    lesson = db.relationship('Lessons', backref='StepExpectedTracker', lazy='dynamic')

    def __repr__(self):
        return '<Type: {}, {}>'.format(self.length_of_class, self.step_id)


class StepActualTracker(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    length_of_class = db.Column(db.Integer, db.ForeignKey('length_of_class.id'))
    step_id = db.Column(db.Integer, db.ForeignKey('step.id'))

    step_actual_progress = db.relationship('StepActualProgress', backref='StepActualTracker', lazy='dynamic')
    lesson = db.relationship('Lessons', backref='StepActualTracker', lazy='dynamic')
    

    def __repr__(self):
        return '<Type: {}, {}>'.format(self.length_of_class, self.step_id)

# class types
class Class121(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    what_was_done = db.Column(db.String(500))
    exercises_done = db.Column(db.String(100), index=True)
    comment = db.Column(db.String(500))
    datetime = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    classes121_id = db.Column(db.Integer, db.ForeignKey('classes121.id'))


    def __repr__(self):
        return '<Class: {}, {}, {}>'.format(self.what_was_done, self.exercises_done, self.comment)


class StepExpectedProgress(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    class_number = db.Column(db.Integer, index=True) # is it first second third etc
    lesson_number = db.Column(db.Integer, index=True) # book lesson number
    last_page = db.Column(db.Integer)
    last_word = db.Column(db.String(40))
    exercises = db.Column(db.String(100))

    step_expected_id = db.Column(db.Integer, db.ForeignKey('step_expected_tracker.id'))

    def __repr__(self):
        return '<Class: {}, {}, {}, {}, {}>'.format(self.class_number, self.lesson_number, self.last_page, self.last_word, self.exercises)


class StepActualProgress(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    class_number = db.Column(db.Integer, index=True) # is it first second third etc
    lesson_number = db.Column(db.Integer, index=True) # book lesson number
    last_page = db.Column(db.Integer)
    last_word = db.Column(db.String(40))
    exercises = db.Column(db.String(100))
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    comment = db.Column(db.String(500))

    step_actual_id = db.Column(db.Integer, db.ForeignKey('step_actual_tracker.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Class: {}, {}, {}, {}, {}, {}, {}>'.format(self.class_number, self.lesson_number, self.last_page, self.last_word, self.exercises, self.datetime, self.comment)
