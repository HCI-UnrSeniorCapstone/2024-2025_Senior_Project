# NOTE: THIS USES GUNICORN FOR PRODUCTION MODE
import os
from app import create_app

env = os.getenv("FLASK_ENV", "production")
app = create_app(env)  # Production mode
