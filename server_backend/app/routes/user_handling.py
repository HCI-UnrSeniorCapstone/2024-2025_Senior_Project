from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from app import db

bp = Blueprint("user_handling", __name__)


@bp.route("/api/accounts/update_profile_register", methods=["POST"])
@auth_required("token")
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
