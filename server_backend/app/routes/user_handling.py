import json
from flask import Blueprint, request, jsonify, render_template
from flask_security.utils import hash_password, verify_password
from flask_security import login_user
from security.models import User, db
from werkzeug.security import check_password_hash

bp = Blueprint("user_handling", __name__)
from app import csrf


@bp.route("/api/accounts/register", methods=["POST"])
@csrf.exempt
def register():
    # Retrieve raw JSON data from the request body
    json_data = request.data.decode("utf-8")

    # Parse the JSON data
    try:
        session_data = json.loads(json_data)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400

    email = session_data.get("email")
    input_password = session_data.get("password")

    if not email or not input_password:
        return jsonify({"error": "Email and password are required"}), 400

    # Check if the user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    # Create the new user
    hashed_password = hash_password(input_password)
    print("input password: " + input_password)
    print("hashed password: " + hashed_password)
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@bp.route("/api/accounts/login", methods=["POST"])
@csrf.exempt
def login():
    # Ensure CSRF protection is checked
    # csrf_token = request.headers.get("X-CSRF-TOKEN")
    # if not csrf_token:
    #     return jsonify({"error": "CSRF token is missing"}), 400

    # Verify the CSRF token here (if necessary, depending on how you're handling it)
    # If you're using Flask-Security, CSRF protection is automatically managed

    json_data = request.data.decode("utf-8")  # Use request.data instead of request.form
    try:
        session_data = json.loads(json_data)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400

    email = session_data.get("email")
    password = session_data.get("password")

    # Debugging log
    print(f"Login attempt for email: {email}")

    # Find the user by email
    user = User.query.filter_by(email=email).first()

    # Ensure user exists before verifying password
    if not user:
        print("User not found")
        return jsonify({"error": "User not found"}), 401
    # if not check_password_hash(user.password, password):
    #     print("no good")

    if not verify_password(password, user.password):
        print("Password mismatch")
        print(password)
        print(user.password)
        return jsonify({"error": "Invalid password"}), 401

    # Log in the user
    login_user(user)
    print("Login successful")

    # Optionally, return the CSRF token in the response (so the client can store it)
    return jsonify({"message": "Login successful"}), 200
