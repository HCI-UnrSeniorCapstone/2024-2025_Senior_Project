from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user, logout_user
from app import db
from app.utility.db_connection import get_db_connection

bp = Blueprint("user_handling", __name__)


@bp.route("/api/accounts/get_user_profile_info", methods=["GET"])
@auth_required()
def get_user_profile_info():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
        SELECT email, first_name, last_name, username
        FROM user
        WHERE user_id = %s
        """

        cur.execute(query, (current_user.id,))
        result = cur.fetchone()

        # Close the cursor
        cur.close()

        if result:
            email, first_name, last_name, username = result
            return (
                jsonify(
                    {
                        "email": email,
                        "first_name": first_name,
                        "last_name": last_name,
                        "username": username,
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        # Error message
        return jsonify({"error": str(e)}), 500


@bp.route("/api/accounts/logout", methods=["POST"])
@auth_required()
def logout():
    try:
        logout_user()
        return jsonify({"message": "Logged out successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/accounts/update_profile_register", methods=["POST"])
@auth_required()
def update_profile():
    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    if first_name:
        current_user.first_name = first_name
        print(current_user)
    if last_name:
        current_user.last_name = last_name

    db.session.commit()

    return (
        jsonify(
            {
                "message": "Profile updated",
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
            }
        ),
        200,
    )
