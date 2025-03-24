import json
from flask import Blueprint, request, jsonify
from flask_security.utils import hash_password
from security.models import User, db

bp = Blueprint("user_handling", __name__)


@bp.route("/register", methods=["POST"])
def register():
    json_data = request.form.get("json")
    # Parse the JSON
    try:
        session_data = json.loads(json_data)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400
    email = session_data.get("email")
    password = session_data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    new_user = User(email=email, password=hash_password(password))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201
