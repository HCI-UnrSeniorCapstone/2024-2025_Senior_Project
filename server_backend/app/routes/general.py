from flask import Blueprint, jsonify
from app.utility.db_connection import get_db_connection
from app.routes.studies import get_data

bp = Blueprint('general', __name__)

# Basic ping
@bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "Pong!"})

# Test Database Connection and Fetch Data from 'user' table
@bp.route('/test_db')
def test_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Test query
        cur.execute("SELECT * FROM user")

        # Get all rows
        results = cur.fetchall()

        # Close the cursor
        cur.close()

        return jsonify(results)

    except Exception as e:
        # Error message
        return jsonify({"error": str(e)})