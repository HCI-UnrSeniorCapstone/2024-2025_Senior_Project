import os
from pathlib import Path

# Local SQLite database path
DB_PATH = Path(__file__).parent / "local_database.db"

# Database config for local development
DB_CONFIG = {
    'SQLITE': {
        'path': str(DB_PATH)
    },
    # Keep the original MySQL config for reference
    'MYSQL': {
        'host': 'your_university_host',
        'user': 'your_username',
        'password': 'your_password',
        'database': 'your_database',
        'port': 3306
    }
}

# Flag to determine which database to use
USE_SQLITE = True  # Set to True for local development