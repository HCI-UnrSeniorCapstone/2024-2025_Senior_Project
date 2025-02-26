import os
from flask import Blueprint, jsonify
from app.utility.db_connection import get_db_connection

bp = Blueprint("testing_reset_db", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory of the test file

# Go up one level to reach the root folder, then navigate to sql_database
CREATE_TABLES_SQL = os.path.join(BASE_DIR, "../../../sql_database", "create_tables.sql")
INSERT_DATA_SQL = os.path.join(
    BASE_DIR, "../../../sql_database/sample_data", "insert_all.sql"
)


def run_sql_file(cursor, file_path):
    with open(file_path, "r") as file:
        sql_statements = file.read()

    try:
        cursor.execute(sql_statements)
    except Exception as e:
        print(f"Error executing SQL file: {file_path}\n{e}")


@bp.route("/testing_reset_db", methods=["POST"])
def testing_reset_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check right database
        check_db_query = """SELECT DATABASE()"""
        cur.execute(check_db_query)

        current_db = cur.fetchone()[0]

        # Only works when __init__.py for create_app is in testing mode
        if current_db == "test_db":
            # Drop and recreate the test_db
            cur.execute("DROP DATABASE IF EXISTS test_db;")
            cur.execute("CREATE DATABASE test_db;")
            cur.execute("USE test_db;")  # Switch to test_db

            run_sql_file(cur, CREATE_TABLES_SQL)
            run_sql_file(cur, INSERT_DATA_SQL)

            conn.commit()

            return jsonify({"message": "test_db has been reset!"}), 200
        else:
            return jsonify({"error": "Current database is NOT the test database"}), 400

    except Exception as e:
        # Error message
        error_type = type(e).__name__
        error_message = str(e)

        # Return error response
        return (
            jsonify({"error_type": error_type, "error_message": error_message}),
            500,
        )
