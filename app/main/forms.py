from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField
from wtforms.fields import HiddenField, SelectField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, Length
from app.models import Project

class NewComponentForm(FlaskForm) :
    name = StringField("Name", validators = [DataRequired(), Length(max = 128)])
    description = TextAreaField("Description", validators = [Length(max = 8192)])
    submit = SubmitField("Submit")

class EditTaskForm(FlaskForm) :
    name = StringField("Name", validators = [DataRequired(), Length(max = 128)])
    description = TextAreaField("Description", validators = [Length(max = 8192)])
    is_complete = BooleanField("Completed?")
    tasklists = SelectField("Tasklist", coerce = int, validators = [DataRequired()])
    submit = SubmitField("Submit")

class NewTaskLogForm(FlaskForm) :
    start_time = DateTimeLocalField("Start Time", format='%Y-%m-%dT%H:%M', id = "startDatePicker", validators = [DataRequired()])
    end_time = DateTimeLocalField("End Time", id = "endDatePicker", format='%Y-%m-%dT%H:%M', validators = [DataRequired()])
    note = StringField("Note", validators = [Length(max = 128)])
    minutesTimezoneOffset = HiddenField("Timezone Offset")
    submit = SubmitField("Submit")