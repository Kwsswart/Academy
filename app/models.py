from datetime import datetime
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

    user_access = db.relationship(
                        'User', secondary=user_permissions,
                        backref=db.backref('user_permissions', lazy='dynamic'),
                        lazy='dynamic')

    def __repr__(self):
        return '<Permission Group : {} '.format(self.group_name)

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
    phone = db.Column(db.String(20), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    position = db.Column(db.String(20), index=True)

    access_groups = db.relationship(
                        'PermissionGroups', secondary=user_permissions,
                        backref=db.backref('user_permissions', lazy='dynamic'),
                        lazy='dynamic')
    # relationships
    academy_id = db.Column(db.Integer, db.ForeignKey('academy.id'))
    lessons = db.relationship('Lessons', backref='teacher', lazy='dynamic')
    student = db.relationship('Student', backref='teacher', lazy='dynamic')

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



class Lessons(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    days = db.Column(db.String(128), index=True)
    time = db.Column(db.String(128), index=True)
    length = db.Column(db.String(128), index=True)
    form = db.Column(db.String(128), index=True)
    comment = db.Column(db.String())

    # relationship
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    student = db.relationship('Student', backref='lessons', lazy='dynamic')
    academy_id = db.Column(db.Integer, db.ForeignKey('academy.id'))

    def __repr__(self):
        return '<Lesson {}, {}, {}, {}, {}, {}>'.format(self.name, self.days, self.time, self.length, self.form, self.comment)



class Student(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True, unique=True)
    phone = db.Column(db.String(20), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    days_missed = db.Column(db.Integer)
    comment = db.Column(db.String())

    # relationship
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('lessons.id'))
    academy_id = db.Column(db.Integer, db.ForeignKey('academy.id'))

    def __repr__(self):
        return '<Student {}, {}, {}, {}, {}>'.format(self.name, self.phone, self.email, self.days_missed, self.comment)



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


