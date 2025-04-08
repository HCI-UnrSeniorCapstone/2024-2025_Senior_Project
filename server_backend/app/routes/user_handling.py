import json
from flask import Blueprint, request, jsonify, render_template
from flask_security.utils import hash_password, verify_password
from flask_security import login_user
from security.models import User, db
from werkzeug.security import check_password_hash
from flask import session

bp = Blueprint("user_handling", __name__)
from app import csrf


@bp.route("/api/accounts/register", methods=["POST"])
@csrf.exempt
def register():
    try:
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
    except Exception as e:
        # Error message
        error_type = type(e).__name__
        error_message = str(e)

        # 500 means internal error, AKA the database probably broke
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


# @bp.after_request
# def after_request(response):
#     print("SDFLKSDJFLSKDJF")
#     # Generate CSRF token
#     csrf_token = csrf.generate_csrf()

#     # Set CSRF token as a cookie (accessible to JavaScript)
#     response.set_cookie("XSRF-TOKEN", csrf_token, httponly=False, samesite="Strict")

#     return response


from flask_wtf.csrf import generate_csrf


# @bp.route("/api/accounts/login", methods=["POST"])
# @csrf.exempt
# def login():
#     try:
#         json_data = request.data.decode("utf-8")
#         session_data = json.loads(json_data)

#         email = session_data.get("email")
#         password = session_data.get("password")

#         if not email or not password:
#             return jsonify({"error": "Email and password are required"}), 400

#         user = User.query.filter_by(email=email).first()
#         if not user:
#             return jsonify({"error": "User not found"}), 401

#         if not verify_password(password, user.password):
#             return jsonify({"error": "Invalid password"}), 401

#         login_user(user)
#         db.session.commit()
#         session.modified = True

#         # CSRF cookie for frontend
#         response = jsonify({"message": "Login successful"})
#         response.set_cookie(
#             "XSRF-TOKEN",
#             generate_csrf(),
#             httponly=False,
#             secure=False,
#             samesite="None",
#         )

#         return response, 200

#     except json.JSONDecodeError as e:
#         return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400
#     except Exception as e:
#         return (
#             jsonify(
#                 {
#                     "error_type": type(e).__name__,
#                     "error_message": str(e),
#                 }
#             ),
#             500,
#         )
