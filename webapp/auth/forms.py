# webapp/auth/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo

class LoginForm(FlaskForm):
    username = StringField(
        'Brugernavn',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Adgangskode',
        validators=[DataRequired()]
    )
    submit = SubmitField('Log ind')

class ChangePasswordForm(FlaskForm):
    password = PasswordField(
        'Ny adgangskode',
        validators=[
            DataRequired(),
            Length(min=8, message="Mindst 8 tegn"),
            Regexp(r'.*[A-Z].*', message="Mindst ét stort bogstav"),
            Regexp(r'.*\d.*', message="Mindst ét tal"),
            Regexp(r'.*\W.*', message="Mindst ét specialtegn")
        ]
    )
    confirm = PasswordField(
        'Gentag adgangskode',
        validators=[
            DataRequired(),
            EqualTo('password', message='Kodeord skal matche')
        ]
    )
    submit = SubmitField('Skift adgangskode')
