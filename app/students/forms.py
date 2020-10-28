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
    companyname = StringField('Company Name')
    submit = SubmitField('Add Student')


    def validate_name(self, name):

        lesson = Lessons.query.filter_by(id=self.lesson.data).first()
        academy = Academy.query.filter_by(name=self.academy.data).first()

        student = Student.query.filter_by(academy_id=academy.id).filter_by(name=name.data).first()
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

    def validate_company(self, companyname):
        ''' Check that the class name entered isn't in use at the academy. '''

        
        options_IC = [
            'In-Company-121'
        ]
        if self.typeofclass.data in options_IC and companyname.data == None:
            raise ValidationError('Please Fill in the company name')
            





class RemoveStudentForm(FlaskForm):
    affirmation = SelectField('Are you sure?', validators=[DataRequired()], choices=[
        ('Yes','Yes'),
        ('No','No')
    ])
    submit = SubmitField('Confirm')

class EditStudentForm(FlaskForm):
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
    companyname = StringField('Company Name')
    submit1 = SubmitField('Edit Student')

    def __init__(self, obj, *args, **kwargs):
        self.student = int(obj)
        super(EditStudentForm, self).__init__(*args, **kwargs)

    def validate_name(self, name):
        student = Student.query.filter_by(id=self.student).first()
        if name.data != student.name:
            academy = Academy.query.filter_by(id=student.academy_id).first()
            if self.academy.data == academy.name:
                student1 = Student.query.filter_by(name=name.data).filter_by(academy_id=academy.id).first()
            else:
                academy1 = Academy.query.filter_by(name=self.academy.data).first()
                student1 = Student.query.filter_by(name=name.data).filter_by(academy_id=academy1.id).first()
            if student1 is not None:
                raise ValidationError('Name already in use.')

    def validate_phone2(self, phone):
        student = Student.query.filter_by(id=self.student).first()
        if phone.data != student.phone:
            new = student.query.filter_by(phone=phone.data).first()
            if new is not None:
                raise ValidationError('Phone number already in use.')

    def validate_email(self, email):
        student = Student.query.filter_by(id=self.student).first()
        if email.data != student.email:
            new = Student.query.filter_by(email=email.data).first()
            if new is not None:
                raise ValidationError('Email already in use.')

    def validate_company(self, companyname):
        ''' Check that the class name entered isn't in use at the academy. '''
        
        options_IC = [
            'In-Company-121'
        ]
        if self.typeofclass.data in options_IC and companyname.data == None:
            raise ValidationError('Please Fill in the company name')


class AdditionalClassForm(FlaskForm):

    academy_ = SelectField('Academy', validators=[DataRequired()], choices=[
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
    lengthofclass_ = SelectField('Length of class', validators=[DataRequired()], choices=[
        (None , '--'),
        ('30 Minutes', '30 Minutes'),
        ('1 Hour', '1 Hour'),
        ('1,5 Hours', '1,5 Hours'),
        ('2 Hours', '2 Hours'),
        ('2,5 Hours', '2,5 Hours'),
        ('3 Hours', '3 Hours')], default=None)
    typeofclass_ = SelectField('Type Of Class', validators=[DataRequired()], choices=[
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
    step_ = SelectField('Step', choices=[
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
    exams_ = SelectField('Exam Level', choices=[
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
    kids_ = SelectField('Children Level', choices=[
        (None , '--'),
        ('Red', 'Red'),
        ('Blue', 'Blue'),
        ('Yellow', 'Yellow'),
        ('Pink', 'Pink'),
        ('Orange', 'Orange'),
        ('Green', 'Green'),
        ('Violet', 'Violet'),
        ('Turquoise', 'Turquoise')], default=None)
    agerange_ = SelectField('Children Class Age Range', choices=[
        (None , '--'),
        ('3-4', '3-4'),
        ('5-6', '5-6'),
        ('6-7', '6-7'),
        ('7-8', '7-8'),
        ('9-10', '9-10'),
        ('11-12', '11-12')], default=None)
    lesson_ = SelectField('Class', validators=[DataRequired()], choices=[], validate_choice=False)
    companyname_ = StringField('Company Name')
    
    def validate_company(self, companyname_):
        ''' Check that the class name entered isn't in use at the academy. '''

        
        options_IC = [
            'In-Company-121'
        ]
        if self.typeofclass_.data in options_IC and companyname_.data == None:
            raise ValidationError('Please Fill in the company name')
    

class AdditionalClassForm2(FlaskForm):

    academy3 = SelectField('Academy', validators=[DataRequired()], choices=[
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
    lengthofclass3 = SelectField('Length of class', validators=[DataRequired()], choices=[
        (None , '--'),
        ('30 Minutes', '30 Minutes'),
        ('1 Hour', '1 Hour'),
        ('1,5 Hours', '1,5 Hours'),
        ('2 Hours', '2 Hours'),
        ('2,5 Hours', '2,5 Hours'),
        ('3 Hours', '3 Hours')], default=None)
    typeofclass3 = SelectField('Type Of Class', validators=[DataRequired()], choices=[
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
    step3 = SelectField('Step', choices=[
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
    exams3 = SelectField('Exam Level', choices=[
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
    kids3 = SelectField('Children Level', choices=[
        (None , '--'),
        ('Red', 'Red'),
        ('Blue', 'Blue'),
        ('Yellow', 'Yellow'),
        ('Pink', 'Pink'),
        ('Orange', 'Orange'),
        ('Green', 'Green'),
        ('Violet', 'Violet'),
        ('Turquoise', 'Turquoise')], default=None)
    agerange3 = SelectField('Children Class Age Range', choices=[
        (None , '--'),
        ('3-4', '3-4'),
        ('5-6', '5-6'),
        ('6-7', '6-7'),
        ('7-8', '7-8'),
        ('9-10', '9-10'),
        ('11-12', '11-12')], default=None)
    lesson3 = SelectField('Class', validators=[DataRequired()], choices=[], validate_choice=False)
    companyname3 = StringField('Company Name')
    

    def validate_company(self, companyname3):
        ''' Check that the class name entered isn't in use at the academy. '''

        
        options_IC = [
            'In-Company-121'
        ]
        if self.typeofclass3.data in options_IC and companyname3.data == None:
            raise ValidationError('Please Fill in the company name')