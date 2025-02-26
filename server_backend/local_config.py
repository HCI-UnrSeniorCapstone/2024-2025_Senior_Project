import os

# Dba config 
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '12345678'),
    'database': os.environ.get('DB_NAME', 'fulcrum_analytics')
}

# Flask settings
DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_for_development_only')
PORT = int(os.environ.get('PORT', 5000))

# CORS settings
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8080',  # Vue.js dev server
    'http://localhost:5173',  # Vite dev server
    'http://127.0.0.1:8080',
    'http://127.0.0.1:5173'
]

# Analytics settings
CACHE_TIMEOUT = 300  # Cache timeout in seconds (5 minutes)
MAX_PARTICIPANTS_PER_PAGE = 50
DEFAULT_DATE_RANGE = 30  # Default date range for charts (in days)