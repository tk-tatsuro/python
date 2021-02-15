from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField, SubmitField,
)
from wtforms.validators import DataRequired


class GetJobForm(FlaskForm):
    tag = StringField(
        'tag: ', validators=[DataRequired()]
    )
    submit = SubmitField('Get Job offers')


class OutputHtmlForm(FlaskForm):
    tag = StringField(
        'tag: ', validators=[DataRequired()]
    )
    submit = SubmitField('Output HTML')
