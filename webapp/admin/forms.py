# webapp/admin/forms.py
import logging
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, ValidationError,PasswordField
from wtforms.validators import DataRequired, Regexp, Email, Length, EqualTo
from webapp.models import User, UserRole


logger = logging.getLogger(__name__)

class CreateUserForm(FlaskForm):
    """
    Admin form for creating a new user.
    The password is autogenerated via activation link.
    """
    username = StringField(
        'Personalnummer',
        validators=[
            DataRequired(),
            Regexp(r'^\d{4,6}$', message="Personalenummer skal være 4–6 cifre")
        ]
    )
    email = StringField(
        "E-mail",
        validators=[
            DataRequired(),
            Email(message="Ugyldig e-mailadresse"),
            Length(max=120)
        ]
    )
    phone_number = StringField(
    "Telefonnummer",
    validators=[
        DataRequired(message="Telefonnummer er påkrævet"),
        Length(min=8, max=20, message="Telefonnummer skal være mellem 8 og 20 tegn")
        ]
    )
    role = SelectField(
        'Rolle',
        choices=[(r.name, r.value) for r in UserRole]
    )
    submit = SubmitField('Opret bruger')

    def validate_username(self, field):
        logger.debug(f"👉 validate_username called with {field.data!r}")
        existing = User.query.filter_by(username=field.data).first()
        logger.debug(f"   -> bruger findes? {existing!r}")
        if existing:
            raise ValidationError('Brugernavn optaget')

    def validate_email(self, field):
        logger.debug(f"👉 validate_email called with {field.data!r}")
        existing = User.query.filter_by(email=field.data).first()
        logger.debug(f"   -> e-mail findes? {existing!r}")
        if existing:
            raise ValidationError('E-mail optaget')


class EditUserForm(FlaskForm):
    """
    Admin form for editing an existing user.
    Username is read-only. Password change is optional.
    """
    username = StringField('Personalnummer', render_kw={'readonly': True})
    password = PasswordField(
        'Ny adgangskode',
        validators=[
            Length(min=8, message="Mindst 8 tegn"),
            Regexp(r'.*[A-Z].*', message="Mindst ét stort bogstav"),
            Regexp(r'.*\d.*', message="Mindst ét tal"),
            Regexp(r'.*\W.*', message="Mindst ét specialtegn")
        ]
    )
    confirm = PasswordField(
        'Gentag adgangskode',
        validators=[EqualTo('password', message='Kodeord skal matche')]
    )
    phone_number = StringField(
    "Telefonnummer",
    validators=[
        DataRequired(message="Telefonnummer er påkrævet"),
        Length(min=8, max=20, message="Telefonnummer skal være mellem 8 og 20 tegn")
        ]
    )
    role = SelectField(
        'Rolle',
        choices=[(r.name, r.value) for r in UserRole]
    )
    submit = SubmitField('Gem ændringer')