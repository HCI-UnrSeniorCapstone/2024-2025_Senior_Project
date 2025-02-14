import gzip
import io
import zipfile
import pandas as pd
import json
import os


def set_available_features(task_measurments):
    # makes sures the default taks are false
    default_tasks = {
        "Mouse Movement": False,
        "Mouse Scrolls": False,
        "Mouse Clicks": False,
        "Keyboard Inputs": False,
    }

    # checks if features are in the array, then it will change hash into true
    for task in task_measurments:
        if task in default_tasks:
            default_tasks[task] = True

    return default_tasks


def get_study_detail(subData):
    study_name = subData.get("studyName")
    study_desc = subData.get("studyDescription")
    study_design = subData.get("studyDesignType")
    people_count = subData.get("participantCount")

    return (
        study_name,
        study_desc,
        study_design,
    )


def create_study_details(submissionData, cur):
    # Get study_design_type
    cur.execute(
        "SELECT study_design_type_id FROM study_design_type WHERE study_design_type_description = %s",
        (submissionData["studyDesignType"],),
    )
    result = cur.fetchone()
    study_design_type_id = result[0]

    # Insert study
    insert_study_query = """
    INSERT INTO study (study_name, study_description, study_design_type_id, expected_participants)
    VALUES (%s, %s, %s, %s)
    """
    study_name = submissionData["studyName"]
    study_description = submissionData["studyDescription"]
    expected_participants = submissionData["participantCount"]

    # Execute study insert
    cur.execute(
        insert_study_query,
        (study_name, study_description, study_design_type_id, expected_participants),
    )

    return cur.lastrowid


def create_study_task_factor_details(study_id, submissionData, cur):
    # Insert tasks
    insert_task_query = """
    INSERT INTO task (task_name, study_id, task_description, task_directions, duration)
    VALUES (%s, %s, %s, %s, %s)
    """
    for task in submissionData["tasks"]:
        task_name = task["taskName"]
        task_description = task["taskDescription"]
        task_directions = task["taskDirections"]
        task_duration = task.get("taskDuration", None)

        # Error handling for bad duration inputs. Convert empty or invalid values to None
        if task_duration is not None:
            try:
                task_duration = float(task_duration) if task_duration else None
            except ValueError:
                task_duration = None

        # Execute insert for each task
        cur.execute(
            insert_task_query,
            (task_name, study_id, task_description, task_directions, task_duration),
        )

        # Get the task_id of the newly inserted task
        task_id = cur.lastrowid

        # Define query for getting measurement_option_id
        select_measurement_option_query = """
        SELECT measurement_option_id FROM measurement_option WHERE measurement_option_name = %s
        """
        # Define query for inserting task_measurement
        insert_measurement_query = """
        INSERT INTO task_measurement (task_id, measurement_option_id)
        VALUES (%s, %s)
        """
        # Process each measurement option for the task
        for measurement_option in task["measurementOptions"]:
            # Get id for each measurement option
            cur.execute(select_measurement_option_query, (measurement_option,))
            result = cur.fetchone()
            if result:
                measurement_option_id = result[0]

                # Insert task-to-measurement
                cur.execute(insert_measurement_query, (task_id, measurement_option_id))

    # Insert factors
    for factor in submissionData["factors"]:
        insert_factor_query = """
        INSERT INTO factor (study_id, factor_name, factor_description)
        VALUES (%s, %s, %s)
        """
        factor_name = factor["factorName"]
        factor_description = factor["factorDescription"]
        cur.execute(
            insert_factor_query,
            (
                study_id,
                factor_name,
                factor_description,
            ),
        )


def zip_one_csv(result):
    # Create an in-memory bytes buffer for the ZIP archive
    zip_buffer = io.BytesIO()

    # Create a ZIP file within the buffer
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        (
            _,
            csv_path,
            _,
            task_name,
            _,
            measurement_option_name,
            _,
            factor_name,
        ) = result
        # should always be csv but this gives protections in future
        ext = os.path.splitext(csv_path)[1]
        if os.path.exists(csv_path):  # Ensure the file exists
            custom_name = f"{task_name}_{factor_name}_{measurement_option_name}{ext}"
            zip_file.write(csv_path, arcname=custom_name)

    # Rewind the buffer's file pointer to the beginning
    zip_buffer.seek(0)
    return zip_buffer


def zip_multiple_csvs_with_folders(results_with_size):
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Iterate over each participant session
        for participant_session_id, csv_records in results_with_size:
            session_folder = f"session_{participant_session_id}"
            # Iterate over each CSV record for that session
            for record_with_size in csv_records:
                csv_record, _ = record_with_size

                (
                    _,
                    csv_path,
                    _,
                    task_name,
                    _,
                    measurement_option_name,
                    _,
                    factor_name,
                ) = csv_record

                ext = os.path.splitext(csv_path)[1]
                if os.path.exists(csv_path):
                    custom_name = (
                        f"{task_name}_{factor_name}_{measurement_option_name}{ext}"
                    )
                    # Put file in folder
                    arcname = f"{session_folder}/{custom_name}"
                    zip_file.write(csv_path, arcname=arcname)

    zip_buffer.seek(0)
    return zip_buffer


def zip_multiple_csvs(results_with_size):
    # Create an in-memory bytes buffer for the ZIP archive
    zip_buffer = io.BytesIO()

    # Create a ZIP file within the buffer
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for result, _ in results_with_size:
            (
                _,
                csv_path,
                _,
                task_name,
                _,
                measurement_option_name,
                _,
                factor_name,
            ) = result
            # should always be csv but this gives protections in future
            ext = os.path.splitext(csv_path)[1]
            if os.path.exists(csv_path):  # Ensure the file exists
                custom_name = (
                    f"{task_name}_{factor_name}_{measurement_option_name}{ext}"
                )
                zip_file.write(csv_path, arcname=custom_name)

    # Rewind the buffer's file pointer to the beginning
    zip_buffer.seek(0)
    return zip_buffer


# Sort the results by the size of the CSV files so that the user sees data quicker by loading smallest first
def sort_csv_by_size(results):
    results_with_size = []
    for result in results:
        file_size = os.path.getsize(result[1])
        results_with_size.append((result, file_size))

    results_with_size.sort(key=lambda x: x[1])
    return results_with_size


# Gets all csvs from a participant
# def get_all_participant_csv_files(participant_id, cur):
#     select_session_data_instance_route_query = """
#         SELECT sdi.session_data_instance_id, sdi.csv_results_path, sdi.task_id, t.task_name, sdi.measurement_option_id, mo.measurement_option_name, sdi.factor_id, f.factor_name
#         FROM session_data_instance sdi
#         INNER JOIN participant_session ps
#         ON ps.participant_session_id = sdi.participant_session_id
#         INNER JOIN task AS t
#         ON t.study_id = ps.study_id AND t.task_id = sdi.task_id
#         INNER JOIN factor AS f
#         ON f.study_id = ps.study_id AND f.factor_id = sdi.factor_id
#         INNER JOIN measurement_option AS mo
#         ON mo.measurement_option_id = sdi.measurement_option_id
#         WHERE ps.participant_id = %s
#         """

#     cur.execute(select_session_data_instance_route_query, (participant_id,))

#     results = cur.fetchall()
#     return sort_csv_by_size(results)


# Gets all csvs for a participant session
def get_all_participant_session_csv_files(participant_session_id, cur):
    select_session_data_instance_route_query = """
        SELECT sdi.session_data_instance_id, sdi.csv_results_path, sdi.task_id, t.task_name, sdi.measurement_option_id, mo.measurement_option_name, sdi.factor_id, f.factor_name
        FROM session_data_instance sdi
        INNER JOIN participant_session ps
        ON ps.participant_session_id = sdi.participant_session_id
        INNER JOIN task AS t
        ON t.study_id = ps.study_id AND t.task_id = sdi.task_id
        INNER JOIN factor AS f
        ON f.study_id = ps.study_id AND f.factor_id = sdi.factor_id
        INNER JOIN measurement_option AS mo
        ON mo.measurement_option_id = sdi.measurement_option_id
        WHERE ps.participant_session_id = %s
        """

    cur.execute(select_session_data_instance_route_query, (participant_session_id,))

    results = cur.fetchall()
    return sort_csv_by_size(results)


def get_one_csv_file(session_data_instance_id, cur):
    select_session_data_instance_route_query = """
        SELECT sdi.session_data_instance_id, sdi.csv_results_path, sdi.task_id, t.task_name, sdi.measurement_option_id, mo.measurement_option_name, sdi.factor_id, f.factor_name
        FROM session_data_instance sdi
        INNER JOIN participant_session ps
        ON ps.participant_session_id = sdi.participant_session_id
        INNER JOIN task AS t
        ON t.study_id = ps.study_id AND t.task_id = sdi.task_id
        INNER JOIN factor AS f
        ON f.study_id = ps.study_id AND f.factor_id = sdi.factor_id
        INNER JOIN measurement_option AS mo
        ON mo.measurement_option_id = sdi.measurement_option_id
        WHERE sdi.session_data_instance_id = %s
        """

    cur.execute(select_session_data_instance_route_query, (session_data_instance_id,))

    result = cur.fetchone()
    return result


def get_all_study_csv_files(study_id, cur):
    # SQL query to get session data instance details
    select_session_data_instance_routes_query = """
        SELECT sdi.session_data_instance_id, sdi.csv_results_path, sdi.task_id, t.task_name, sdi.measurement_option_id, mo.measurement_option_name, sdi.factor_id, f.factor_name
        FROM session_data_instance sdi
        INNER JOIN participant_session ps
        ON ps.participant_session_id = sdi.participant_session_id
        INNER JOIN task AS t
        ON t.study_id = ps.study_id AND t.task_id = sdi.task_id
        INNER JOIN factor AS f
        ON f.study_id = ps.study_id AND f.factor_id = sdi.factor_id
        INNER JOIN measurement_option AS mo
        ON mo.measurement_option_id = sdi.measurement_option_id
        WHERE ps.study_id = %s
        ORDER BY sdi.session_data_instance_id
        """

    cur.execute(select_session_data_instance_routes_query, (study_id,))

    results = cur.fetchall()

    return sort_csv_by_size(results)


def generate_session_data_from_csv(results_with_size, chunk_size):
    for result, _ in results_with_size:
        (
            session_data_instance_id,
            csv_path,
            task_id,
            _,
            measurement_option_id,
            _,
            factor_id,
            _,
        ) = result
        # Send metadata ONCE per session instance
        metadata = {
            "session_data_instance_id": session_data_instance_id,
            "task_id": task_id,
            "measurement_option_id": measurement_option_id,
            "factor_id": factor_id,
        }
        yield json.dumps({"metadata": metadata}, separators=(",", ":")) + "\n"

        # Read the CSV file in chunks
        for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
            chunk_list = chunk.values.tolist()
            yield json.dumps({"data": chunk_list}, separators=(",", ":")) + "\n"
