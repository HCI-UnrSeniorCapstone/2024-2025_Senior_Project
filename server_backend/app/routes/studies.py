import base64
from io import BytesIO
import os

import requests
from flask import Blueprint, current_app, request, jsonify, Response, send_file
import json
import pandas as pd
from app.utility.studies import (
    create_study_details,
    create_study_task_factor_details,
    save_study_consent_form,
    remove_study_consent_form,
)
from app.utility.db_connection import get_db_connection
from app import create_app
from flask_security import auth_required
from flask_login import current_user
from werkzeug.utils import secure_filename

bp = Blueprint("studies", __name__)


# Gets and saves data from study form page and stores it into a json file. Then uploads data into db
# The query will need to be UPDATED since the user is hardcoded rn
@bp.route("/api/create_study", methods=["POST"])
@auth_required()
def create_study():
    try:
        submission_data = request.get_json()
        if not submission_data:
            return jsonify({"error": "Missing JSON body"}), 400

        # Establish DB connection
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert study details
        study_id = create_study_details(submission_data, cur)
        create_study_task_factor_details(study_id, submission_data, cur)

        # Get owner role ID
        cur.execute(
            """
            SELECT study_user_role_type_id 
            FROM study_user_role_type 
            WHERE study_user_role_description = 'Owner'
        """
        )
        study_user_role_type_id = cur.fetchone()[0]

        # Assign owner role
        cur.execute(
            """
            INSERT INTO study_user_role (user_id, study_id, study_user_role_type_id)
            VALUES (%s, %s, %s)
        """,
            (current_user.id, study_id, study_user_role_type_id),
        )

        # Save base64-encoded consent file if present
        if "consentFile" in submission_data:
            file_info = submission_data["consentFile"]
            filename = secure_filename(file_info.get("filename"))
            base64_data = file_info.get("content")

            if filename and base64_data:
                file_bytes = base64.b64decode(base64_data)
                base_dir = current_app.config.get("RESULTS_BASE_DIR_PATH")
                full_path = os.path.join(base_dir, "study_consent_forms", str(study_id))

                os.makedirs(full_path, exist_ok=True)
                with open(os.path.join(full_path, filename), "wb") as f:
                    f.write(file_bytes)

                # Optionally store metadata in DB
                # save_study_consent_form_metadata(study_id, filename, cur)

        # Commit and finish
        conn.commit()
        cur.close()
        return (
            jsonify({"message": "Study created successfully", "study_id": study_id}),
            200,
        )

    except Exception as e:
        if "conn" in locals():
            conn.rollback()

        return jsonify({"error_type": type(e).__name__, "error_message": str(e)}), 500


@bp.route("/api/is_overwrite_study_allowed/<int:study_id>", methods=["GET"])
@auth_required()
def is_overwrite_study_allowed(study_id):
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
            consent_file = submission_data["consentFile"]
            filename = secure_filename(consent_file.get("filename", "consent_form.pdf"))
            content = consent_file.get("content")

            if filename and content:
                full_path = os.path.join(base_dir, "study_consent_forms", str(study_id))
                os.makedirs(full_path, exist_ok=True)
                file_path = os.path.join(full_path, filename)

                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(content))

                # save_study_consent_form_metadata(study_id, filename, cur)
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


@bp.route("/api/copy_study/<int:study_id>", methods=["POST"])
@auth_required()
def copy_study(study_id):
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

        url = os.getenv("VUE_APP_BACKEND_URL").strip()
        port = os.getenv("VUE_APP_BACKEND_PORT").strip()
        full_url = f"http://{url}:{port}"

        load_study_url = f"{full_url}/load_study/{study_id}"
        load_response = requests.get(load_study_url)

        if load_response.status_code != 200:
            return {
                "error": "Failed to load study data",
                "status": load_response.status_code,
            }, load_response.status_code

        study_data = load_response.json()

        # Give new study name
        study_count = study_results[0]
        study_data["studyName"] = study_results[1] + " (" + str(study_count) + ")"

        create_study_url = f"{full_url}/create_study/{user_id}"
        create_response = requests.post(create_study_url, json=study_data)
        if create_response.status_code != 200:
            return {
                "error": "Failed to create study data",
                "status": create_response.status_code,
            }, create_response.status_code

        return create_response.json(), 200

    except Exception as e:
        # Error message
        error_type = type(e).__name__
        error_message = str(e)

        # 500 means internal error, AKA the database probably broke
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


# This route is for loading ALL the detail on a single study, essentially rebuilding in reverse of how create_study deconstructs and saves into db
@bp.route("/api/load_study/<int:study_id>", methods=["GET"])
@auth_required()
def load_study(study_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get Study Details
        get_study_info = """
        SELECT
            s.study_name AS 'User Study Name',
            s.study_description AS 'Description',
            s.expected_participants AS '# Expected Participants',
            surt.study_user_role_description AS 'Role',
            sdt.study_design_type_description AS 'Study Design Type'
        FROM study AS s
        INNER JOIN study_user_role AS sur
            ON sur.study_id = s.study_id
        INNER JOIN study_user_role_type AS surt
            ON sur.study_user_role_type_id = surt.study_user_role_type_id
        INNER JOIN study_design_type AS sdt
            ON s.study_design_type_id = sdt.study_design_type_id
        WHERE s.study_id = %s
        """
        cur.execute(get_study_info, (study_id,))
        study_res = cur.fetchone()

        # Get all the tasks under the study
        get_tasks = """
        SELECT
            task_id AS 'Task ID',
            task_name AS 'Task Name',
            task_description AS 'Task Description',
            task_directions AS 'Task Directions',
            duration AS 'Duration'
        FROM task
        WHERE study_id = %s;
        """
        cur.execute(get_tasks, (study_id,))
        task_res = cur.fetchall()

        # Get all the factors under the study
        get_factors = """
        SELECT
            factor_id AS 'Factor ID',
            factor_name AS 'Factor Name',
            factor_description AS 'Factor Description'
        FROM factor
        WHERE study_id = %s;
        
        """
        cur.execute(get_factors, (study_id,))
        factor_res = cur.fetchall()

        # Creating the study obj before adding measurement option info
        study_data = {
            "studyName": study_res[0],
            "studyDescription": study_res[1],
            "studyDesignType": study_res[4],
            "participantCount": str(study_res[2]),
            "tasks": [
                {
                    "taskID": task[0],
                    "taskName": task[1],
                    "taskDescription": task[2],
                    "taskDirections": task[3],
                    "taskDuration": task[4],
                    "measurementOptions": [],
                }
                for task in task_res
            ],
            "factors": [
                {
                    "factorID": factor[0],
                    "factorName": factor[1],
                    "factorDescription": factor[2],
                }
                for factor in factor_res
            ],
        }

        # Get all the measurements under the task under the study
        get_task_measurements = """
        SELECT
            tm.task_id AS 'Task ID',
            mo.measurement_option_name AS 'Measurement Option'
        FROM task_measurement AS tm
        JOIN task AS t
        ON tm.task_id = t.task_id
        JOIN measurement_option AS mo
        ON tm.measurement_option_id = mo.measurement_option_id
        WHERE tm.task_id IN (SELECT task_id FROM task WHERE study_id = %s);
        """
        cur.execute(get_task_measurements, (study_id,))
        measurement_res = cur.fetchall()

        # Use taskID to get the measurement types into the correct task measurement[]
        for task in study_data["tasks"]:
            task["measurementOptions"] = [
                measurement[1]
                for measurement in measurement_res
                if measurement[0] == task["taskID"]
            ]

        cur.close()

        return jsonify(study_data), 200

    except Exception as e:
        # Error message
        error_type = type(e).__name__
        error_message = str(e)

        # 500 means internal error, AKA the database probably broke
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


# Note, the study still exists in the database but not available to users
@bp.route("/api/delete_study/<int:study_id>", methods=["POST"])
@auth_required()
def delete_study(study_id):
    try:
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


@bp.route("/api/get_study_consent_form/<int:study_id>", methods=["GET"])
def get_study_consent_form(study_id):
    try:
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
