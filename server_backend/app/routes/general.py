import json
from flask import Blueprint, jsonify, request
from app.utility.db_connection import get_db_connection
from flask_security import auth_required

bp = Blueprint("general", __name__)


# Basic ping
@bp.route("/ping", methods=["GET"])
@auth_required("token")
def ping():
    return jsonify({"message": "Pong!"}), 200


# Test Database Connection and Fetch Data from 'user' table
@bp.route("/test_db")
@auth_required("token")
def test_db():
    # Convert all cookies into a dictionary (cookies are stored in request.cookies as a dictionary)
    cookies_dict = request.cookies

    # Convert the cookies dictionary to JSON string (for printing)
    cookies_json = json.dumps(
        cookies_dict, indent=4
    )  # Use indent=4 for pretty formatting

    # Print the JSON formatted cookies
    print("Cookies as JSON:")
    print(cookies_json)
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Test query
        cur.execute("SELECT * FROM user")

        # Get all rows
        results = cur.fetchall()

        # Close the cursor
        cur.close()

        return jsonify(results), 200

    except Exception as e:
        # Error message
        return jsonify({"error": str(e)}), 500
