import io
import os
import zipfile
from flask import Blueprint, current_app, request, jsonify, Response, send_file
from app.utility.sessions import (
    build_archive_name,
    generate_session_data_from_csv,
    get_all_participant_session_csv_files,
    get_all_study_csv_files,
    get_file_name_for_folder,
    get_one_csv_file,
    get_participant_session_name_for_folder,
    get_participant_session_order,
    get_study_name_for_folder,
    get_trial_name_for_folder,
    # zip_csv_files,
)
from app.utility.db_connection import get_db_connection

bp = Blueprint("sessions", __name__)


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


# 1. All CSV from a participant (grouped by trial)
@bp.route(
    "/get_all_session_data_instance_from_participant_zip/<int:participant_id>",
    methods=["GET"],
)
def get_all_session_data_instance_from_participant_zip(participant_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Get all participant sessions for this participant (ordered by creation time)
        cur.execute(
            "SELECT participant_session_id, created_at, study_id FROM participant_session WHERE participant_id = %s ORDER BY created_at",
            (participant_id,),
        )
        sessions = cur.fetchall()
        if not sessions:
            return jsonify({"error": "No session data found for this participant"}), 404

        all_records = []
        # For each session, fetch its CSV records and annotate them with participant_session_count and study_name.
        for idx, (participant_session_id, created_at, study_id) in enumerate(
            sessions, start=1
        ):
            participant_session_count = idx
            cur.execute("SELECT study_name FROM study WHERE study_id = %s", (study_id,))
            study_row = cur.fetchone()
            study_name = study_row[0] if study_row else "unknown_study"
            csv_records = get_all_participant_session_csv_files(
                participant_session_id, cur
            )
            # Append the extra info to each record (we can simply use the record as is because grouping will override trial)
            # We'll accumulate all records from all sessions.
            for rec, size in csv_records:
                # Create a new tuple with the original record (rec) unchanged.
                all_records.append(((rec), size))
        cur.close()

        # Group records by a key: (study_name, participant_session_count, trial_id)
        def group_key_func(record):
            # Here, record[9] is participant_session_id is not used;
            # We assume that the study_name and participant_session_count are constant per session.
            # For grouping, we extract the trial_id from record[2] and then use the session order that we had.
            # Since we lost the original session order, we call get_participant_session_order(record[9]) here.
            session_order = get_participant_session_order(record[9])
            trial_id = record[2]
            # Also fetch study_name from the record's extra annotation if available.
            # (Here we assume the study_name remains the same across sessions for this participant.)
            # For simplicity, use a placeholder if not available.
            study_name = "study"
            return (study_name, session_order, trial_id)

        zip_buffer = zip_csv_files(
            all_records,
            group_by=group_key_func,
            already_grouped=False,
            record_offset=0,
        )
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name="participant.zip",
        )
    except Exception as e:
        return jsonify({"error_type": type(e).__name__, "error_message": str(e)}), 500


# 2. All CSV for a participant session (each trial folder within that session)
@bp.route(
    "/get_all_session_data_instance_from_participant_session_zip/<int:participant_session_id>",
    methods=["GET"],
)
def get_all_session_data_instance_from_participant_session_zip(participant_session_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT created_at, study_id FROM participant_session WHERE participant_session_id = %s",
            (participant_session_id,),
        )
        session_info = cur.fetchone()
        if not session_info:
            return jsonify({"error": "Participant session not found"}), 404
        session_time_stamp, study_id = session_info
        cur.execute("SELECT study_name FROM study WHERE study_id = %s", (study_id,))
        study_row = cur.fetchone()
        study_name = study_row[0] if study_row else "unknown_study"
        participant_session_count = get_participant_session_order(
            participant_session_id
        )
        results_with_size = get_all_participant_session_csv_files(
            participant_session_id, cur
        )
        cur.close()

        if not results_with_size:
            return (
                jsonify({"error": "No CSV data found for this participant session"}),
                404,
            )

        # Use group_by to group records by (study_name, participant_session_count, trial_id)
        def group_key_func(record):
            trial_id = record[2]
            return (study_name, participant_session_count, trial_id)

        zip_buffer = zip_csv_files(
            results_with_size,
            group_by=group_key_func,
            already_grouped=False,
            record_offset=0,
        )
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{session_time_stamp}_participant_session.zip",
        )
    except Exception as e:
        return jsonify({"error_type": type(e).__name__, "error_message": str(e)}), 500


# 3. Only one specific CSV
@bp.route(
    "/get_one_session_data_instance_zip/<int:session_data_instance_id>", methods=["GET"]
)
def get_one_session_data_instance_zip(session_data_instance_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        result = get_one_csv_file(session_data_instance_id, cur)
        cur.close()
        if not result:
            return jsonify({"error": "Session data instance not found"}), 404
        # For a single file, we use the non-grouped branch.
        zip_buffer = zip_csv_files([(result, 0)], group_by=None, record_offset=0)
        download_name = f"trial_{result[2]}_{result[4]}_{result[8]}_{result[6]}.zip"
        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=download_name,
        )
    except Exception as e:
        return jsonify({"error_type": type(e).__name__, "error_message": str(e)}), 500


# 4. All CSV for a study (grouped by trial)
# @bp.route("/get_all_session_data_instance_zip/<int:study_id>", methods=["GET"])
# def get_all_session_data_instance_zip(study_id):
#     try:
#         conn = get_db_connection()
#         cur = conn.cursor()
#         cur.execute("SELECT study_name FROM study WHERE study_id = %s", (study_id,))
#         study_row = cur.fetchone()
#         if not study_row:
#             return jsonify({"error": "Study not found"}), 404
#         study_name = study_row[0]
#         results_with_size = get_all_study_csv_files(study_id, cur)
#         cur.close()
#         if not results_with_size:
#             return jsonify({"error": "No CSV data found for this study"}), 404

#         # Group key: (study_name, participant_session_order, trial_id)
#         def group_key_func(record):
#             session_order = get_participant_session_order(record[9])
#             trial_id = record[2]
#             return (study_name, session_order, trial_id)

#         zip_buffer = zip_csv_files(
#             results_with_size,
#             group_by=group_key_func,
#             already_grouped=False,
#             record_offset=0,
#         )
#         return send_file(
#             zip_buffer,
#             mimetype="application/zip",
#             as_attachment=True,
#             download_name=f"{study_name}.zip",
#         )
#     except Exception as e:
#         return jsonify({"error_type": type(e).__name__, "error_message": str(e)}), 500


# TESTING OUT NEW VERSION
@bp.route("/get_all_session_data_instance_zip/<int:study_id>", methods=["GET"])
def get_all_session_data_instance_zip(study_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get the results and size from the function you mentioned
        results_with_size = get_all_study_csv_files(study_id, cur)
        cur.close()

        # If no CSV data found, return an error
        if not results_with_size:
            return jsonify({"error": "No data found for this study"}), 404

        # Fetch the required data for folder naming
        study_name = get_study_name_for_folder(study_id, conn.cursor())
        participant_sessions = get_participant_session_name_for_folder(
            study_id, conn.cursor()
        )
        trials = get_trial_name_for_folder(study_id, conn.cursor())
        file_names = get_file_name_for_folder(study_id, conn.cursor())

        # Create an in-memory ZIP file
        memory_file = io.BytesIO()

        with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            trial_counts = {}

            # Iterate over the session data results and organize files in the ZIP
            for result in results_with_size:
                file_path = result[1]
                measurement_option = result[6]
                session_data_instance_id = result[0]

                if not isinstance(file_path, str):
                    return jsonify({"error": "File path is not a valid string"}), 400

                file_name = file_names.get(file_path, "UnknownFile")
                path_parts = file_path.split("/")

                try:
                    participant_session_id = int(path_parts[-3].split("_")[0])
                    trial_id = int(path_parts[-2].split("_")[0])
                except ValueError:
                    return (
                        jsonify(
                            {
                                "error": "Invalid participant session ID or trial ID in file path"
                            }
                        ),
                        400,
                    )

                participant_session_name = participant_sessions.get(
                    participant_session_id, "UnknownSession"
                )
                trial_task_name = (
                    trials["tasks"].get(result[3], {}).get("task_name", "UnknownTrial")
                )
                trial_factor_name = (
                    trials["factors"]
                    .get(result[7], {})
                    .get("factor_name", "UnknownTrial")
                )

                trial_key = f"{trial_task_name}_{trial_factor_name}_{trial_id}"
                trial_counts[trial_key] = trial_counts.get(trial_key, 0) + 1
                trial_folder = (
                    f"{trial_task_name}_{trial_factor_name}_trial_{result[10]}"
                )

                folder_name = f"{study_name}/{participant_session_name}_participant_session/{trial_folder}"

                # Extract the file extension
                file_extension = os.path.splitext(file_path)[1]
                zip_file_path = f"{folder_name}/{measurement_option}{file_extension}"

                with open(file_path, "rb") as file:
                    zipf.writestr(zip_file_path, file.read())

        memory_file.seek(0)

        return send_file(
            memory_file,
            mimetype="application/zip",
            as_attachment=True,
            download_name="session_data.zip",
        )

    except Exception as e:
        return jsonify({"error_type": type(e).__name__, "error_message": str(e)}), 500


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
