import mysql.connector
import pytest
import sys
import os

from app import create_app

# Path to your SQL files
CREATE_TABLES_SQL = "/path/to/create_tables.sql"
INSERT_DATA_SQL = "/path/to/insert_all.sql"


# Fixture for creating and dropping the test database
@pytest.fixture(scope="function")
def mysql_database():
    # Create Flask app context with test-specific configuration
    app = create_app()

    # Override config values to use test database
    app.config["MYSQL_DB"] = "test_db"

    # Establish connection to MySQL server using the test DB configuration
    conn = mysql.connector.connect(
        host=app.config["MYSQL_HOST"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
    )

    cursor = conn.cursor()

    # Create a new test database for testing
    cursor.execute("CREATE DATABASE IF NOT EXISTS test_db")
    cursor.execute("USE test_db")

    # Run the SQL files to create tables and insert fake data
    with open(CREATE_TABLES_SQL, "r") as f:
        cursor.execute(f.read(), multi=True)

    with open(INSERT_DATA_SQL, "r") as f:
        cursor.execute(f.read(), multi=True)

    # Commit the changes
    conn.commit()

    # Yield the connection to tests
    yield conn

    # Teardown - Drop the test database after tests
    cursor.execute("DROP DATABASE test_db")
    conn.commit()

    cursor.close()
    conn.close()
