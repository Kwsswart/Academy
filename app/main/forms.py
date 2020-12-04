import phonenumbers
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField, SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User


class AnnouncementForm(FlaskForm):
    """ Form to Handle Submission of Announcements """

    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
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
    for_all = BooleanField('For all Academies')
    submit = SubmitField('Make Announcement')
