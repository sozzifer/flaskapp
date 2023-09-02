from typing import Dict, List, Optional, Union

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug import Response
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User

# @app.route decorator defines the URLs to which the associated View function refers
@app.route("/")
@app.route("/index")
# @login_required decorator indicates that user must be logged in to view this page
@login_required
def index() -> str:
    posts: List[Dict] = [
        {"author": {"username": "John"}, "body": "Beautiful day in Portland!"},
        {"author": {"username": "Susan"}, "body": "The Avengers movie was so cool!"},
    ]
    # Arguments passed to render_template() relate to the keywords used in templates
    return render_template(
        "index.html", title=f"{current_user.username}'s Homepage", posts=posts
    )


@app.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    # If user is already logged in, redirect to homepage
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form: LoginForm = LoginForm()
    if form.validate_on_submit():
        # Check database for username - 1 result expected
        # Instantiate User object to hold user details from database
        user: User = User.query.filter_by(username=form.username.data).first()
        # If username not found or password is incorrect, flash error
        if user is None or not user.check_password(form.password.data):
            flash(f"Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page: Optional[str] = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout() -> Response:
    logout_user()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form: RegistrationForm = RegistrationForm()
    if form.validate_on_submit():
        user: User = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f"User {user.username} registered")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)

# User profile page - dynamic component <username>
@app.route("/user/<username>")
@login_required
def user(username: str) -> str:
    # first_or_404() returns one result if user found, otherwise returns 404
    user: User = User.query.filter_by(username=username).first_or_404()
    posts: List[Dict] = [
        {"author": user, "body": "Test post #1"},
        {"author": user, "body": "Test post #2"}
    ]
    return render_template("user.html", user=user, posts=posts)