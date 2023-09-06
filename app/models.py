from datetime import datetime as dt
from hashlib import md5
import jwt
from time import time
from typing import Any, Callable, List, Optional

from flask_login import UserMixin
from sqlalchemy.orm import RelationshipProperty
from werkzeug.security import check_password_hash, generate_password_hash

from app import app, db, login

# Followers association table
followers = db.Table(
    "followers",
    db.Column("follower_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id")),
)


class User(UserMixin, db.Model):  # type: ignore
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
    """The `User.followed` RelationshipProperty links an instance of `User` to other `User` instances. For two users linked by this relationship, the left side `follower` user follows the right side `followed` users, i.e. the relationship is defined as seen from the left side user. Querying on the `follower` user returns a list of `followed` users.
    """
    followed: RelationshipProperty = db.relationship(
        "User",
        # "User" is the class to be used on the right side of the relationship. The left side is the parent `User` class. Since this is a self-referential relationship, the same class is used on both sides.
        secondary=followers,
        # `secondary` sets `followers` as the association table to be used for this relationship.
        primaryjoin=(followers.c.follower_id == id),
        # `primaryjoin` indicates the condition that links the left side entity (the `follower` user) with the association table. The joining condition for the left side of the relationship is the user ID matching the `follower_id` field in the association table.
        secondaryjoin=(followers.c.followed_id == id),
        # `secondaryjoin` indicates the condition that links the right side entity (the `followed` user) with the association table. The join condition for the right side of the relationship is the user ID matching the `followed_id` field in the association table.
        backref=db.backref("followers", lazy="dynamic"),
        # `backref` defines how this relationship will be accessed from the right side entity. From the left side, the relationship is `followed`, so from the right side `followers` represents all the left side users that are linked to the target right side user.
        lazy="dynamic",
        # `lazy`="dynamic" sets the left side query to run only if specifically requested (see also `backref`).
    )

    """sqlalchemy.exc.ArgumentError: Type annotation for "User.posts" can't be correctly interpreted for Annotated Declarative Table form.  ORM annotations should normally make use of the ``Mapped[]`` generic type, or other ORM-compatible generic type, as a container for the actual type, which indicates the intent that the attribute is mapped. Class variables that are not intended to be mapped by the ORM should use ClassVar[].  To allow Annotated Declarative to disregard legacy annotations which don't use Mapped[] to pass, set "__allow_unmapped__ = True" on the class or a superclass of this class. (Background on this error at: https://sqlalche.me/e/20/zlpr)
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

    def get_reset_password_token(self, expires_in: int = 600) -> str:
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token: str) -> "User":
        try:
            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])[
                "reset_password"
            ]
        except:
            return
        return User.query.get(id)

    def avatar(self, size: int) -> str:
        """Generate user avatar from MD5 hash of user email"""
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=monsterid&s={size}"

    def follow(self, user: "User") -> None:
        """Add `user` to `self.followed`"""
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user: "User") -> None:
        """Remove `user` from `self.followed`"""
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user: "User") -> bool:
        """Return items in the association table with the left side foreign key set to the `self` user, and the right side set to the `user` argument"""
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self) -> List["Post"]:
        """Return posts by users followed by this user, as well as this user's own posts"""
        # Get `followed` posts
        followed_posts = (
            # Join the `Posts` table to the `followers` table on followed_id:Post.user_id
            Post.query.join(followers, (followers.c.followed_id == Post.user_id))
            # Filter the result by `follower.id == self.id` i.e. just the posts for users followed by this user
            .filter(followers.c.follower_id == self.id)
        )
        # Get this user's posts
        my_posts = Post.query.filter_by(user_id=self.id)
        return followed_posts.union(my_posts).order_by(Post.timestamp.desc())  # type: ignore


@login.user_loader
def load_user(id: str) -> Optional[User]:
    """Get User from id"""
    return User.query.get(int(id))


class Post(db.Model):  # type: ignore
    """Post database model"""

    id: int = db.Column(db.Integer, primary_key=True)
    body: str = db.Column(db.String(140))
    timestamp: Callable[[Any], Any] = db.Column(
        db.DateTime, index=True, default=dt.utcnow  # type: ignore
    )
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"<Post {self.body}>"
