# webapp/auth/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo

# Login form with username and password fields
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

# Login form with username and password fields
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

class ActivateForm(FlaskForm):
    password = PasswordField(
        'Adgangskode',
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
    submit = SubmitField('Aktivér konto')


class OTPForm(FlaskForm):
    otp = StringField('SMS-kode', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Bekræft kode')