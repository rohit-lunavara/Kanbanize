from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, Length
from app.models import User

class LoginForm(FlaskForm) :
    username = StringField("Username", validators = [DataRequired(), Length(min = 6, max = 64)])
    password = PasswordField("Password", validators = [DataRequired(), Length(min = 6, max = 64)])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

class RegistrationForm(FlaskForm) :
    username = StringField("Username", validators = [DataRequired(), Length(min = 6, max = 64)])
    email = StringField("Email", validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators = [DataRequired(), Length(min = 6, max = 64)])
    password2 = PasswordField("Repeat Password", validators = [DataRequired(), EqualTo("password"), Length(min = 6, max = 64)])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Register")

    def validate_username(self, username) :
        user = User.query.filter_by(username = username.data).first()
        if user is not None :
            raise ValidationError("Please use a different username.")

    def validate_email(self, email) :
        user = User.query.filter_by(email = email.data).first()
        if user is not None :
            raise ValidationError("Please use a different email address.")