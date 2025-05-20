from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class OmneoLookupForm(FlaskForm):
    member_id = StringField('GoodieCard ID')
    email = StringField('E-mail')
    submit = SubmitField('Lookup')
