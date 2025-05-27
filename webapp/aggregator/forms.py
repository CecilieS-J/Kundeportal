from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, FileField, SubmitField
from wtforms.validators import DataRequired, Optional

class CustomerLookupForm(FlaskForm):
    search_type = RadioField(
        'Søg efter',
        choices=[('email','Email'),('customer_no','Customer No'),('goodie_id','Goodiecard')],
        validators=[DataRequired()]
    )
    query = StringField('Værdi', validators=[Optional()])
    file = FileField('Upload fil (.csv eller .xlsx)', validators=[Optional()])
    submit = SubmitField('Søg')
