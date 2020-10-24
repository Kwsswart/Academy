import phonenumbers
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, IntegerField, BooleanField, SubmitField, SelectField, SelectMultipleField, TextAreaField
from wtforms_components import TimeField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import Academy, Lessons, Student, LengthOfClass, TypeOfClass, DaysDone, Step, StepMarks, Classes121, Class121, StepExpectedTracker, StepExpectedProgress, StepActualProgress, StepActualTracker



class CreateStudentForm(FlaskForm):
    
    name = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    comment = TextAreaField('Comment On Student')
    academy = SelectField('Academy', validators=[DataRequired()], choices=[
        (None , '--'),
        ('Alonso Martínez','Alonso Martínez'),
        ('Argüelles','Argüelles'),
        ('Ercilla','Ercilla'),
        ('Gómez Laguna','Gómez Laguna'),
        ('La Paz','La Paz'),
        ('Nuevos Ministerios','Nuevos Ministerios'),
        ('Online', 'Online'),
        ('Rambla Catalunya','Rambla Catalunya'),
        ('San Miguel','San Miguel')], default=None)
    lengthofclass = SelectField('Length of class', validators=[DataRequired()], choices=[
        (None , '--'),
        ('30 Minutes', '30 Minutes'),
        ('1 Hour', '1 Hour'),
        ('1,5 Hours', '1,5 Hours'),
        ('2 Hours', '2 Hours'),
        ('2,5 Hours', '2,5 Hours'),
        ('3 Hours', '3 Hours')], default=None)
    typeofclass = SelectField('Type Of Class', validators=[DataRequired()], choices=[
        (None , '--'),
        ('121-General English', '121-General English'),
        ('121-Exam Class', '121-Exam Class'),
        ('121-Business English', '121-Business English'),
        ('121-Children', '121-Children'),
        ('Group Exam', 'Group Exam Class'),
        ('Group Intensive', 'Group Intensive'),
        ('Group Children', 'Group Children'),
        ('Group General English', 'Group General English'),
        ('Group Business English', 'Group Business English'),
        ('In-Company-121', 'In-Company-121'),
        ('In-Company General English', 'In-Company General English'),
        ('In-Company Business English', 'In-Company Business English')], default=None)
    step = SelectField('Step', choices=[
        (None , '--'),
        ('1', 'Step 1'),
        ('2', 'Step 2'),
        ('3', 'Step 3'),
        ('4', 'Step 4'),
        ('5', 'Step 5'),
        ('6', 'Step 6'),
        ('7', 'Step 7'),
        ('8', 'Step 8'),
        ('9', 'Step 9'),
        ('10', 'Step 10'),
        ('11', 'Step 11'),
        ('12', 'Step 12'),
        ('13', 'Step 13'),
        ('14', 'Step 14'),
        ('15', 'Step 15'),
        ('16', 'Step 16')], default=None)
    exams = SelectField('Exam Level', choices=[
        (None , '--'),
        ('Cambridge E3', 'Cambridge E3'),
        ('Cambridge E4', 'Cambridge E4'),
        ('Cambridge E5', 'Cambridge E5'),
        ('Cambridge E6', 'Cambridge E6'),
        ('Cambridge E7', 'Cambridge E7'),
        ('Cambridge E8', 'Cambridge E8'),
        ('Cambridge E9', 'Cambridge E9'),
        ('Cambridge E10', 'Cambridge E10'),
        ('TFL B1', 'TFL B1'),
        ('TFL B2', 'TFL B2'),
        ('TFL C2', 'TFL C1'),
        ('TFL C2', 'TFL C2'),
        ('IELTS B1', 'IELTS B1'),
        ('IELTS B2', 'IELTS B2'),
        ('IELTS C1', 'IELTS C1'),
        ('IELTS C2', 'IELTS C2')], default=None)
    kids = SelectField('Children Level', choices=[
        (None , '--'),
        ('Red', 'Red'),
        ('Blue', 'Blue'),
        ('Yellow', 'Yellow'),
        ('Pink', 'Pink'),
        ('Orange', 'Orange'),
        ('Green', 'Green'),
        ('Violet', 'Violet'),
        ('Turquoise', 'Turquoise')], default=None)
    agerange = SelectField('Children Class Age Range', choices=[
        (None , '--'),
        ('3-4', '3-4'),
        ('5-6', '5-6'),
        ('6-7', '6-7'),
        ('7-8', '7-8'),
        ('9-10', '9-10'),
        ('11-12', '11-12')], default=None)
    lesson = SelectField('Class', validators=[DataRequired()], choices=[], validate_choice=False)
    submit = SubmitField('Add Student')


    def validate_name(self, name):

        lesson = Lessons.query.filter_by(id=self.lesson.data).first()
        academy = Academy.query.filter_by(name=self.academy.data).first()

        student = Student.query.filter_by(academy_id=academy.id).first()
        if student is not None:
            raise ValidationError('Student name is already in the system with this Academy.')

    def validate_phone2(self, phone):
        student = Student.query.filter_by(phone=phone.data).first()
        if student is not None:
            raise ValidationError('Use different phone number.')
    
    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')