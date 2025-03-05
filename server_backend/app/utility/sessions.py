import io
import zipfile
import pandas as pd
import json
import os

from app.utility.db_connection import get_db_connection


def get_participant_session_order(participant_session_id):
    """
    Returns the order (count) of a given participant_session_id based on its created_at timestamp.
    This function opens a new connection (optimize as needed).
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT participant_id, created_at FROM participant_session WHERE participant_session_id = %s",
        (participant_session_id,),
    )
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return None
    participant_id, created_at = row
    cur.execute(
        "SELECT COUNT(*) FROM participant_session WHERE participant_id = %s AND created_at <= %s",
        (participant_id, created_at),
    )
    order_count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return order_count


# --- Updated SQL Query ---
def get_core_csv_files_query():
    return """
SELECT 
    s.study_name,
    sdi.session_data_instance_id,
    sdi.results_path,
    tr.trial_id,
    tr.task_id,
    t.task_name,
    sdi.measurement_option_id,
    mo.measurement_option_name,
    tr.factor_id,
    f.factor_name,
    ps.participant_session_id
FROM session_data_instance sdi
INNER JOIN trial tr
    ON tr.trial_id = sdi.trial_id
INNER JOIN participant_session ps
    ON ps.participant_session_id = tr.participant_session_id
INNER JOIN task AS t
    ON t.study_id = ps.study_id AND t.task_id = tr.task_id
INNER JOIN factor AS f
    ON f.study_id = ps.study_id AND f.factor_id = tr.factor_id
INNER JOIN study AS s
    ON s.study_id = f.study_id
INNER JOIN measurement_option AS mo
    ON mo.measurement_option_id = sdi.measurement_option_id
    """


def get_trial_order_for_folder(participant_session_id, cur):
    query = """
    SELECT t.trial_id, t.created_at
    FROM trial AS t
    WHERE participant_session_id = %s
    ORDER BY t.created_at DESC
    """
    cur.execute(query, (participant_session_id,))
    results = cur.fetchall()

    trial_order = {}
    counter = 1
    for result in results:
        trial_order[result[0]] = counter
        counter += 1
    return trial_order


def get_study_name_for_folder(study_id, cur):
    query = """
    SELECT s.study_name
    FROM study AS s
    WHERE s.study_id = %s
    """
    cur.execute(query, (study_id,))
    return cur.fetchone()[0]


def get_participant_session_name_for_folder(study_id, cur):
    query = """
    SELECT ps.participant_session_id, ps.created_at
    FROM participant_session AS ps
    WHERE study_id = %s
    ORDER BY ps.created_at ASC
    """
    cur.execute(query, (study_id,))
    results = cur.fetchall()

    participant_sessions = {}
    counter = 1
    for result in results:
        participant_sessions[result[0]] = counter
        counter += 1
    return participant_sessions


def get_trial_name_for_folder(study_id, cur):
    query = """
    SELECT t.task_id, t.task_name, f.factor_id, f.factor_name
    FROM study AS s
    INNER JOIN task AS t
    ON t.study_id = s.study_id
    INNER JOIN factor AS f
    ON f.study_id = s.study_id
    WHERE s.study_id = %s
    """
    cur.execute(query, (study_id,))
    results = cur.fetchall()
    tasks = {}
    factors = {}

    for task_id, task_name, factor_id, factor_name in results:
        # Add task to tasks dictionary (using task_id as key)
        if task_id not in tasks:
            tasks[task_id] = {
                "task_name": task_name,
                "factors": {},  # We will map factors for this task here
            }

        # Add factor to factors dictionary (using factor_id as key)
        if factor_id not in factors:
            factors[factor_id] = {
                "factor_name": factor_name,
                "tasks": {},  # We will map tasks for this factor here
            }

        # Link the factor to the task in the tasks dictionary
        tasks[task_id]["factors"][factor_id] = factors[factor_id]

        # Link the task to the factor in the factors dictionary
        factors[factor_id]["tasks"][task_id] = tasks[task_id]

    return {"tasks": tasks, "factors": factors}


def get_file_name_for_folder(study_id, cur):
    query = """
    SELECT sdi.results_path, mo.measurement_option_name
    FROM session_data_instance AS sdi
    INNER JOIN measurement_option AS mo
    ON mo.measurement_option_id = sdi.measurement_option_id
    INNER JOIN trial AS t
    ON t.trial_id = sdi.trial_id
    INNER JOIN participant_session AS ps
    ON ps.participant_session_id = t.participant_session_id
    WHERE ps.study_id = %s
    """
    cur.execute(query, (study_id,))
    results = cur.fetchall()
    file_names = {}

    for result in results:
        file_names[result[0]] = result[1]
    return file_names


def extract_study_name(results_path):
    """
    Extracts the study folder (e.g. "1_study_id") from the results path.
    Modify this function if you want to map it to a friendlier study name.
    """
    parts = results_path.split(os.sep)
    for part in parts:
        if "study_id" in part:
            return part
    return "unknown_study"


def build_archive_name(row):
    """
    Given a row tuple with the following order:
      (session_data_instance_id, results_path, trial_id, task_id,
       task_name, measurement_option_id, measurement_option_name,
       factor_id, factor_name, participant_session_id)

    Build the internal path for the zip archive:
      <study_name>/<participant_session_id>/<task_name__factor_name>/<measurement_option_name>.csv
    """
    (
        session_data_instance_id,
        results_path,
        trial_id,
        task_id,
        task_name,
        measurement_option_id,
        measurement_option_name,
        factor_id,
        factor_name,
        participant_session_id,
    ) = row

    study_name = extract_study_name(results_path)
    return os.path.join(
        study_name,
        str(participant_session_id),
        f"{task_name}__{factor_name}",
        f"{measurement_option_name}.csv",
    )


# --- Updated zip_csv_files ---
# def zip_csv_files(
#     data,
#     *,
#     group_by: callable = None,
#     already_grouped: bool = False,
#     record_offset: int = 0,
# ):
#     """
#     Creates a zip archive from CSV files.

#     In the group_by branch the group key is expected to be a tuple:
#       (study_name, participant_session_count, trial_id)
#     which will be passed to extract_file_info.
#     """
#     zip_buffer = io.BytesIO()
#     with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
#         if already_grouped:
#             # Each item in data is (group_key, list of (record, size))
#             for group_key, group_records in data:
#                 # group_key is expected to be (study_name, participant_session_count, trial_id)
#                 study_name, participant_session_count, trial_id = group_key
#                 for record_with_size in group_records:
#                     record, _ = record_with_size
#                     csv_path, archive_path = extract_file_info(
#                         record,
#                         offset=record_offset,
#                         study_name=study_name,
#                         participant_session_count=participant_session_count,
#                         trial_id_override=trial_id,
#                     )
#                     if os.path.exists(csv_path):
#                         zip_file.write(csv_path, arcname=archive_path)
#                     else:
#                         print(f"Missing file: {csv_path}")
#         elif group_by is not None:
#             groups = {}
#             for record_with_size in data:
#                 record, _ = record_with_size
#                 key = group_by(record)
#                 groups.setdefault(key, []).append(record)
#             for group_key, records in groups.items():
#                 # group_key is (study_name, participant_session_count, trial_id)
#                 study_name, participant_session_count, trial_id = group_key
#                 for record in records:
#                     csv_path, archive_path = extract_file_info(
#                         record,
#                         offset=record_offset,
#                         study_name=study_name,
#                         participant_session_count=participant_session_count,
#                         trial_id_override=trial_id,
#                     )
#                     if os.path.exists(csv_path):
#                         zip_file.write(csv_path, arcname=archive_path)
#                     else:
#                         print(f"Missing file: {csv_path}")
#         else:
#             for record_with_size in data:
#                 record, _ = record_with_size
#                 csv_path, archive_path = extract_file_info(record, offset=record_offset)
#                 if os.path.exists(csv_path):
#                     zip_file.write(csv_path, arcname=archive_path)
#                 else:
#                     print(f"Missing file: {csv_path}")
#     zip_buffer.seek(0)
#     return zip_buffer


# --- Updated Sorting Function ---
def sort_csv_by_size(results):
    results_with_size = []
    for result in results:
        file_size = os.path.getsize(result[1])
        results_with_size.append((result, file_size))
    results_with_size.sort(key=lambda x: x[1])
    return results_with_size


def get_all_participant_session_csv_files(participant_session_id, cur):
    query = get_core_csv_files_query() + "WHERE ps.participant_session_id = %s"
    cur.execute(query, (participant_session_id,))
    results = cur.fetchall()
    return sort_csv_by_size(results)


def get_one_csv_file(session_data_instance_id, cur):
    query = get_core_csv_files_query() + "WHERE sdi.session_data_instance_id = %s"
    cur.execute(query, (session_data_instance_id,))
    result = cur.fetchone()
    return result


def get_all_study_csv_files(study_id, cur):
    query = (
        get_core_csv_files_query()
        + "WHERE ps.study_id = %s ORDER BY sdi.session_data_instance_id"
    )
    cur.execute(query, (study_id,))
    results = cur.fetchall()
    # return sort_csv_by_size(results)
    return results


def generate_session_data_from_csv(results_with_size, chunk_size):
    """
    Stream CSV content by first sending metadata and then CSV data in chunks.
    """
    for result, _ in results_with_size:
        (
            session_data_instance_id,
            _,
            task_id,
            _,
            measurement_option_id,
            _,
            factor_id,
            _,
        ) = result
        metadata = {
            "session_data_instance_id": session_data_instance_id,
            "task_id": task_id,
            "measurement_option_id": measurement_option_id,
            "factor_id": factor_id,
        }
        yield json.dumps({"metadata": metadata}, separators=(",", ":")) + "\n"
        for chunk in pd.read_csv(result[1], chunksize=chunk_size):
            chunk_list = chunk.values.tolist()
            yield json.dumps({"data": chunk_list}, separators=(",", ":")) + "\n"
