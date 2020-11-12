import phonenumbers
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, IntegerField, BooleanField, SubmitField, SelectField, SelectMultipleField, TextAreaField
from wtforms_components import TimeField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Optional
from app.models import Academy, Lessons, Student, LengthOfClass, TypeOfClass, DaysDone, Step, StepMarks, Classes121, Class121, StepExpectedTracker, StepExpectedProgress, StepActualProgress, StepActualTracker
from app.classes.helpers import OptionalIf



class CreateClassForm(FlaskForm):
    name = StringField('Name')
    time = TimeField('Time of Lesson', validators=[DataRequired()])
    typeofclass = SelectField('Type Of Class', validators=[DataRequired()], choices=[
        ('Group Exam', 'Group Exam Class'),
        ('Group Intensive', 'Group Intensive'),
        ('Group Children', 'Group Children'),
        ('Group General English', 'Group General English'),
        ('Group Business English', 'Group Business English'),
        ('In-Company General English', 'In-Company General English'),
        ('In-Company Business English', 'In-Company Business English')])
    step = SelectField('Step', choices=[
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
        ('16', 'Step 16')])
    exams = SelectField('Exam Level', choices=[
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
        ('IELTS C2', 'IELTS C2'),])
    kids = SelectField('Children Level', choices=[
        ('Red', 'Red'),
        ('Blue', 'Blue'),
        ('Yellow', 'Yellow'),
        ('Pink', 'Pink'),
        ('Orange', 'Orange'),
        ('Green', 'Green'),
        ('Violet', 'Violet'),
        ('Turquoise', 'Turquoise')])
    agerange = SelectField('Children Class Age Range', choices=[
        ('3-4', '3-4'),
        ('5-6', '5-6'),
        ('6-7', '6-7'),
        ('7-8', '7-8'),
        ('9-10', '9-10'),
        ('11-12', '11-12')])
    academy = SelectField('Academy', validators=[DataRequired()], choices=[
        ('Alonso Martínez','Alonso Martínez'),
        ('Argüelles','Argüelles'),
        ('Ercilla','Ercilla'),
        ('Gómez Laguna','Gómez Laguna'),
        ('La Paz','La Paz'),
        ('Nuevos Ministerios','Nuevos Ministerios'),
        ('Online', 'Online'),
        ('Rambla Catalunya','Rambla Catalunya'),
        ('San Miguel','San Miguel')])
    lengthofclass = SelectField('Length of class', validators=[DataRequired()], choices=[
        ('30 Minutes', '30 Minutes'),
        ('1 Hour', '1 Hour'),
        ('1,5 Hours', '1,5 Hours'),
        ('2 Hours', '2 Hours'),
        ('2,5 Hours', '2,5 Hours'),
        ('3 Hours', '3 Hours')])
    daysdone = SelectMultipleField('Days Done', validators=[DataRequired()], choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday')])
    startat = SelectField('Start at Lesson', validators=[DataRequired()], choices=[], validate_choice=False)
    comment = TextAreaField('Special Comments', validators=[Length(min=0, max=500)])
    submit = SubmitField('Create Class')



    def validate_daysdone(self, lengthofclass):
        ''' Validate day and time combinations. '''
        print(self.daysdone.data)
        # Check General english times and days
        if self.typeofclass.data == 'Group General English':
            
            if 'Monday' in self.daysdone.data and 'Wednesday' in self.daysdone.data:
                if 'Friday' not in self.daysdone.data and len(self.daysdone.data) > 2:
                    raise ValidationError('· Group classes on can only be on Monday and Wednesday or Tuesday and Thursday!')
                elif len(self.daysdone.data) > 3:
                    raise ValidationError('· Group classes on can only be on Monday and Wednesday or Tuesday and Thursday!')
                elif self.lengthofclass.data not in ('1 Hour',  '1,5 Hours'):
                    raise ValidationError('· Group classes on Monday and Wednesday can only be 1 Hour or 1,5 Hours long.')
            elif 'Tuesday' in self.daysdone.data and 'Thursday' in self.daysdone.data:
                if len(self.daysdone.data) > 2:
                    raise ValidationError('· Group classes on can only be on Monday and Wednesday or Tuesday and Thursday!')
                if self.lengthofclass.data not in ('1 Hour',  '1,5 Hours'):
                    raise ValidationError('· Group classes on Tuesday and Thursday can only be 1 Hour or 1,5 Hours long.')
            elif 'Friday' in self.daysdone.data and self.lengthofclass.data == '2 Hours':
                if len(self.daysdone.data) > 1:
                    raise ValidationError('· Two hour group classes can only take place on Fridays!')
            elif 'Saturday' in self.daysdone.data and self.lengthofclass.data == '2,5 Hours':
                if len(self.daysdone.data) > 1:
                    raise ValidationError('· Two hour group classes can only take place on Fridays!')
            else:
                raise ValidationError('· Ensure Group class and times are correct.')
            
            
        # Check Exams times and days
        if self.typeofclass.data == 'Group Exam':
            if 'Monday' in self.daysdone.data and 'Wednesday' in self.daysdone.data:
                if 'Friday' not in self.daysdone.data and len(self.daysdone.data) > 2:
                    raise ValidationError('· Group Exam classes on can only be on Monday and Wednesday or Tuesday and Thursday!')
                elif len(self.daysdone.data) > 3:
                    raise ValidationError('· Group Exam classes on can only be on Monday and Wednesday or Tuesday and Thursday!')
                elif self.lengthofclass.data != '1,5 Hours':
                    raise ValidationError('· Group Exam classes on Monday and Wednesday can only be 1,5 Hours long.')
            elif 'Tuesday' in self.daysdone.data and 'Thursay' in self.daysdone.data:
                if len(self.daysdone.data) > 2:
                    raise ValidationError('· Group Exam classes on can only be on Monday and Wednesday or Tuesday and Thursday!')
                elif self.lengthofclass.data != '1,5 Hours':
                    raise ValidationError('· Group Exam classes on Tuesday and Thursday can only be 1,5 Hours long.')
                else:
                    raise ValidationError('· Ensure Group class and times are correct')
            elif 'Friday' in self.daysdone.data and self.lengthofclass.data == '2 Hours':
                if len(self.daysdone.data) > 1:
                    raise ValidationError('· Two hour group classes can only take place on Fridays!')
            elif 'Saturday' in self.daysdone.data and self.lengthofclass.data == '2,5 Hours':
                if len(self.daysdone.data) > 1:
                    raise ValidationError('· Two and a half hour group classes can only take place on Saturdays!')
            else:
                raise ValidationError('· Ensure Group class and times are correct.')
            
        # Check Children
        if self.typeofclass.data == 'Group Children':

            if 'Monday' in self.daysdone.data and 'Wednesday' in self.daysdone.data:
                if 'Friday' not in self.daysdone.data and len(self.daysdone.data) > 2:
                    raise ValidationError('· Group Children classes on can only be on Monday and Wednesday or Tuesday and Thursday!')
                elif len(self.daysdone.data) > 3:
                    raise ValidationError('· Group Children classes on can only be on Monday and Wednesday or Tuesday and Thursday!')
                elif self.lengthofclass.data != '1 Hour':
                    raise ValidationError('· Group Children classes on Monday and Wednesday can only be 1 Hour long.')
                else:
                    raise ValidationError('· Ensure Group class and times are correct')
            elif 'Tuesday' in self.daysdone.data and 'Thursay' in self.daysdone.data:
                if len(self.daysdone.data) > 2:
                    raise ValidationError('· Group Children classes on can only be on Monday and Wednesday or Tuesday and Thursday!')
                elif self.lengthofclass.data != '1 Hour':
                    raise ValidationError('· Group Children classes on Tuesday and Thursday can only be 1 Hour long.')
                else:
                    raise ValidationError('· Ensure Group class and times are correct')
            elif 'Friday' in self.daysdone.data and self.lengthofclass.data == '2 Hours':
                if len(self.daysdone.data) > 1:
                    raise ValidationError('· Two hour children group classes can only take place on Fridays!')
            elif 'Saturday' in self.daysdone.data and self.lengthofclass.data == '2,5 Hours':
                if len(self.daysdone.data) > 1:
                    raise ValidationError('· Two and a half hour group classes can only take place on Saturdays!')
            else:
                raise ValidationError('· Ensure Group class and times are correct.')
            

        # Check Intensives
        if self.typeofclass.data == 'Group Intensive':
            if self.lengthofclass.data != '1,5 Hours' and self.lengthofclass.data != '2 Hours':
                raise ValidationError('· Intensive Classes need to be 1,5 Hours or 2 Hours long!')

    def validate_startat(self, step):
        ''' Check that the lesson entered is in the step '''

        lowest = int(self.step.data) * 10 - 9
        highest = int(self.step.data) * 10
        if int(self.startat.data) < lowest or int(self.startat.data) > highest:
            raise ValidationError('· Class can only start between lessons {} and {} at step {}'.format(lowest, highest, self.step.data))
  
                
    def validate_step(self, typeofclass):
        ''' Check ensure that level is filled. '''

        if self.typeofclass.data=='121-General English' or self.typeofclass.data=='Group General English' or \
            self.typeofclass.data=='121-Business English' or self.typeofclass.data=='Group Business English':
            if self.step.data is None:
                raise ValidationError('· Ensure step is filled to match level.')
        if self.typeofclass.data=='121-Exam Class' or self.typeofclass.data=='Group Exam Class':
            if self.exams.data is None:
                raise ValidationError('· Ensure exam level is filled to match level.')
        if self.typeofclass.data=='Group Children' or self.typeofclass.data=='121-Children':
            if self.kids.data is None or self.agerange.data is None:
                raise ValidationError('· Ensure kids level and age range fields are filled to match level.')

    def validate_time(self, time):
        ''' Ensure time allows classes to take place between the assigned hours. '''

        if not 8 <= time.data.hour <= 21:
            raise ValidationError('· The academies are only open from 08:00 until 10:00.')
        if time.data.minute not in (0, 15, 30, 45):
            raise ValidationError('· Ensure classes start either on the hour or in fifteen minute intervals.')
        if time.data.hour == 21 and time.data.minute != 0:
            raise ValidationError('· You cannot book a class for after 21:00.')
        if time.data.hour == 21 and self.lengthofclass.data not in ('30 Minutes', '1 Hour'):
            raise ValidationError('· Class cannot be at that time so long, as this would finish after the acadamies close.')
        if 'Saturday' in self.daysdone.data:
            if not 8 <= time.data.hour <= 11:
                raise ValidationError('· On Saturdays you can only book classes at 08:00 or 11:30.')
            if time.data.hour == 11 and time.data.minute != 30:
                raise ValidationError('· You cannot book a class for after 11:30 on a Saturday.')

    def validate_class(self, name, academy):
        ''' heck that company name filled in '''

        
        options_IC = [
            'In-Company General English',
            'In-Company Business English',
        ]
        if self.typeofclass.data in options_IC and name.data == None:
            raise ValidationError('Please Fill in the company name')
            




class StepProgressForm(FlaskForm):
    ''' Step Progress Form. '''

    lesson_number = SelectField('Lesson Number', validators=[DataRequired()], choices=[], validate_choice=False)
    last_page = SelectField('Last Page', validators=[DataRequired()], choices=[], validate_choice=False)
    last_word = StringField('Last Word', validators=[DataRequired()])
    exercises = StringField('Exercises Done')
    comment = TextAreaField('Comment On Class')
    sub = SubmitField('Add Progress')


class AttendanceForm(FlaskForm):
    attended = SelectField('Attended',  choices=[
        ('Yes','Yes'),
        ('No','No')])
    score = IntegerField('Score', validators=[OptionalIf('attended')], render_kw={"placeholder": "3/4/5"})
    writing = IntegerField('Writing', validators=[OptionalIf('attended')], render_kw={"placeholder": "Percentage (Only numbers)"})
    speaking = IntegerField('Speaking', validators=[OptionalIf('attended')], render_kw={"placeholder": "Percentage (Only numbers)"})

    def validate_score(self, attended):
        if self.attended.data == 'Yes' and self.score.data == None:
            raise ValidationError('You need to provide score if student attended!')
        elif self.attended.data == 'Yes':
            if  self.score.data < 3 or self.score.data > 5:
                raise ValidationError('Score needs to be either 3, 4, or 5.')

        

class InsertCustom(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired()])
    exercises = StringField('Exercises')
    submit = SubmitField('Insert Custom Programming')