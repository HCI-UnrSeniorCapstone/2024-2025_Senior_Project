import os
from flask import Blueprint, current_app, jsonify, send_file
from app.utility.db_connection import get_db_connection
from flask_security import auth_required

bp = Blueprint("downloads", __name__)


# Retrieve tracking tool ZIP (update later to distinguish between OS and versioning if needed)
@bp.route("/api/download_tracking_tool", methods=["POST"])
@auth_required()
def download_tracking_tool():
    try:
        base_path = "/home/hci/Documents/tracking_tool_downloads"
        filename = "FulcrumTrackingTool.zip"
        full_path = os.path.join(base_path, filename)

        if not os.path.exists(full_path):
            return jsonify({"error": "Tracking tool not found."}), 404

        return send_file(
            full_path,
            as_attachment=True,
            download_name=filename,
            mimetype="application/zip",
        )

    except Exception as e:
        print(f"Error sending tracking tool: {e}")
        return jsonify({"error_type": type(e).__name__, "error_message": str(e)}), 500
