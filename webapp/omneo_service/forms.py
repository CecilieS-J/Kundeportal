from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, SubmitField
from wtforms.validators import DataRequired

class OmneoLookupForm(FlaskForm):
    search_type = RadioField(
        'Søg efter', 
        choices=[('email', 'Email'), ('card_pos', 'GoodieCard ID')],
        default='email'
    )
    query_value = StringField('Søgeværdi', validators=[DataRequired(message="Du skal indtaste en værdi")])
    submit = SubmitField('Søg')
