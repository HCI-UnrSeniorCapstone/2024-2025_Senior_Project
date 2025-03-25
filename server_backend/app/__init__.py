# This file initializes the flask app configuration
from flask import Flask
from flask_cors import CORS
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
    auth_required,
    hash_password,
)
from flask_security.models import fsqla_v3 as fsqla
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os

mysql = MySQL()
db = SQLAlchemy()  # Only for user tracking via Flask-Security
csrf = CSRFProtect()


def create_app(testing=False):
    # Creating app
    app = Flask(__name__)
    app.config.from_object(__name__)

    # Load environment variables
    load_dotenv()

    # MYSQL Configuration
    app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST")
    app.config["MYSQL_USER"] = os.getenv("MYSQL_USER")
    app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD")
    app.config["VUE_APP_BACKEND_URL"] = os.getenv("VUE_APP_BACKEND_URL")
    app.config["VUE_APP_BACKEND_PORT"] = os.getenv("VUE_APP_BACKEND_PORT")
    if testing:
        app.config["MYSQL_DB"] = "test_db"
    else:
        app.config["MYSQL_DB"] = os.getenv("MYSQL_DB").strip()
    mysql.init_app(app)

    # Server CSV pathway configuration
    app.config["RESULTS_BASE_DIR_PATH"] = os.getenv("RESULTS_BASE_DIR_PATH")

    # Flask-Security configs
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    # app.config["SECURITY_PASSWORD_HASH"] = "argon2"
    app.config["SECURITY_PASSWORD_SALT"] = os.getenv("SECRET_PASSWORD_SALT")
    app.config["REMEMBER_COOKIE_SAMESITE"] = "strict"
    app.config["SESSION_COOKIE_SAMESITE"] = "strict"

    # Customized settings so that VUE can be used instead of default server-side html rendering via Flask Security
    SECURITY_FLASH_MESSAGES = False
    SECURITY_URL_PREFIX = "/api/accounts"

    SECURITY_RECOVERABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_CONFIRMABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_UNIFIED_SIGNIN = True

    SECURITY_POST_CONFIRM_VIEW = "/confirmed"
    SECURITY_CONFIRM_ERROR_VIEW = "/confirm-error"
    SECURITY_RESET_VIEW = "/reset-password"
    SECURITY_RESET_ERROR_VIEW = "/reset-password-error"
    SECURITY_LOGIN_ERROR_VIEW = "/login-error"
    SECURITY_POST_OAUTH_LOGIN_VIEW = "/post-oauth-login"
    SECURITY_REDIRECT_BEHAVIOR = "spa"

    SECURITY_CSRF_PROTECT_MECHANISMS = ["session", "basic"]
    SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS = True

    SECURITY_CSRF_COOKIE_NAME = "XSRF-TOKEN"
    WTF_CSRF_CHECK_DEFAULT = False
    WTF_CSRF_TIME_LIMIT = None
    csrf.init_app(app)
    # CSRFProtect(app)

    # SQLAlchemy ONLY for Flask-Security
    # This is done since Flask-Security is easy to use when using an ORM
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB').strip()}"
    )
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    CORS(
        app, resources={r"/*": {"origins": "*"}}, expose_headers=["Content-Disposition"]
    )
    # Import models
    from security.models import User, Role

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    # Register blueprints
    from app.routes.general import bp as general_bp
    from app.routes.studies import bp as studies_bp
    from app.routes.sessions import bp as sessions_bp
    from app.routes.testing_reset_db import bp as testing_reset_db_bp
    from app.routes.user_handling import bp as user_handling_bp

    app.register_blueprint(general_bp)
    app.register_blueprint(studies_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(testing_reset_db_bp)
    app.register_blueprint(user_handling_bp)

    return app
