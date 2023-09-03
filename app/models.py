from datetime import datetime as dt
from hashlib import md5
from typing import Optional

from flask_login import UserMixin
from sqlalchemy.orm import RelationshipProperty
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login

# Followers association table
followers = db.Table(
    "followers",
    db.Column("follower_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id")),
)


class User(UserMixin, db.Model):
    """User database model.

    UserMixin class provides default implementations for:
     - is_authenticated
     - is_active
     - is_anonymous
     - get_id()
    """

    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(64), index=True, unique=True)
    email: str = db.Column(db.String(120), index=True, unique=True)
    password_hash: str = db.Column(db.String(128))
    about_me: str = db.Column(db.String(140))
    last_seen: dt = db.Column(db.DateTime, default=dt.utcnow)
    posts: RelationshipProperty = db.relationship(
        "Post", backref="author", lazy="dynamic"
    )
    """The `followed` RelationshipProperty links a `User` instance to other `User` instances. For two `User`s linked by this relationship, the left-hand `User` follows the right-hand `User`, i.e. the relationship is defined as seen from the left-hand `User`. Querying on the left-hand side returns the list of `User`s followed by `self.User`.
    """
    followed: RelationshipProperty = db.relationship(
        # "User" is the class to be used on the right-hand side of the relationship. The left-hand side is the parent `User` class. Since this is a self-referential relationship, the same class is used on both sides.
        "User",
        # `secondary` sets `followers` as the association table to be used for this relationship.
        secondary=followers,
        # `primaryjoin` indicates the condition that links the left side entity (the `follower` user) with the association table. The join condition for the left side of the relationship is the user ID matching the `follower_id` field in the association table.
        primaryjoin=(followers.c.follower_id == id),
        # `secondaryjoin` indicates the condition that links the right side entity (the `followed` user) with the association table. The join condition for the right side of the relationship is the user ID matching the `followed_id` field in the association table.
        secondaryjoin=(followers.c.followed_id == id),
        # `backref` defines how this relationship will be accessed from the right side entity. From the left side, the relationship is `followed`, so from the right side `followers` represents all the left side users that are linked to the target right side user. `lazy`="dynamic" sets the right side query to run only if specifically requested.
        backref=db.backref("followers", lazy="dynamic"),
        # `lazy`="dynamic" sets the left side query to run only if specifically requested.
        lazy="dynamic",
    )

    """sqlalchemy.exc.ArgumentError: Type annotation for "User.posts" can't be correctly interpreted for Annotated Declarative Table form.  ORM annotations should normally make use of the ``Mapped[]`` generic type, or other ORM-compatible generic type, as a container for the actual type, which indicates the intent that the attribute is mapped. Class variables that are not intended to be mapped by the ORM should use ClassVar[].  To allow Annotated Declarative to disregard legacy annotations which don't use Mapped[] to pass, set "__allow_unmapped__ = True" on the class or a superclass this class. (Background on this error at: https://sqlalche.me/e/20/zlpr)
    """
    __allow_unmapped__ = True

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password: str) -> None:
        """Create password_hash from user-provided password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Compare password_hash to user-provided password and return boolean."""
        return check_password_hash(self.password_hash, password)

    def avatar(self, size: int) -> str:
        """Generate user avatar from MD5 hash of user email"""
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=monsterid&s={size}"


@login.user_loader
def load_user(id: str) -> Optional[User]:
    """Get User from id"""
    return User.query.get(int(id))


class Post(db.Model):  # type: ignore
    """Post database model"""

    id: int = db.Column(db.Integer, primary_key=True)
    body: str = db.Column(db.String(140))
    timestamp: dt = db.Column(db.DateTime, index=True, default=dt.utcnow)
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"<Post {self.body}>"
