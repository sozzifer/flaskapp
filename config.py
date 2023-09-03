import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """Config object to hold app configuration options"""

    SECRET_KEY: str = os.environ.get("SECRET_KEY") or "secret_password"
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = ["sozzifer@gmail.com"]

"""To configure a Gmail email server, set the following environmental variables:
export MAIL_SERVER=smtp.googlemail.com
export MAIL_PORT=587
export MAIL_USE_TLS=1
export MAIL_USERNAME=<your-gmail-username>
export MAIL_PASSWORD=<your-gmail-password>
"""