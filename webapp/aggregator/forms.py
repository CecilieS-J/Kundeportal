# webapp/aggregator/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import Optional, Email

class GoodieForm(FlaskForm):
    goodie_id = StringField(
        "Goodie ID",
        validators=[Optional()]
    )
    email = EmailField(
        "Email",
        validators=[Optional(), Email(message="Ugyldig emailadresse")]
    )
    customer_no = StringField(
        "Customer No",
        validators=[Optional()]
    )
    submit = SubmitField("Søg")