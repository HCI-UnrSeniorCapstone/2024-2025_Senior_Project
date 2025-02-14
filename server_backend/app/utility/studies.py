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


def extract_file_info(record, offset=0):
    """
    Extracts the CSV file path and builds a custom filename from a record.

    Expected record layout (relative to offset):
      offset+0: session_data_instance_id
      offset+1: csv_results_path
      offset+2: task_id
      offset+3: task_name
      offset+4: measurement_option_id
      offset+5: measurement_option_name
      offset+6: factor_id
      offset+7: factor_name
    """
    csv_path = record[offset + 1]
    task_name = record[offset + 3]
    measurement_option_name = record[offset + 5]
    factor_name = record[offset + 7]
    ext = os.path.splitext(csv_path)[1]
    custom_name = f"{task_name}_{factor_name}_{measurement_option_name}{ext}"
    return csv_path, custom_name


def zip_csv_files(
    data,
    *,
    group_by: callable = None,
    already_grouped: bool = False,
    record_offset: int = 0,
):
    """
    Use cases:
      - Zip one CSV: Call with a flat list of one tuple, no grouping.
      - Zip multiple CSVs (flat): Call with a flat list, group_by=None.
      - Zip multiple CSVs with folders (flat): Call with a flat list and supply group_by.
      - Zip multiple CSVs with folders (already grouped): Call with already_grouped=True,
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        if already_grouped:
            # Data is already grouped: iterate over groups
            for group_key, group_records in data:
                for record_with_size in group_records:
                    record, _ = record_with_size
                    csv_path, custom_name = extract_file_info(
                        record, offset=record_offset
                    )
                    if os.path.exists(csv_path):
                        arcname = f"{group_key}/{custom_name}"
                        zip_file.write(csv_path, arcname=arcname)
                    else:
                        print(f"Missing file: {csv_path}")
        elif group_by is not None:
            # Data is flat, so group it on the fly
            groups = {}
            for record_with_size in data:
                record, _ = record_with_size
                key = group_by(record)
                groups.setdefault(key, []).append(record)
            for group_key, records in groups.items():
                for record in records:
                    csv_path, custom_name = extract_file_info(
                        record, offset=record_offset
                    )
                    if os.path.exists(csv_path):
                        arcname = f"{group_key}/{custom_name}"
                        zip_file.write(csv_path, arcname=arcname)
                    else:
                        print(f"Missing file: {csv_path}")
        else:
            # No grouping just write all files to the zip archive root
            for record_with_size in data:
                record, _ = record_with_size
                csv_path, custom_name = extract_file_info(record, offset=record_offset)
                if os.path.exists(csv_path):
                    zip_file.write(csv_path, arcname=custom_name)
                else:
                    print(f"Missing file: {csv_path}")

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
        SELECT 
            sdi.session_data_instance_id, 
            ps.participant_session_id,
            sdi.csv_results_path, 
            sdi.task_id, 
            t.task_name, 
            sdi.measurement_option_id, 
            mo.measurement_option_name, 
            sdi.factor_id, 
            f.factor_name
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
            _,
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
