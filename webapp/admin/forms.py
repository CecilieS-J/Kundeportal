# webapp/admin/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Regexp, EqualTo
from webapp.models import UserRole


class CreateUserForm(FlaskForm):
    """Admin-opretter af ny bruger. Kodeord sættes automatisk til Magasin2025."""
    username = StringField(
        'Personalnummer',
        validators=[
            DataRequired(),
            Regexp(r'^\d{4,6}$', message="Personalenummer skal være 4–6 cifre")
        ]
    
    )
    role = SelectField(
        'Rolle',
        choices=[(r.name, r.value) for r in UserRole]
    )
    submit = SubmitField('Opret bruger')

    
class EditUserForm(FlaskForm):
    username = StringField('Personalnummer', render_kw={'readonly': True})
    password = PasswordField('Ny adgangskode', validators=[])
    confirm  = PasswordField('Gentag adgangskode',
                  validators=[EqualTo('password', message='Kodeord skal matche')])
    role     = SelectField('Rolle',
                  choices=[(r.name, r.value) for r in UserRole])
    submit   = SubmitField('Gem ændringer')
