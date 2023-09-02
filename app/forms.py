from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    username: StringField = StringField("Username", validators=[DataRequired()])
    password: PasswordField = PasswordField("Password", validators=[DataRequired()])
    remember_me: BooleanField = BooleanField("Remember me")
    submit: SubmitField = SubmitField("Sign in")


class RegistrationForm(FlaskForm):
    username: StringField = StringField("Username", validators=[DataRequired()])
    email: StringField = StringField("Email address", validators=[DataRequired(), Email()])
    password: PasswordField = PasswordField("Password", validators=[DataRequired()])
    password2: PasswordField = PasswordField("Repeat password", validators=[DataRequired(), EqualTo("password")])
    submit: SubmitField = SubmitField("Register")

    def validate_username(self, username: StringField):
        user: User = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Username already registered")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Email address already registered")