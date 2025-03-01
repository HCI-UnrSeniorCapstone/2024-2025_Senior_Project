from io import BytesIO
import io
import random
import os
import csv
import time
import zipfile
from flask import Blueprint, current_app, request, jsonify, Response, send_file
import json
import pandas as pd
from app.utility.studies import (
    create_study_details,
    create_study_task_factor_details,
    generate_session_data_from_csv,
    get_all_participant_session_csv_files,
    get_all_study_csv_files,
    get_one_csv_file,
    set_available_features,
    get_study_detail,
    zip_csv_files,
)
from app.utility.db_connection import get_db_connection


bp = Blueprint("studies", __name__)


# Gets and saves data from study form page and stores it into a json file. Then uploads data into db
# The query will need to be UPDATED since the user is hardcoded rn
@bp.route("/create_study", methods=["POST"])
def create_study():
    # Get request and convert to json
    submissionData = request.get_json()

    # Formatting display
    json_object = json.dumps(submissionData, indent=4)
    try:
        # Establish DB connection
        conn = get_db_connection()
        cur = conn.cursor()

        study_id = create_study_details(submissionData, conn, cur)
        create_study_task_factor_details(study_id, submissionData, conn, cur)

        # # CREATES NEW USER. THIS MUST BE CHANGED WHEN WE HAVE USER SESSION IDS
        # select_user_query = """
        # SELECT user_id FROM user WHERE first_name = 'TEST' AND last_name = 'TEST' AND email = 'broYrUreadingThis@example.com'
        # """

        # cur.execute(select_user_query)

        # # If None then user doesn't exist
        # existing_user = cur.fetchone()

        # if existing_user:
        #     user_id = existing_user[0]
        # # Make user
        # else:
        #     insert_user_query = """
        #     INSERT INTO user (first_name, last_name, email)
        #     VALUES ('TEST', 'TEST', 'broYrUreadingThis@example.com')
        #     """

        #     cur.execute(insert_user_query)

        # Get new user_id
        user_id = 1

        # Get owner id
        select_study_user_role_type = """
        SELECT study_user_role_type_id FROM study_user_role_type WHERE study_user_role_description = 'Owner'
        """
        cur.execute(select_study_user_role_type)
        result = cur.fetchone()
        study_user_role_type_id = result[0]

        # study_user_role
        insert_study_user_role_query = """
        INSERT INTO study_user_role (user_id, study_id, study_user_role_type_id)
        VALUES (%s, %s, %s)
        """
        cur.execute(
            insert_study_user_role_query, (user_id, study_id, study_user_role_type_id)
        )

        # Commit changes to the database
        conn.commit()

        # Close cursor
        cur.close()
        return jsonify({"message": "Study created successfully"}), 200

    except Exception as e:
        # Error message
        error_type = type(e).__name__
        error_message = str(e)

        # 500 means internal error, AKA the database probably broke
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


@bp.route("/overwrite_study/<int:user_id>/<int:study_id>", methods=["PUT"])
def overwrite_study(user_id, study_id):
    # Get request and convert to json
    submissionData = request.get_json()

    # Formatting display
    json_object = json.dumps(submissionData, indent=4)
    try:
        conn = get_db_connection()
        cur = conn.cursor()

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
                user_id,
                study_id,
            ),
        )
        user_access_exists = cur.fetchone()[0]

        # Error Message
        if user_access_exists == 0:
            # Check if study exists
            check_study_query = """
            SELECT study_id
            FROM study
            WHERE study_id = %s
            """
            cur.execute(check_study_query, (study_id,))
            study_exists = cur.fetchone()[0]

            if study_exists == 0:
                return jsonify({"error": "Study does not exist"}), 404

            return jsonify({"error": "User does not have access to study"}), 404
        print(user_access_exists)
        # Error Message
        if user_access_exists == "Viewer":
            return jsonify({"error": "User may only view this study"}), 404

        elif user_access_exists == "Owner" or user_access_exists == "Editor":

            # If sessions exist, info can't be overwritten
            check_sessions_query = """
            SELECT COUNT(*)
            FROM participant_session
            WHERE study_id = %s 
            """
            cur.execute(check_sessions_query, (study_id,))
            sessions_exist = cur.fetchone()[0]

            # Error Message
            if sessions_exist != 0:
                return (
                    jsonify(
                        {
                            "error": "Sessions already exist, so the study may not be overwritten"
                        }
                    ),
                    404,
                )

            delete_task_query = """
            DELETE 
            FROM task
            WHERE study_id = %s
            """
            cur.execute(delete_task_query, (study_id,))

            delete_factor_query = """
            DELETE 
            FROM factor
            WHERE study_id = %s
            """
            cur.execute(delete_factor_query, (study_id,))

            # Get study_design_type
            cur.execute(
                "SELECT study_design_type_id FROM study_design_type WHERE study_design_type_description = %s",
                (submissionData["studyDesignType"],),
            )
            result = cur.fetchone()
            study_design_type_id = result[0]

            # Update study query
            update_study_query = """
            UPDATE study 
            SET study_name = %s,
                study_description = %s,
                study_design_type_id = %s,
                expected_participants = %s
            WHERE study_id = %s;
            """

            study_name = submissionData["studyName"]
            study_description = submissionData["studyDescription"]
            expected_participants = submissionData["participantCount"]

            # Execute study update
            cur.execute(
                update_study_query,
                (
                    study_name,
                    study_description,
                    study_design_type_id,
                    expected_participants,
                    study_id,
                ),
            )

            # Build up rest of info
            create_study_task_factor_details(study_id, submissionData, conn, cur)

            # Commit the transaction
            conn.commit()
            # Close cursor
            cur.close()

        return jsonify({"message": "Study overwritten successfully"}), 200

    except Exception as e:
        # Error message
        error_type = type(e).__name__
        error_message = str(e)

        # 500 means internal error, AKA the database probably broke
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


@bp.route("/get_study_data/<int:user_id>", methods=["GET"])
def get_study_data(user_id):

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
        cur.execute(check_user_query, (user_id,))
        user_exists = cur.fetchone()[0]

        # Error Message
        if user_exists == 0:
            return jsonify({"error": "User not found"}), 404

        # Select query
        select_user_studies_info_query = """
        SELECT 
            DATE_FORMAT(study.created_at, '%m/%d/%Y') AS 'Date Created',
            study.study_id AS 'Study ID',
            study.study_name AS 'User Study Name',
            study.study_description AS 'Description',
            CONCAT(
                COALESCE(completed_sessions.completed_count, 0), 
                ' / ', 
                study.expected_participants
            ) AS 'Sessions',
            study_user_role_type.study_user_role_description AS 'Role'
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
        WHERE study_user_role.user_id = 1
        """
        # Execute get
        # cur.execute(select_user_studies_info_query, (user_id,))
        cur.execute(select_user_studies_info_query)
        # Get all rows
        results = cur.fetchall()

        # column_names = [desc[0] for desc in cur.description]  # Extract column names

        # Format results as a list of dictionaries
        # json_results = [dict(zip(column_names, row)) for row in results]

        # Close cursor
        cur.close()

        return jsonify(results), 200

    except Exception as e:
        # Error message
        error_type = type(e).__name__
        error_message = str(e)

        # 500 means internal error, AKA the database probably broke
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


# This route is for loading ALL the detail on a single study, essentially rebuilding in reverse of how create_study deconstructs and saves into db
@bp.route("/load_study/<int:study_id>", methods=["GET"])
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
            "studyDescription": study_res[1] or "No study description provided",
            "studyDesignType": study_res[4],
            "participantCount": str(study_res[2]),
            "tasks": [
                {
                    "taskID": task[0],
                    "taskName": task[1],
                    "taskDescription": task[2] or "No task description provided",
                    "taskDirections": task[3] or "No task directions provided",
                    "taskDuration": str(task[4]),
                    "measurementOptions": [],
                }
                for task in task_res
            ],
            "factors": [
                {
                    "factorID": factor[0],
                    "factorName": factor[1],
                    "factorDescription": factor[2] or "No factor description provided",
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
@bp.route("/delete_study/<int:study_id>/<int:user_id>", methods=["POST"])
def delete_study(study_id, user_id):
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
        cur.execute(check_owner_query, (study_id, user_id))
        is_owner = cur.fetchone()[0]

        if is_owner == 0:
            return jsonify({"error": "Only the owner can delete the study"}), 403

        # Proceed with deletion if the user is the owner
        insert_deletion_query = """
        INSERT INTO deleted_study (study_id, deleted_by_user_id)
        VALUES (%s, %s)
        """
        cur.execute(insert_deletion_query, (study_id, user_id))

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


# Saves tracked data to server file system, db will have a file path to the CSVs
@bp.route(
    "/save_session_data_instance/<int:participant_session_id>/<int:study_id>/<int:task_id>/<int:measurement_option_id>/<int:factor_id>",
    methods=["POST"],
)
def save_session_data_instance(
    participant_session_id, study_id, task_id, measurement_option_id, factor_id
):

    # Check if the request contains the file part
    # pretty sure vue has to name is input_csv
    if "input_csv" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["input_csv"]

    # Check if the file is a CSV by its MIME type
    if not file.content_type == "text/csv":
        return jsonify({"error": "Invalid file type. Only CSV files are allowed."}), 400

    try:

        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Base directory for participant results
        base_dir = current_app.config.get("RESULTS_BASE_DIR_PATH")
        # CSV path not included yet
        create_session_data_instance = """
        INSERT INTO session_data_instance(participant_session_id, task_id, measurement_option_id, factor_id)
        VALUES (%s, %s, %s, %s)
        """
        cur.execute(
            create_session_data_instance,
            (
                participant_session_id,
                task_id,
                measurement_option_id,
                factor_id,
            ),
        )

        # Get the session_data_instance_id of the newly inserted study
        session_data_instance_id = cur.lastrowid

        # Construct file path
        full_path = os.path.join(
            base_dir,
            f"{study_id}_study_id",
            f"{participant_session_id}_participant_session_id",
            f"{session_data_instance_id}_session_data_instance_id",
        )

        # Create directory (this will also create parts of the directory that don't exist)
        os.makedirs(full_path, exist_ok=True)

        # Full file path with CSV
        file_path = os.path.join(full_path, f"{session_data_instance_id}.csv")

        # Check if CSV already exists
        # Want to terminate early because we dont want to overwrite study data
        if os.path.exists(file_path):
            return (
                jsonify(
                    {
                        "error_type": "Duplicate session_data_instance",
                        "error_message": "CSV with same name already exists",
                    }
                ),
                500,
            )

        # Save the file to the system (overwrite if exists)
        file.save(file_path)

        # Add pathway for database
        update_path_session_data_instance = """
        UPDATE session_data_instance
        SET csv_results_path = %s
        WHERE session_data_instance_id = %s
        """
        cur.execute(
            update_path_session_data_instance, (file_path, session_data_instance_id)
        )

        # Commit the transaction
        conn.commit()

        # Close cursor
        cur.close()

        return jsonify({"message": "CSV saved successfully"}), 200
    except Exception as e:
        # Error message
        error_type = type(e).__name__
        error_message = str(e)

        # 500 means internal error, AKA the database probably broke
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


# All csv from a participant
@bp.route(
    "/get_all_session_data_instance_from_participant_zip/<int:participant_id>",
    methods=["GET"],
)
def get_all_session_data_instance_from_participant_zip(participant_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        select_participant_session_ids_query = """
            SELECT ps.participant_session_id
            FROM participant_session AS ps
            WHERE ps.participant_id = %s
        """
        cur.execute(select_participant_session_ids_query, (participant_id,))
        id_results = cur.fetchall()

        # Build already-grouped data: list of (group_key, list of (record, size) tuples)
        grouped_data = []
        for result in id_results:
            participant_session_id = result[0]
            csv_records = get_all_participant_session_csv_files(
                participant_session_id, cur
            )
            # Here the group key is a folder name
            grouped_data.append((f"session_{participant_session_id}", csv_records))
        cur.close()

        zip_buffer = zip_csv_files(grouped_data, already_grouped=True, record_offset=0)
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name="participant.zip",
        )
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


# All csv for a participant session
@bp.route(
    "/get_all_session_data_instance_from_participant_session_zip/<int:participant_session_id>",
    methods=["GET"],
)
def get_all_session_data_instance_from_participant_session_zip(participant_session_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get a flat list of (record, size) tuples
        results_with_size = get_all_participant_session_csv_files(
            participant_session_id, cur
        )

        select_participant_session_creation_query = """
            SELECT ps.created_at
            FROM participant_session AS ps 
            WHERE ps.participant_session_id = %s 
        """
        cur.execute(
            select_participant_session_creation_query, (participant_session_id,)
        )
        session_time_stamp = cur.fetchone()[0]
        cur.close()

        zip_buffer = zip_csv_files(results_with_size, group_by=None, record_offset=0)
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{session_time_stamp}_participant_session.zip",
        )
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


# Only 1 specific csv
@bp.route(
    "/get_one_session_data_instance_zip/<int:session_data_instance_id>", methods=["GET"]
)
def get_one_session_data_instance_zip(session_data_instance_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        result = get_one_csv_file(session_data_instance_id, cur)
        cur.close()

        # Wrap the single record in a list as (record, dummy_size)
        zip_buffer = zip_csv_files([(result, 0)], group_by=None, record_offset=0)
        download_name = f"{result[3]}_{result[7]}_{result[5]}.zip"
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=download_name,
        )
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


# All csv for a study
@bp.route("/get_all_session_data_instance_zip/<int:study_id>", methods=["GET"])
def get_all_session_data_instance_zip(study_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        results_with_size = get_all_study_csv_files(study_id, cur)
        select_study_name_query = """
            SELECT s.study_name
            FROM study AS s
            WHERE s.study_id = %s
        """
        cur.execute(select_study_name_query, (study_id,))
        study_name = cur.fetchone()[0]
        cur.close()

        zip_buffer = zip_csv_files(
            results_with_size,
            group_by=lambda record: f"session_{record[1]}",
            already_grouped=False,
            record_offset=1,
        )
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{study_name}.zip",
        )
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


# Gets all CSV data for a study
# Uses streaming
@bp.route("/get_all_session_data_instance/<int:study_id>", methods=["GET"])
def get_all_session_data_instance(study_id):
    try:
        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        results_with_size = get_all_study_csv_files(study_id, cur)

        # Close the cursor after processing
        cur.close()

        # How many rows read per CSV
        chunk_size = 2000
        # Return the response as a streamed response
        return Response(
            generate_session_data_from_csv(results_with_size, chunk_size),
            content_type="application/json",
            status=200,
        )

    except Exception as e:
        # Error handling
        error_type = type(e).__name__
        error_message = str(e)

        return jsonify({"error_type": error_type, "error_message": error_message}), 500


# When a new session is started we must create a participant session instance and retrieve that newly created id for later user inserting data properly
@bp.route("/create_participant_session/<int:study_id>", methods=["POST"])
def create_participant_session(study_id):
    # Get request and convert to json
    submissionData = request.get_json()

    # Formatting display
    json_object = json.dumps(submissionData, indent=5)
    try:
        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Get gender_type
        cur.execute(
            "SELECT gender_type_id FROM gender_type WHERE gender_description = %s",
            (submissionData["participantGender"],),
        )
        result = cur.fetchone()
        gender_type_id = result[0]

        # Get highest_education_type
        cur.execute(
            "SELECT highest_education_type_id FROM highest_education_type WHERE highest_education_description = %s",
            (submissionData["participantEducationLv"],),
        )
        result = cur.fetchone()
        highest_education_type_id = result[0]

        # Insert participant data into the participant table
        insert_participant_query = """
        INSERT INTO participant (age, gender_type_id, highest_education_type_id, technology_competence)
        VALUES (%s, %s, %s, %s)
        """
        cur.execute(
            insert_participant_query,
            (
                submissionData["participantAge"],
                gender_type_id,
                highest_education_type_id,
                submissionData["participantTechCompetency"],
            ),
        )

        # id of the participant just created
        participant_id = cur.lastrowid

        race_ethnicities = submissionData.get("participantRaceEthnicity", [])
        for ethnicity in race_ethnicities:
            # Get ethnicity_type
            cur.execute(
                "SELECT ethnicity_type_id FROM ethnicity_type WHERE ethnicity_description = %s",
                (ethnicity,),
            )
            result = cur.fetchone()
            ethnicity_type_id = result[0]

            # Update intersection table
            insert_participant_ethnicity_query = """
            INSERT INTO participant_ethnicity(participant_id, ethnicity_type_id)
            VALUES (%s, %s)
            """

            cur.execute(
                insert_participant_ethnicity_query,
                (
                    participant_id,
                    ethnicity_type_id,
                ),
            )

        # Insert participant session data into the participant_session table
        insert_into_participant_session = """
        INSERT INTO participant_session (participant_id, study_id)
        VALUES (%s, %s)
        """
        cur.execute(insert_into_participant_session, (participant_id, study_id))

        # session id needed back on the vue side to pass to local script so we can save csv data properly
        participant_session_id = cur.lastrowid

        # Commit changes to the database
        conn.commit()
        cur.close()

        return jsonify({"participant_session_id": participant_session_id}), 201

    except Exception as e:
        conn.rollback()

        # Error message
        error_type = type(e).__name__
        error_message = str(e)

        # 500 means internal error, AKA the database probably broke
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


# Get session general info for study panel
@bp.route("/get_all_session_info/<int:study_id>", methods=["GET"])
def get_all_session_info(study_id):
    try:
        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        select_session_info_query = """
        SELECT participant_session_id,
        ROW_NUMBER() OVER (ORDER BY created_at) AS 'Session Name',
        created_at AS 'Date Conducted',
        CASE
            WHEN is_valid = 1 THEN 'Valid'
            WHEN is_valid = 0 THEN 'Invalid'
        END AS 'Status',
        IFNULL(comments, '') AS 'Comments',  -- If comments is null, return an empty string
        IFNULL(ended_at, 'N/A') AS 'Ended At'  -- If ended_at is null, return 'N/A'
        FROM participant_session
        WHERE study_id = %s
        """

        cur.execute(select_session_info_query, (study_id,))

        results = cur.fetchall()

        return jsonify(results), 200
    except Exception as e:
        # Error message
        error_type = type(e).__name__
        error_message = str(e)

        # 500 means internal error, AKA the database probably broke
        return jsonify({"error_type": error_type, "error_message": error_message}), 500


# Gets CSV data for 1 participant_session with corresponding types
# Note: this does not use BATCHING or anything for data transfer optimization. This is for DEMO so don't feed in a lot of data
@bp.route(
    "/get_participant_session_data/<int:study_id>/<int:participant_session_id>",
    methods=["GET"],
)
def get_participant_session_data(study_id, participant_session_id):
    try:
        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        select_participant_session_data_query = """
        SELECT sdi.session_data_instance_id, sdi.csv_results_path, sdi.measurement_option_id, sdi.task_id, sdi.factor_id
        FROM session_data_instance sdi
        JOIN participant_session ps
        ON ps.participant_session_id = sdi.participant_session_id
        WHERE ps.study_id = %s AND ps.participant_session_id = %s
        """

        cur.execute(
            select_participant_session_data_query, (study_id, participant_session_id)
        )

        results = cur.fetchall()

        if not results:
            return (
                jsonify(
                    {
                        "error": "No data found for the given study_id and participant_session_id."
                    }
                ),
                404,
            )

        df_dict = {}
        measurement_option_dict = {}
        task_dict = {}
        factor_dict = {}

        for result in results:
            # Convert CSV to dataframe
            df = pd.read_csv(result[1])

            # Convert DataFrame to a list of lists (each row is a list)
            df_list = df.values.tolist()

            # Add dataframe JSON to dictionary
            df_dict[result[0]] = df_list

            select_measurment_option_description_query = """
            SELECT measurement_option_name
            FROM measurement_option
            WHERE measurement_option_id = %s
            """

            cur.execute(select_measurment_option_description_query, (result[2],))
            option_name = cur.fetchone()

            if option_name:
                measurement_option_dict[result[0]] = option_name[0]
            else:
                measurement_option_dict[result[0]] = None

            # task dict based upon same id as everything else for key
            task_dict[result[0]] = result[3]

            # factor dict based upon same id as everything else for key
            factor_dict[result[0]] = result[4]
        cur.close()

        # Create the response body with both dictionaries
        response = {
            "df_dict": df_dict,
            "measurement_option_dict": measurement_option_dict,
            "task_dict": task_dict,
            "factor_dict": factor_dict,
        }
        return jsonify(response), 200

    except Exception as e:
        # Error message
        error_type = type(e).__name__
        error_message = str(e)

        return jsonify({"error_type": error_type, "error_message": error_message}), 500
