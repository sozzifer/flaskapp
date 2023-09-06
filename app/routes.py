from datetime import datetime as dt
from typing import Dict, List, Optional, Union

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug import Response
from werkzeug.urls import url_parse

from app import app, db
from app.email import send_password_reset_email
from app.forms import (
    EditProfileForm,
    LoginForm,
    PostForm,
    RegistrationForm,
    EmptyForm,
    ResetPasswordForm,
    ResetPasswordRequestForm,
)
from app.models import Post, User


@app.before_request
def before_request():
    """Code to be executed before any view function is called"""
    if current_user.is_authenticated:  # type: ignore
        current_user.last_seen = dt.utcnow()
        db.session.commit()


# @app.route decorator defines the URLs to which the associated view function refers (i.e. www.sozzifer.org/ and www.sozzifer.org/index)
@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
# @login_required decorator indicates that user must be logged in to view this page
@login_required
def index() -> Union[Response, str]:
    """Index page (homepage) view function"""
    form = PostForm()
    if form.validate_on_submit():
        # If form is submitted and passes validation, add post to database, flash message and redirect to homepage
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post is now live!")
        # Use redirect() to avoid inserting duplicate posts if user refreshes the page: https://en.wikipedia.org/wiki/Post/Redirect/Get
        return redirect(url_for("index"))
    page = request.args.get(key="page", default=1, type=int)
    # Get a list of followed posts for the current user and paginate
    posts = current_user.followed_posts().paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False
    )
    next_url = url_for("index", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("index", page=posts.prev_num) if posts.has_prev else None
    # Arguments passed to render_template() relate to the keywords used in templates
    return render_template(
        "index.html",
        title=f"{current_user.username}'s Homepage",
        form=form,
        posts=posts,  # type: ignore
        next_url=next_url,
        prev_url=prev_url,
    )


@app.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    """Login page view function"""
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
        # If user attempts to access a page for which @login_required, get the value of `next` from the HTTP request and generate the redirect URL, otherwise redirect to homepage
        next_page: Optional[str] = request.args.get(key="next")
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
    """Registration page view function"""
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


@app.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request() -> Union[str, Response]:
    if current_user.is_authenticated:
        # If the user is logged in, redirect to homepage
        return redirect(url_for("index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        # If reset password form is submitted and passes validation, send password resent email, flash message and redirect to login page
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash("Check your email for instructions on resetting your password")
        return redirect(url_for("login"))
    return render_template(
        "reset_password_request.html", title="Reset Password", form=form
    )


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        redirect(url_for("index"))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset")
        return redirect(url_for("login"))
    return render_template("reset_password.html", form=form)


@app.route("/user/<username>")
@login_required
def user(username: str) -> str:
    """User profile view function."""
    user: User = User.query.filter_by(username=username).first_or_404()
    page = request.args.get(key="page", default=1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False
    )
    next_url = (
        url_for("user", username=user.username, page=posts.next_num)
        if posts.has_next
        else None
    )
    prev_url = (
        url_for("user", username=user.username, page=posts.prev_num)
        if posts.has_prev
        else None
    )
    form = EmptyForm()
    return render_template(
        "user.html",
        user=user,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
        form=form,
        title=f"{user.username}'s Profile",
    )


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile() -> Union[str, Response]:
    """Edit profile page view function"""
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


@app.route("/follow/<username>", methods=["POST"])
@login_required
def follow(username: str) -> Response:
    """Follow user view function"""
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f"User {username} not found")
            return redirect(url_for("index"))
        if user == current_user:
            flash("You cannot follow yourself")
            return redirect(url_for("user", username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f"You followed {username}")
        return redirect(url_for("user", username=username))
    else:
        return redirect(url_for("index"))


@app.route("/unfollow/<username>", methods=["POST"])
def unfollow(username: str) -> Response:
    """Unfollow user view function"""
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f"User {username} not found")
            return redirect(url_for("index"))
        if user == current_user:
            flash(f"You cannot unfollow yourself")
            return redirect(url_for("user", username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f"You unfollowed {username}")
        return redirect(url_for("user", username=username))
    else:
        # validate_on_submit will return False if the CSRF token is missing or invalid
        return redirect(url_for("index"))


@app.route("/explore")
@login_required
def explore() -> str:
    page = request.args.get(key="page", default=1, type=int)
    # Get a list of all posts and paginate
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)  # type: ignore
    next_url = url_for("explore", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("explore", page=posts.prev_num) if posts.has_prev else None
    return render_template(
        "index.html",
        title="Explore",
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
    )
