import os

from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, Status


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
        if len(username.data.split(' ')) != 2:
            raise ValidationError('Username must consists of first name and last name')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
        if Status.query.filter_by(email=email.data).first() is None:
            raise ValidationError('Unregistered email')

    def validate_password(self, password):
        if len(password.data) < 7:
            raise ValidationError('Password must be longer than 6 symbols')
        if password.data.isalpha() or password.data.isdigit() or not password.data.isalnum():
            raise ValidationError('Password must consists of letters and numbers')

class MakeHomeworkForm(FlaskForm):
    number = StringField('Задание или сообщение', validators=[DataRequired()])
    comments = TextAreaField('Комментарии')
    files = FileField('Загрузить файл(если файлов несколько загрузите одним архивом)')
    submit = SubmitField('Загрузить')


class HomeworkLoadForm(FlaskForm):
    comments = TextAreaField('Решение')
    files = FileField('Загрузить файл(если файлов несколько загрузите одним архивом)')
    submit = SubmitField('Загрузить')


class CheckForm(FlaskForm):
    code = PasswordField('Email code', validators=[DataRequired()])
    submit = SubmitField('Проверить')


class LoadAvatarForm(FlaskForm):
    files = FileField('Загрузить фото')
    submit = SubmitField('Загрузить')
