import phonenumbers
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User



class LoginForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class UserRegistrationForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Full Name', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    position = SelectField('Position', validators=[DataRequired()], choices=[
        ('Upper Management', 'Upper Management'),
        ('Management', 'Management'), 
        ('Admin','Admin'), 
        ('Teacher','Teacher')])
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
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
    
    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')
