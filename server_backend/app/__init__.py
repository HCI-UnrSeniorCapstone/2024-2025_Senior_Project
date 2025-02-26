# This file initializes the flask app configuration
from flask import Flask
from flask_cors import CORS
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

mysql = MySQL()


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
    if testing:
        app.config["MYSQL_DB"] = "test_db"
    else:
        app.config["MYSQL_DB"] = os.getenv("MYSQL_DB").strip()
    mysql.init_app(app)

    # Server CSV pathway configuration
    app.config["RESULTS_BASE_DIR_PATH"] = os.getenv("RESULTS_BASE_DIR_PATH")

    CORS(app, resources={r"/*": {"origins": "*"}})

    # Register blueprints
    from app.routes.general import bp as general_bp
    from app.routes.studies import bp as studies_bp
    from app.routes.sessions import bp as sessions_bp

    app.register_blueprint(general_bp)
    app.register_blueprint(studies_bp)
    app.register_blueprint(sessions_bp)

    return app
