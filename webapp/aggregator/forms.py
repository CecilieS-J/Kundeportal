from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import Optional, Email, DataRequired

class GoodieForm(FlaskForm):
    search_type = RadioField(
        "Søg efter",
        choices=[
            ('goodie_id',   'Goodie ID'),
            ('email',       'Email'),
            ('customer_no', 'Customer No'),
             ('sib_id',       'SIB ID'),
            ('phone',        'Telefonnummer'),
        ],
        default='goodie_id',
        validators=[DataRequired()]
    )
    query_value = StringField("Søgeværdi", validators=[Optional()])
    excel_file = FileField(
        "Upload Excel (.xlsx)",
        validators=[
            Optional(),                         # <— Her skal du have Optional(), IKKE FileRequired
            FileAllowed(['xlsx'], "Kun .xlsx-filer er tilladt")
        ]
    )
    submit = SubmitField("Søg")



class EventForm(FlaskForm):
    goodie_id = StringField(
        "Goodie ID",
        validators=[DataRequired(message="Du skal indtaste et Goodie ID")]
    )
    submit    = SubmitField("Hent event-log")