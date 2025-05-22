from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired

class BrevoLookupForm(FlaskForm):
    search_type = SelectField(
        'Søg efter',
        choices=[('email', 'E-mail'), ('sib_id', 'SIB ID')],
        validators=[DataRequired()]
    )
    query = StringField('Søgeværdi', validators=[DataRequired()])
    submit = SubmitField('Søg')