import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

# app object instantiated from Flask class
app: Flask = Flask(__name__)
app.config.from_object(Config)

login: LoginManager = LoginManager(app)
login.login_view = "login"  # type: ignore

db: SQLAlchemy = SQLAlchemy(app)
migrate: Migrate = Migrate(app, db)

mail = Mail(app)

# Enable logging if app not in debug mode
if not app.debug:
    if app.config["MAIL_SERVER"]:
        auth = None
        if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
            auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
        secure = None
        if app.config["MAIL_USE_TLS"]:
            secure = ()
        # Create SMTPHandler object to report errors (not warnings, informational or debugging messages), and attach it to the app.logger object
        mail_handler = SMTPHandler(
            mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
            fromaddr="no-reply" + app.config["MAIL_SERVER"],
            toaddrs=app.config["ADMINS"],
            subject="Flask app failure",
            credentials=auth,
            secure=secure,
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    # Set up log file
    if not os.path.exists("logs"):
        os.mkdir("logs")

    # Set max log file size and number of backups to retain
    file_handler = RotatingFileHandler(
        "logs/flaskapp.log", maxBytes=10240, backupCount=10
    )

    # Set file_handler log format and level
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    # Set app log level and server startup message
    app.logger.setLevel(logging.INFO)
    app.logger.info("Flask app startup")

# Imports at bottom to avoid circular import errors
from app import errors, models, routes
