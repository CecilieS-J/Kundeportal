# webapp/admin/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Regexp, EqualTo, Email, Length
from webapp.models import UserRole, User


class CreateUserForm(FlaskForm):
    """
    Admin form for creating a new user.
    The password is automatically set to 'Magasin2025'.
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
        validators=[DataRequired(), Email(message="Ugyldig e-mailadresse"), Length(max=120)]
    )
    role = SelectField(
        'Rolle',
        choices=[(r.name, r.value) for r in UserRole]
    )
    submit = SubmitField('Opret bruger')
    
    def validate_username(self, field):
        """Kaster fejl, hvis username allerede findes i databasen."""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Brugernavn optaget')

    
class EditUserForm(FlaskForm):
    """
    Admin form for editing an existing user.
    Username is read-only. Password change is optional.
    """
    username = StringField('Personalnummer', render_kw={'readonly': True})
    password = PasswordField('Ny adgangskode', validators=[])
    confirm  = PasswordField('Gentag adgangskode',
                  validators=[EqualTo('password', message='Kodeord skal matche')])
    role     = SelectField('Rolle',
                  choices=[(r.name, r.value) for r in UserRole])
    submit   = SubmitField('Gem ændringer')
