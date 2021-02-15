from flask_wtf import FlaskForm
from wtforms.fields import (
    SubmitField, HiddenField, TextAreaField
)
from flaskr.models.base import User, UserConnect


class MessageForm(FlaskForm):
    to_user_id = HiddenField()
    message = TextAreaField()
    submit = SubmitField('Send Message')

    def validate(self):
        if not super(FlaskForm, self).validate():
            return False
        is_friend = UserConnect.is_friend(self.to_user_id.data)
        if not is_friend:
            return False
        return True
