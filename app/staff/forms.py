import phonenumbers
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User


class EditProfileForm(FlaskForm):
    """ Form to handle changes to User/Staff data """
    
    name = StringField('Full Name', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    position = SelectField('Position', validators=[DataRequired()], choices=[], validate_choice=False)
    academy = SelectField('Academy', validators=[DataRequired()], choices=[
        ('Alonso Martínez','Alonso Martínez'),
        ('Argüelles','Argüelles'),
        ('Ercilla','Ercilla'),
        ('Gómez Laguna','Gómez Laguna'),
        ('La Paz','La Paz'),
        ('Nuevos Ministerios','Nuevos Ministerios'),
        ('Online', 'Online'),
        ('Rambla Catalunya','Rambla Catalunya'),
        ('San Miguel','San Miguel')
        ])
    trained = SelectMultipleField('Trained to teach', choices=[
        ('General English', 'General English'),
        ('Exam', 'Exam'),
        ('Children', 'Children'),
        ('Level Test', 'Level Test'),
        ('Admin', 'Admin')
        ])
    submit = SubmitField('Confirm')

    def __init__(self, obj, *args, **kwargs):
        self.user = int(obj)
        super(EditProfileForm, self).__init__(*args, **kwargs)

    def validate_name(self, name):
        """ Validate name isn't in use with users withing the company """

        user = User.query.filter_by(id=self.user).first()
        if name.data != user.name:
            user1 = User.query.filter_by(name=name.data).first()
            if user1 is not None:
                raise ValidationError('Name already in use.')

    def validate_phone2(self, phone):
        """ Validate Phone Number isn't in use in the database """

        user = User.query.filter_by(id=self.user).first()
        if phone.data != user.phone:
            new = User.query.filter_by(phone=phone.data).first()
            if new is not None:
                raise ValidationError('Phone number already in use.')

    def validate_email(self, email):
        """ Validate Email isn't in use in the database """
        
        user = User.query.filter_by(id=self.user).first()
        if email.data != user.email:
            new = User.query.filter_by(email=email.data).first()
            if new is not None:
                raise ValidationError('Email already in use.')

    def validate_phone(self, phone):
        """ Validate Phone Number matching normal patterns and is a valid phone number """

        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')


class RemoveUserForm(FlaskForm):
    """ Form to handle removal of staff data """
    
    affirmation = SelectField('Are you sure?', validators=[DataRequired()], choices=[
        ('Yes','Yes'),
        ('No','No')
    ])
    submit = SubmitField('Confirm')


class AvatarUploadForm(FlaskForm):
    """ Form to handle custom avatar uploads """
    
    file = FileField('File', validators=[FileRequired(), FileAllowed(
        ['jpg', 'jpeg','png'], 'Only "jpg", "jpeg" and "png" files are supported')])
    submit = SubmitField('Submit field')


class EmailForm(FlaskForm):
    """ Form to handle email data """
    
    subject = StringField('Subject', validators=[DataRequired(), Length(min=0, max=50)])
    body = TextAreaField('Message', validators=[DataRequired(), Length(min=0, max=500)])
    submit = SubmitField('Send Email')