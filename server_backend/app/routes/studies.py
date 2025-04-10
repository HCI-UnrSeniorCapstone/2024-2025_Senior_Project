import base64
from io import BytesIO
import os

import requests
from flask import Blueprint, current_app, request, jsonify, Response, send_file
import json
import pandas as pd
from app.utility.studies import (
    create_study_data,
    create_study_details,
    create_study_task_factor_details,
    save_study_consent_form,
    remove_study_consent_form,
    get_all_study_data_helper,
)
from app.utility.db_connection import get_db_connection
from app import create_app
from flask_security import auth_required
from flask_login import current_user


bp = Blueprint("studies", __name__)


# Gets and saves data from study form page and stores it into a json file. Then uploads data into db
@bp.route("/api/create_study", methods=["POST"])
@auth_required()
def create_study():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get JSON data from the request body
        submission_data = request.get_json()

        if not submission_data:
            return jsonify({"error": "Missing JSON body"}), 400

        study_id = create_study_data(submission_data, current_user.id, cur)

        # Handle consent file (optional)
        base_dir = current_app.config.get("RESULTS_BASE_DIR_PATH")
        if "consentFile" in submission_data:
            file = submission_data["consentFile"]
            save_study_consent_form(study_id, file, cur, base_dir)
        conn.commit()
        return (
            jsonify({"message": "Study created successfully", "study_id": study_id}),
            200,
        )

    except Exception as e:
        if "conn" in locals():
            conn.rollback()

        error_type = type(e).__name__
        error_message = str(e)
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


@bp.route("/api/is_overwrite_study_allowed", methods=["POST"])
@auth_required()
def is_overwrite_study_allowed():
    # Get JSON data
    submission_data = request.get_json()

    if not submission_data or "studyID" not in submission_data:
        return jsonify({"error": "Missing studyID in request body"}), 400

    study_id = submission_data["studyID"]
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the user exists
        check_user_query = """
        SELECT COUNT(*) 
        FROM user 
        WHERE user_id = %s
        """
        cur.execute(check_user_query, (current_user.id,))
        user_exists = cur.fetchone()[0]

        # Error Message
        if user_exists == 0:
            return jsonify({"error": "User not found"}), 404

        # Check if user has access
        check_user_query = """
        SELECT study_user_role_description 
        FROM study_user_role sur
        INNER JOIN study_user_role_type surt
        ON surt.study_user_role_type_id = sur.study_user_role_type_id
        WHERE user_id = %s AND study_id = %s
        """
        cur.execute(
            check_user_query,
            (
                current_user.id,
                study_id,
            ),
        )
        user_access_exists = cur.fetchone()

        # Error Message
        if user_access_exists is None:
            return jsonify(False), 200
        # Error Message
        if user_access_exists[0] == "Viewer":
            return jsonify(False), 200

        if user_access_exists[0] == "Owner" or user_access_exists[0] == "Editor":
            # If sessions exist, info can't be overwritten
            check_sessions_query = """
            SELECT participant_session_id
            FROM participant_session
            WHERE study_id = %s 
            """
            cur.execute(check_sessions_query, (study_id,))
            sessions_exist = cur.fetchone()

            # Error Message
            if sessions_exist is not None:
                return (
                    jsonify(False),
                    200,
                )
            else:
                return (
                    jsonify(True),
                    200,
                )

    except Exception as e:
        # Error message
        error_type = type(e).__name__
        error_message = str(e)

        # 500 means internal error, AKA the database probably broke
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


@bp.route("/api/overwrite_study", methods=["POST"])
@auth_required()
def overwrite_study():
    submission_data = request.get_json()

    if not submission_data:
        return jsonify({"error": "No study data provided"}), 400

    study_id = submission_data.get("studyID")
    if not study_id:
        return jsonify({"error": "Missing studyID in submission"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if study exists
        cur.execute("SELECT study_id FROM study WHERE study_id = %s", (study_id,))
        if cur.fetchone() is None:
            return jsonify({"error": "Study does not exist"}), 404

        # Check user role
        cur.execute(
            """
            SELECT study_user_role_description 
            FROM study_user_role sur
            INNER JOIN study_user_role_type surt
            ON surt.study_user_role_type_id = sur.study_user_role_type_id
            WHERE user_id = %s AND study_id = %s
        """,
            (current_user.id, study_id),
        )
        role_result = cur.fetchone()

        if role_result is None:
            return jsonify({"error": "User does not have access to study"}), 403
        if role_result[0] == "Viewer":
            return jsonify({"error": "User may only view this study"}), 403

        # Check if sessions exist
        cur.execute(
            "SELECT participant_session_id FROM participant_session WHERE study_id = %s",
            (study_id,),
        )
        if cur.fetchone():
            return (
                jsonify(
                    {
                        "error": "Sessions already exist, so the study may not be overwritten"
                    }
                ),
                400,
            )

        # Delete existing tasks/factors
        cur.execute("DELETE FROM task WHERE study_id = %s", (study_id,))
        cur.execute("DELETE FROM factor WHERE study_id = %s", (study_id,))

        # Resolve study_design_type_id
        cur.execute(
            "SELECT study_design_type_id FROM study_design_type WHERE study_design_type_description = %s",
            (submission_data["studyDesignType"],),
        )
        study_design_type_id = cur.fetchone()[0]

        # Update study core info
        cur.execute(
            """
            UPDATE study 
            SET study_name = %s,
                study_description = %s,
                study_design_type_id = %s,
                expected_participants = %s
            WHERE study_id = %s
        """,
            (
                submission_data["studyName"],
                submission_data["studyDescription"],
                study_design_type_id,
                submission_data["participantCount"],
                study_id,
            ),
        )

        # Recreate task/factor entries
        create_study_task_factor_details(study_id, submission_data, cur)

        # Handle consent file (optional)
        base_dir = current_app.config.get("RESULTS_BASE_DIR_PATH")
        if "consentFile" in submission_data:
            file = submission_data["consentFile"]
            save_study_consent_form(study_id, file, cur, base_dir)
        else:
            # No file present → remove existing file
            remove_study_consent_form(study_id, cur)

        conn.commit()
        cur.close()
        return jsonify({"message": "Study overwritten successfully"}), 200

    except Exception as e:
        if "conn" in locals():
            conn.rollback()
        return jsonify({"error_type": type(e).__name__, "error_message": str(e)}), 500


@bp.route("/api/get_study_data", methods=["GET"])
@auth_required()
def get_study_data():
    # https://www.geeksforgeeks.org/read-json-file-using-python/
    # gets the json data from the db
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the user exists
        check_user_query = """
        SELECT COUNT(*) 
        FROM user 
        WHERE user_id = %s
        """
        cur.execute(check_user_query, (current_user.id,))
        user_exists = cur.fetchone()[0]
        # Error Message
        if user_exists == 0:
            return jsonify({"error": "User not found"}), 404

        # Select query
        select_user_studies_info_query = """
        SELECT 
            DATE_FORMAT(study.created_at, '%%m/%%d/%%Y') AS `Date_Created`,
            study.study_id AS `Study_ID`,
            study.study_name AS `User_Study_Name`,
            study.study_description AS `Description`,
            CONCAT(
                COALESCE(completed_sessions.completed_count, 0), 
                ' / ', 
                study.expected_participants
            ) AS `Sessions`,
            study_user_role_type.study_user_role_description AS `Role`
        FROM study
        INNER JOIN study_user_role
            ON study_user_role.study_id = study.study_id
        INNER JOIN study_user_role_type
            ON study_user_role.study_user_role_type_id = study_user_role_type.study_user_role_type_id
        LEFT JOIN (
            SELECT 
                study_id, 
                COUNT(*) AS completed_count
            FROM participant_session
            GROUP BY study_id
        ) AS completed_sessions
            ON study.study_id = completed_sessions.study_id
        WHERE study_user_role.user_id = %s
        """

        cur.execute(select_user_studies_info_query, (current_user.id,))
        # Get all rows
        results = cur.fetchall()
        # Close cursor
        cur.close()

        if not results:
            return jsonify({"message": "No studies found"}), 200

        return jsonify(results), 200

    except Exception as e:
        # Error message
        error_type = type(e).__name__
        error_message = str(e)

        # 500 means internal error, AKA the database probably broke
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


@bp.route("/api/copy_study", methods=["POST"])
@auth_required()
def copy_study():
    # Get JSON data from the request body
    submission_data = request.get_json()

    if not submission_data or "studyID" not in submission_data:
        return jsonify({"error": "Missing studyID in request body"}), 400

    study_id = submission_data["studyID"]
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if study exists
        check_study_query = """
        SELECT COUNT(*), study_name
        FROM study
        WHERE study_id = %s
        """
        cur.execute(check_study_query, (study_id,))
        study_results = cur.fetchone()

        if study_results[0] == 0:
            return jsonify({"error": "Study does not exist"}), 404

        # Check if user has access
        check_user_query = """
        SELECT study_user_role_description 
        FROM study_user_role sur
        INNER JOIN study_user_role_type surt
        ON surt.study_user_role_type_id = sur.study_user_role_type_id
        WHERE user_id = %s AND study_id = %s
        """
        cur.execute(
            check_user_query,
            (
                current_user.id,
                study_id,
            ),
        )
        user_access_exists = cur.fetchone()

        # Error Message
        if user_access_exists is None:
            return jsonify({"error": "User does not have access to study"}), 404

        # Get the study data
        study_data = get_all_study_data_helper(study_id)

        # Give new study name
        study_count = study_results[0]
        study_data["studyName"] = study_results[1] + " (" + str(study_count) + ")"

        # Call the helper function to create the new study in the database
        study_id = create_study_data(study_data, current_user.id, cur)

        conn.commit()
        # Return success message
        return (
            jsonify({"message": "Study copied successfully", "study_id": study_id}),
            200,
        )

    except Exception as e:
        if "conn" in locals():
            conn.rollback()

        # Error message
        error_type = type(e).__name__
        error_message = str(e)

        # 500 means internal error, AKA the database probably broke
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


# This route is for loading ALL the detail on a single study, essentially rebuilding in reverse of how create_study deconstructs and saves into db
@bp.route("/api/load_study", methods=["POST"])
@auth_required()
def load_study():
    try:
        # Get the JSON data from the request body
        submission_data = request.get_json()

        if not submission_data or "studyID" not in submission_data:
            return jsonify({"error": "Missing studyID in request body"}), 400

        study_id = submission_data["studyID"]

        # Call the helper function to get the study data
        study_data = get_all_study_data_helper(study_id)

        return jsonify(study_data), 200

    except Exception as e:
        # Error message
        error_type = type(e).__name__
        error_message = str(e)

        return jsonify({"error_type": error_type, "error_message": error_message}), 500


# Note, the study still exists in the database but not available to users
@bp.route("/api/delete_study", methods=["POST"])
@auth_required()
def delete_study():
    try:

        # Get the JSON data from the request body
        submission_data = request.get_json()

        if not submission_data or "studyID" not in submission_data:
            return jsonify({"error": "Missing studyID in request body"}), 400

        study_id = submission_data["studyID"]
        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the user is the owner of the study
        check_owner_query = """
        SELECT COUNT(*)
        FROM study_user_role
        WHERE study_id = %s AND user_id = %s AND study_user_role_type_id = (
            SELECT study_user_role_type_id
            FROM study_user_role_type
            WHERE study_user_role_description = 'Owner'
        )
        """
        cur.execute(check_owner_query, (study_id, current_user.id))
        is_owner = cur.fetchone()[0]

        if is_owner == 0:
            return jsonify({"error": "Only the owner can delete the study"}), 403

        # Proceed with deletion if the user is the owner
        insert_deletion_query = """
        INSERT INTO deleted_study (study_id, deleted_by_user_id)
        VALUES (%s, %s)
        """
        cur.execute(insert_deletion_query, (study_id, current_user.id))

        # Copy study roles into deleted_study_role
        copy_roles_query = """
        INSERT INTO deleted_study_role (study_id, user_id, study_user_role_type_id)
        SELECT study_id, user_id, study_user_role_type_id
        FROM study_user_role
        WHERE study_id = %s
        """
        cur.execute(copy_roles_query, (study_id,))

        # Remove the study from study_user_role to prevent access
        delete_study_roles_query = "DELETE FROM study_user_role WHERE study_id = %s"
        cur.execute(delete_study_roles_query, (study_id,))

        # Commit the transaction
        conn.commit()

        # Close cursor
        cur.close()

        return jsonify({"message": "Study deleted successfully"}), 200

    except Exception as e:
        # Error message
        error_type = type(e).__name__
        error_message = str(e)

        # 500 means internal error, AKA the database probably broke
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


@bp.route("/api/get_study_consent_form", methods=["POST"])
def get_study_consent_form():
    try:
        data = request.get_json()

        # Check if study_id is provided
        if not data or "study_id" not in data:
            return jsonify({"error": "Missing study_id in request body"}), 400

        study_id = data["study_id"]
        conn = get_db_connection()
        cur = conn.cursor()

        consent_form_details_query = """
        SELECT
            file_path,
            original_filename
        FROM consent_form
        WHERE study_id = %s
        """
        cur.execute(consent_form_details_query, (study_id,))
        results = cur.fetchone()
        cur.close()

        # Study never had an assoc consent form which is okay
        if not results:
            return "", 204

        file_path, origin_filename = results

        # Db suggest a consent file should exist but could not retrieve one
        if not os.path.isfile(file_path):
            return jsonify({"error": "Consent form retrieval failed."}), 404

        response = send_file(file_path, mimetype="application/pdf", as_attachment=False)
        response.headers["X-Original-Filename"] = (
            origin_filename  # Need to rename file from filesystem convention to original
        )
        response.headers["Access-Control-Expose-Headers"] = "X-Original-Filename"
        return response

    except Exception as e:
        return jsonify({"error_type": type(e).__name__, "error_message": str(e)}), 500
