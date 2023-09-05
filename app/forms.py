from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    """Login form."""

    username: StringField = StringField("Username", validators=[DataRequired()])
    password: PasswordField = PasswordField("Password", validators=[DataRequired()])
    remember_me: BooleanField = BooleanField("Remember me")
    submit: SubmitField = SubmitField("Sign in")


class RegistrationForm(FlaskForm):
    """Registration form."""

    username: StringField = StringField("Username", validators=[DataRequired()])
    email: StringField = StringField(
        "Email address", validators=[DataRequired(), Email()]
    )
    password: PasswordField = PasswordField("Password", validators=[DataRequired()])
    password2: PasswordField = PasswordField(
        "Repeat password", validators=[DataRequired(), EqualTo("password")]
    )
    submit: SubmitField = SubmitField("Register")

    def validate_username(self, username: StringField) -> None:
        """Validate username."""
        user: User = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Username already registered.")

    def validate_email(self, email: StringField) -> None:
        """Validate email."""
        user: User = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Email address already registered.")


class EditProfileForm(FlaskForm):
    username: StringField = StringField("Username", validators=[DataRequired()])
    about_me: TextAreaField = TextAreaField(
        "About me", validators=[Length(min=0, max=140)]
    )
    submit: SubmitField = SubmitField("Submit")

    def __init__(self, original_username: str, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username: StringField) -> None:
        if username.data != self.original_username:
            user: User = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError("Username not available.")


class EmptyForm(FlaskForm):
    submit: SubmitField = SubmitField("Submit")


class PostForm(FlaskForm):
    post = TextAreaField(
        "Write post", validators=[DataRequired(), Length(min=1, max=140)]
    )
    submit = SubmitField("Post")
