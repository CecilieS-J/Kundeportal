from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SFCCLookupForm(FlaskForm):
    customer_no = StringField("Customer Number", validators=[DataRequired()])
    submit = SubmitField("Søg")
