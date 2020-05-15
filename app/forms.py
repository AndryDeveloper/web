from flask_wtf import FlaskForm, validators
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email
import email_validator


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    message = ''

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat your password', validators=[DataRequired()])

    email = EmailField('Email address', validators=[Email(), DataRequired()])

    submit = SubmitField('Ok')

