from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired

class CustomerLookupForm(FlaskForm):
    """
    Form for looking up customers by different identifiers.
    """
    search_type = SelectField(
        'Søg efter',
        choices=[
            ('email', 'E-mail'),
            ('customer_no', 'Customer No'),
            ('goodie_id', 'Goodie ID'),
            ('sib_id', 'SIB ID')
        ],
        validators=[DataRequired()]
    )
    query = StringField(
        'Søgeværdi',
        validators=[DataRequired()]
    )
    submit = SubmitField('Søg')

