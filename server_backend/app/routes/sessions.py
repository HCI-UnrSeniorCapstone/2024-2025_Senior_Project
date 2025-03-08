import io
import os
import json
import tempfile
import zipfile
from flask import Blueprint, current_app, request, jsonify, Response, send_file
from app.utility.sessions import (
    get_all_participant_csv_files,
    get_all_participant_session_csv_files,
    get_all_study_csv_files,
    get_file_name_for_folder,
    get_one_csv_file,
    get_one_trial,
    get_participant_name_for_folder,
    get_participant_session_name_for_folder,
    get_trial_order_for_folder,
    get_zip,
    parse_file_path,
)
from app.utility.db_connection import get_db_connection

bp = Blueprint("sessions", __name__)


# Test endpoint for receiving the session zip results from the local script
@bp.route("/test_local_to_server", methods=["POST"])
def test_local_to_server():
    try:
        # Check file and JSON payload
        if "file" not in request.files:
            return jsonify({"error": "No zip file received"}), 400

        file = request.files["file"]
        json_data = request.form.get("json")
        if not json_data:
            return jsonify({"error": "No session data received"}), 400

        # Parse the JSON
        try:
            session_data = json.loads(json_data)
        except Exception as e:
            return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400

        participant_session_id = session_data.get("participantSessId")
        trials = session_data.get("trials", [])

        if not participant_session_id or not trials:
            return jsonify({"error": "Invalid session data or no trials found"}), 400

        # Save and unzip the uploaded file
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "session_data.zip")
        file.save(zip_path)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        # Process each trial data and insert into database
        for trial in trials:
            task_id = trial.get("taskID")
            factor_id = trial.get("factorID")
            created_at = trial.get("createdAt")

            if not (task_id and factor_id and created_at):
                continue

            try:
                # Connect to the database
                conn = get_db_connection()
                cur = conn.cursor()

                # Insert trial data
                insert_trial = """
                INSERT INTO trial (participant_session_id, task_id, factor_id, created_at)
                VALUES(%s, %s, %s, %s)
                """
                cur.execute(
                    insert_trial,
                    (participant_session_id, task_id, factor_id, created_at),
                )
                conn.commit()

                # Get the inserted trial ID
                cur.execute("SELECT LAST_INSERT_ID()")
                trial_id = cur.fetchone()[0]

                # Save CSVs to filesystem
                participant_dir = f"/home/hci/Documents/participants_results/{session_data['study_id']}_study_id/{participant_session_id}_participant_session_id/{trial_id}_trial_id"
                os.makedirs(participant_dir, exist_ok=True)

                for root, _, files in os.walk(temp_dir):
                    for file_name in files:
                        if file_name.endswith(".csv"):
                            relative_path = os.path.relpath(root, temp_dir)
                            csv_path = os.path.join(root, file_name)

                            # Save the file with absolute naming
                            absolute_csv_path = os.path.join(participant_dir, file_name)
                            os.rename(csv_path, absolute_csv_path)

            except Exception as e:
                conn.rollback()
                # Error message
                error_type = type(e).__name__
                error_message = str(e)
                return (
                    jsonify(
                        {
                            "Note": "Rollback initiated. Database insertion failed",
                            "error_type": error_type,
                            "error_message": error_message,
                        }
                    ),
                    500,
                )

        # Clean up temp directory
        os.system(f"rm -rf {temp_dir}")

        return jsonify({"message": "Participant session saved successfully"}), 200

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
        SET results_path = %s
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


# All session data from a participant
@bp.route(
    "/get_all_session_data_instance_from_participant_zip/<int:participant_id>",
    methods=["GET"],
)
def get_all_session_data_instance_from_participant_zip(participant_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        study_id_query = """
        SELECT ps.study_id
        FROM participant_session AS ps
        INNER JOIN participant AS p
        ON p.participant_id = ps.participant_id
        WHERE p.participant_id = %s
        """
        cur.execute(study_id_query, (participant_id,))
        study_id = cur.fetchone()[0]

        results_with_size = get_all_participant_csv_files(participant_id, cur)
        cur.close()

        # # Fetch the required data for folder naming
        participant_names = get_participant_name_for_folder(study_id, conn.cursor())
        participant_name = participant_names.get(participant_id, "UnknownParticipant")

        # If no file data found, return an error
        if not results_with_size:
            return jsonify({"error": "No data found for this participant"}), 404

        memory_file = get_zip(results_with_size, study_id, conn, mode="participant")

        return send_file(
            memory_file,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{participant_name}_participant.zip",
        )

    except Exception as e:
        return jsonify({"error_type": type(e).__name__, "error_message": str(e)}), 500


# All session data for a participant session
@bp.route(
    "/get_all_session_data_instance_from_participant_session_zip/<int:participant_session_id>",
    methods=["GET"],
)
def get_all_session_data_instance_from_participant_session_zip(participant_session_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        study_id_query = """
        SELECT s.study_id
        FROM study AS s
        INNER JOIN participant_session AS ps
        ON ps.study_id = s.study_id
        WHERE ps.participant_session_id = %s
        """
        cur.execute(study_id_query, (participant_session_id,))
        study_id = cur.fetchone()[0]

        results_with_size = get_all_participant_session_csv_files(
            participant_session_id, cur
        )
        cur.close()

        # Fetch the required data for folder naming
        participant_sessions = get_participant_session_name_for_folder(
            study_id, conn.cursor()
        )
        participant_session_name = participant_sessions.get(
            participant_session_id, "UnknownSession"
        )

        # If no file data found, return an error
        if not results_with_size:
            return jsonify({"error": "No data found for this participant session"}), 404

        memory_file = get_zip(
            results_with_size, study_id, conn, mode="participant_session"
        )

        return send_file(
            memory_file,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{participant_session_name}_participant_session.zip",
        )

    except Exception as e:
        return jsonify({"error_type": type(e).__name__, "error_message": str(e)}), 500


# Only one specific file of data
@bp.route(
    "/get_one_session_data_instance_zip/<int:session_data_instance_id>", methods=["GET"]
)
def get_one_session_data_instance_zip(session_data_instance_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        study_id_query = """
        SELECT s.study_id
        FROM study AS s
        INNER JOIN participant_session AS ps
        ON ps.study_id = s.study_id
        INNER JOIN trial t
        ON t.participant_session_id = ps.participant_session_id
        INNER JOIN session_data_instance sdi
        ON sdi.trial_id = t.trial_id
        WHERE sdi.session_data_instance_id = %s
        """
        cur.execute(study_id_query, (session_data_instance_id,))
        study_id = cur.fetchone()[0]

        results_with_size = get_one_csv_file(session_data_instance_id, cur)
        cur.close()

        # Fetch the required data for folder naming
        file_names = get_file_name_for_folder(study_id, conn.cursor())
        file_name = file_names.get(session_data_instance_id, "UnknownSession")

        # If no file data found, return an error
        if not results_with_size:
            return jsonify({"error": "No data found for this data instance file"}), 404

        memory_file = get_zip(results_with_size, study_id, conn, mode="one file")

        return send_file(
            memory_file,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{file_name}.zip",
        )

    except Exception as e:
        return jsonify({"error_type": type(e).__name__, "error_message": str(e)}), 500


# All session data for a trial
@bp.route(
    "/get_all_session_data_instance_for_a_trial_zip/<int:trial_id>", methods=["GET"]
)
def get_all_session_data_instance_for_a_trial_zip(trial_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
        SELECT s.study_id, ps.participant_session_id, t.task_name, f.factor_name
        FROM study AS s
        INNER JOIN participant_session AS ps
        ON ps.study_id = s.study_id
        INNER JOIN trial tr
        ON tr.participant_session_id = ps.participant_session_id
        INNER JOIN task AS t
        ON t.task_id = tr.task_id
        INNER JOIN factor AS f
        ON f.factor_id = tr.factor_id
        WHERE tr.trial_id = %s
        """
        cur.execute(query, (trial_id,))
        query_result = cur.fetchone()
        study_id = query_result[0]
        participant_session_id = query_result[1]
        task_name = query_result[2]
        factor_name = query_result[3]

        results_with_size = get_one_trial(trial_id, cur)
        cur.close()

        # Fetch the required data for folder naming
        trial_order = get_trial_order_for_folder(
            participant_session_id, conn.cursor()
        ).get(trial_id, "UnknownTrialOrdering")

        # If no file data found, return an error
        if not results_with_size:
            return jsonify({"error": "No data found for this trial"}), 404

        memory_file = get_zip(results_with_size, study_id, conn, mode="trial")

        return send_file(
            memory_file,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{task_name}_{factor_name}_{trial_order}.zip",
        )

    except Exception as e:
        return jsonify({"error_type": type(e).__name__, "error_message": str(e)}), 500


# All session data for a study
@bp.route("/get_all_session_data_instance_zip/<int:study_id>", methods=["GET"])
def get_all_session_data_instance_zip(study_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        study_name_query = """
        SELECT s.study_name
        FROM study AS s
        WHERE s.study_id = %s
        """
        cur.execute(study_name_query, (study_id,))
        study_name = cur.fetchone()[0]

        results_with_size = get_all_study_csv_files(study_id, cur)
        cur.close()

        # If no file data found, return an error
        if not results_with_size:
            return jsonify({"error": "No data found for this study"}), 404

        memory_file = get_zip(results_with_size, study_id, conn, mode="study")

        return send_file(
            memory_file,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{study_name}.zip",
        )

    except Exception as e:
        return jsonify({"error_type": type(e).__name__, "error_message": str(e)}), 500


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
        SELECT sdi.session_data_instance_id, sdi.results_path, sdi.measurement_option_id, sdi.task_id, sdi.factor_id
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
