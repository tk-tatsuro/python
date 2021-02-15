
from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField, FileField, PasswordField,
    SubmitField, HiddenField, TextAreaField
)
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_login import current_user
from flask import flash

from flaskr.models.base import User, UserConnect


class LoginForm(FlaskForm):
    email = StringField(
        'Email Address: ', validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        'Password: ',
        validators=[DataRequired(), EqualTo('confirm_password', message='Password does not match')]
    )
    confirm_password = PasswordField(
        'Repeat Password: ', validators=[DataRequired()]
    )
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField(
        'Email Address: ', validators=[DataRequired(), Email('Wrong email address')]
    )
    username = StringField('Username: ', validators=[DataRequired()])
    submit = SubmitField('Registration')

    def validate_email(self, field):
        if User.select_user_by_email(field.data):
            raise ValidationError('Email address is already registered')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        'Password',
        validators=[DataRequired(), EqualTo('confirm_password', message='Password does not match')]
    )
    confirm_password = PasswordField(
        'Password Confirm: ', validators=[DataRequired()]
    )
    submit = SubmitField('Update Password')

    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('Password must be at least 8 characters')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email Address: ', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if not User.select_user_by_email(field.data):
            raise ValidationError('Email address does not exist')


class UserForm(FlaskForm):
    email = StringField(
        'Email Address: ', validators=[DataRequired(), Email('Wrong email address')]
    )
    username = StringField('Username: ', validators=[DataRequired()])
    picture_path = FileField('File Upload')
    submit = SubmitField('Update Registration Info')

    def validate(self):
        if not super(FlaskForm, self).validate():
            return False
        user = User.select_user_by_email(self.email.data)
        if user:
            if user.id != int(current_user.get_id()):
                flash('Email address does not exist')
                return False
        return True


class ChangePasswordForm(FlaskForm):
    password = PasswordField(
        'Password',
        validators=[DataRequired(), EqualTo('confirm_password', message='Password does not match')]
    )
    confirm_password = PasswordField(
        'Confirm Password: ', validators=[DataRequired()]
    )
    submit = SubmitField('Update Password')

    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('Password must be at least 8 characters')


class UserSearchForm(FlaskForm):
    username = StringField(
        'Username: ', validators=[DataRequired()]
    )
    submit = SubmitField('Search User')


class ConnectForm(FlaskForm):
    connect_condition = HiddenField()
    to_user_id = HiddenField()
    submit = SubmitField()
