import os
import mysql.connector
import pytest

from app import create_app
from app.utility.db_connection import get_db_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory of the test file

# Go up one level to reach the root folder, then navigate to sql_database
DROP_TABLES_SQL = os.path.join(BASE_DIR, "../../sql_database", "drop_tables.sql")
CREATE_TABLES_SQL = os.path.join(BASE_DIR, "../../sql_database", "create_tables.sql")
INSERT_DATA_SQL = os.path.join(
    BASE_DIR, "../../sql_database/sample_data", "insert_all.sql"
)


def run_sql_file(cursor, file_path):
    """Helper function to run SQL commands from a file."""
    with open(file_path, "r") as file:
        sql_statements = file.read()

        # Split statements by semicolon, but ignore DELIMITER lines
        statements = sql_statements.split(";")

        for statement in statements:
            clean_stmt = statement.strip()
            if clean_stmt and not clean_stmt.startswith("DELIMITER"):
                try:
                    cursor.execute(clean_stmt)
                except Exception as e:
                    print(f"Error executing statement: {clean_stmt}\n{e}")


@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def reset_db(app):
    """
    Drops tables, recreates them, and inserts sample data before each test.
    """
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()

        # Run SQL files
        run_sql_file(cursor, DROP_TABLES_SQL)
        run_sql_file(cursor, CREATE_TABLES_SQL)
        run_sql_file(cursor, INSERT_DATA_SQL)

        # Commit changes
        conn.commit()
        cursor.close()


# @pytest.fixture(scope="function")
# def mysql_database():
#     # Now create the app with test mode
#     app = create_app(testing=True)

#     with app.app_context():
#         conn = get_db_connection()
#         cur = conn.cursor()

#         # Use the test database
#         cur.execute("USE test_db")

#         # Populate tables and seed data
#         with open(CREATE_TABLES_SQL, "r") as f:
#             cur.execute(f.read(), multi=True)

#         with open(INSERT_DATA_SQL, "r") as f:
#             cur.execute(f.read(), multi=True)

#         conn.commit()
#         yield conn

#         # Teardown: drop the test database
#         cur.execute("DROP DATABASE IF EXISTS test_db")
#         conn.commit()
#         cur.close()
#         conn.close()
