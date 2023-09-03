from datetime import datetime as dt
from typing import Dict, List, Optional, Union

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug import Response
from werkzeug.urls import url_parse

from app import app, db
from app.forms import EditProfileForm, LoginForm, RegistrationForm
from app.models import User


@app.before_request
def before_request():
    """Code to be executed before any view function is called"""
    if current_user.is_authenticated:  # type: ignore
        current_user.last_seen = dt.utcnow()
        db.session.commit()


# @app.route decorator defines the URLs to which the associated view function refers (i.e. www.sozzifer.org/ and www.sozzifer.org/index)
@app.route("/")
@app.route("/index")
# @login_required decorator indicates that user must be logged in to view route
@login_required
def index() -> str:
    """Index view function"""
    posts: List[Dict] = [
        {"author": {"username": "John"}, "body": "Beautiful day in Portland!"},
        {"author": {"username": "Susan"}, "body": "The Avengers movie was so cool!"},
    ]
    # Arguments passed to render_template() relate to the keywords used in templates
    return render_template(
        "index.html", title=f"{current_user.username}'s Homepage", posts=posts  # type: ignore
    )


@app.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    """Login view function"""
    if current_user.is_authenticated:  # type: ignore
        # If user is already logged in, redirect to homepage
        return redirect(url_for("index"))
    form: LoginForm = LoginForm()
    if form.validate_on_submit():
        # If form is submitted and passes validation, redirect to login page
        user: User = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            # If username not found or password is incorrect, flash message and redirect to login page (i.e. refresh current page)
            flash(f"Invalid username or password")
            return redirect(url_for("login"))
        # Set current_user
        login_user(user, remember=form.remember_me.data)
        # If user attempts to access a page for which @login_required, get the value of `next` and generate the redirect URL, otherwise redirect to homepage
        next_page: Optional[str] = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout() -> Response:
    """Log out user and redirect to login page"""
    logout_user()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
    """Register view function"""
    if current_user.is_authenticated:  # type: ignore
        # If user is already logged in, redirect to homepage
        return redirect(url_for("index"))
    form: RegistrationForm = RegistrationForm()
    if form.validate_on_submit():
        # If registration form is submitted and passes validation, flash message and redirect to login page
        user: User = User(username=form.username.data, email=form.email.data)  # type: ignore
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f"User {user.username} registered")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/user/<username>")
@login_required
def user_profile(username: str) -> str:
    """User profile view function."""
    user: User = User.query.filter_by(username=username).first_or_404()
    posts: List[Dict] = [
        {"author": user, "body": "Test post #1"},
        {"author": user, "body": "Test post #2"},
    ]
    return render_template(
        "user.html", user=user, posts=posts, title=f"{user.username}'s Profile"
    )


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile() -> Union[str, Response]:
    """Edit profile view function"""
    # TODO Address potential race condition by locking table
    form = EditProfileForm(current_user.username)  # type: ignore
    if form.validate_on_submit():
        # If profile form is submitted and passes validation, flash message and redirect to edit_profile page (i.e. refresh current page)
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your profile has been updated")
        return redirect(url_for("edit_profile"))
    elif request.method == "GET":
        # If validate_on_submit() returns False because this is a GET request, populate form from database fields
        form.username.data = current_user.username  # type: ignore
        form.about_me.data = current_user.about_me  # type: ignore
    return render_template("edit_profile.html", title="Edit Profile", form=form)
