# webapp/aggregator/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class GoodieForm(FlaskForm):
    goodie_id = StringField(
        "Goodie ID",
        validators=[DataRequired(message="Du skal indtaste et Goodie ID")]
    )
    submit = SubmitField("Hent data")
