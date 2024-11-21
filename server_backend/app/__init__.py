# This file initializes the flask app configuration
from flask import Flask
from flask_cors import CORS
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

mysql = MySQL()

def create_app():
    # Creating app
    app = Flask(__name__)
    app.config.from_object(__name__)
    
    # Load environment variables
    load_dotenv()

    # MYSQL Configuration
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
    app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
    mysql.init_app(app)

    CORS(app, resources={r'/*': {'origins': '*'}})

    # Register blueprints
    from app.routes.general import bp as general_bp
    from app.routes.studies import bp as studies_bp
    from app.routes.db_routes import bp as db_routes_bp
    app.register_blueprint(general_bp)
    app.register_blueprint(studies_bp)
    app.register_blueprint(db_routes_bp)

    return app
