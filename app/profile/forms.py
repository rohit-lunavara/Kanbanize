from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import User

class EditProfileForm(FlaskForm) :
    username = StringField("Username", validators = [DataRequired(), Length(min = 6, max = 64)])
    about_me = TextAreaField("About Me", validators = [Length(min = 0, max = 128)])
    submit = SubmitField("Submit")

    def __init__(self, original_username, *args, **kwargs) :
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username) :
        if username.data != self.original_username :
            user = User.query.filter_by(username = self.username.data).first()
            if user is not None :
                raise ValidationError("Please use a different username.")