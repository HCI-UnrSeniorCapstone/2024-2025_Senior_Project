# This file initializes the flask app configuration
from flask import Flask
from flask_cors import CORS
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
)
from flask_security.models import fsqla_v3 as fsqla
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from flask_mailman import Mail
from flask_security import MailUtil
import os

mysql = MySQL()
db = SQLAlchemy()  # Only for user tracking via Flask-Security
csrf = CSRFProtect()

# Confirmation email when registering
mail = Mail()


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

    # Import models
    from security.models import User, Role

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    # Customized settings so that VUE can be used instead of default server-side html rendering via Flask Security
    app.config["SECURITY_FLASH_MESSAGES"] = False
    app.config["SECURITY_URL_PREFIX"] = "/api/accounts"

    app.config["SECURITY_RECOVERABLE"] = True
    app.config["SECURITY_TRACKABLE"] = True
    app.config["SECURITY_CHANGEABLE"] = True
    app.config["SECURITY_CONFIRMABLE"] = True
    app.config["SECURITY_REGISTERABLE"] = True
    app.config["SECURITY_UNIFIED_SIGNIN"] = False

    app.config["SECURITY_POST_CONFIRM_VIEW"] = (
        "http://localhost:5173/confirmed"  # Update this when frontend deployed
    )
    app.config["SECURITY_CONFIRM_ERROR_VIEW"] = (
        "http://localhost:5173/confirmed"  # Update this when frontend deployed
    )
    app.config["SECURITY_RESET_VIEW"] = "/reset-password"
    app.config["SECURITY_RESET_ERROR_VIEW"] = "/reset-password-error"
    app.config["SECURITY_LOGIN_ERROR_VIEW"] = "/login-error"
    app.config["SECURITY_POST_OAUTH_LOGIN_VIEW"] = "/post-oauth-login"
    app.config["SECURITY_REDIRECT_BEHAVIOR"] = "spa"

    app.config["SECURITY_CSRF_PROTECT_MECHANISMS"] = ["session", "basic"]
    app.config["SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS"] = True

    app.config["SECURITY_JSON"] = True  # Forces JSON responses instead of HTML
    app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"] = "Authentication-Token"

    app.config["SECURITY_CSRF_COOKIE_NAME"] = "XSRF-TOKEN"
    app.config["WTF_CSRF_CHECK_DEFAULT"] = False
    app.config["WTF_CSRF_TIME_LIMIT"] = None

    app.config["SESSION_TYPE"] = "filesystem"  # Store sessions in the filesystem
    app.config["SESSION_PERMANENT"] = (
        False  # Make session cookies expire when browser closes
    )
    app.config["SESSION_COOKIE_NAME"] = "session"
    app.config["SESSION_COOKIE_HTTPONLY"] = (
        False  # Prevent JavaScript from accessing session cookie
    )
    app.config["SESSION_COOKIE_SECURE"] = (
        False  # Requires HTTPS, change to False for local dev
    )
    app.config["SESSION_COOKIE_SAMESITE"] = (
        "None"  # Adjust if cross-origin issues occur
    )
    csrf.init_app(app)
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "false").lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")
    mail.init_app(app)

    security = Security(app, user_datastore)
    # CSRFProtect(app)
    # csrf = CSRFProtect(app)

    # SQLAlchemy ONLY for Flask-Security
    # This is done since Flask-Security is easy to use when using an ORM
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB').strip()}"
    )
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    CORS(
        app,
        # resources={r"/*": {"origins": "http://localhost:5173"}},
        expose_headers=[
            "Content-Disposition",
            "Content-Type",
            "X-CSRFToken",
            "Authorization",
            "Authentication-Token",
            "XSRF-TOKEN",
        ],
        supports_credentials=True,
    )

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
