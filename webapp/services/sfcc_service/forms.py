from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SFCCLookupForm(FlaskForm):
    query = StringField('Customer Number', validators=[DataRequired()])
    submit = SubmitField('Søg')