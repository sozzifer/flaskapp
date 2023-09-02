import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """Config object to hold app configuration options"""
    SECRET_KEY:str = os.environ.get("SECRET_KEY") or "secret_password"
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
