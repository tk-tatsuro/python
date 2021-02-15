from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField, SubmitField,
)
from wtforms.validators import DataRequired


class GetPostForm(FlaskForm):
    tag = StringField(
        'tag: ', validators=[DataRequired()]
    )
    submit = SubmitField('Get Post')
