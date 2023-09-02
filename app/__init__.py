from typing import TYPE_CHECKING
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

# app object instantiated from Flask class
app = Flask(__name__)
app.config.from_object(Config)

login = LoginManager(app)
login.login_view = "login"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Imports at bottom to avoid circular import errors
from app import routes, models
