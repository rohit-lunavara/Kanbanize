from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from app.models import Project

class NewProjectForm(FlaskForm) :
    name = StringField("Name", validators = [DataRequired(), Length(min = 3, max = 128)])
    description = TextAreaField("Description", validators = [Length(max = 8192)])
    submit = SubmitField("Create")