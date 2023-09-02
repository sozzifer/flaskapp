from datetime import datetime as dt
from hashlib import md5

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login

# UserMixin provides default implementations for: 
#   - is_authenticated
#   - is_active
#   - is_anonymous
#   - get_id()
class User(UserMixin, db.Model): # type: ignore
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(64), index=True, unique=True)
    email: str = db.Column(db.String(120), index=True, unique=True)
    password_hash: str = db.Column(db.String(128))
    about_me: str = db.Column(db.String(140))
    last_seen: dt = db.Column(db.DateTime, default=dt.utcnow)

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def avatar(self, size: int) -> str:
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=monsterid&s={size}"

@login.user_loader
def load_user(id: str) -> User:
    return User.query.get(int(id))


class Post(db.Model):  # type: ignore
    id: int = db.Column(db.Integer, primary_key=True)
    body: str = db.Column(db.String(140))
    timestamp: dt = db.Column(db.DateTime, index=True, default=dt.utcnow)
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"<Post {self.body}>"
