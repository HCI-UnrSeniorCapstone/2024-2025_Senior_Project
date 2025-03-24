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
from dotenv import load_dotenv
import os

mysql = MySQL()
db = SQLAlchemy()  # Only for user tracking via Flask-Security


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
    app.config["SECURITY_PASSWORD_SALT"] = os.getenv("SECRET_PASSWORD_SALT")
    app.config["REMEMBER_COOKIE_SAMESITE"] = "strict"
    app.config["SESSION_COOKIE_SAMESITE"] = "strict"

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
