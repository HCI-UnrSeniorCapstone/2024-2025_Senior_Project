import io
import zipfile
import pandas as pd
import json
import os


def extract_file_info(record, offset=0):
    """
    Extracts the CSV file path and builds a custom filename from a record.

    Expected record layout (relative to offset):
      offset+0: session_data_instance_id
      offset+1: results_path
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
        SELECT sdi.session_data_instance_id, sdi.results_path, sdi.task_id, t.task_name, sdi.measurement_option_id, mo.measurement_option_name, sdi.factor_id, f.factor_name
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
        SELECT sdi.session_data_instance_id, sdi.results_path, sdi.task_id, t.task_name, sdi.measurement_option_id, mo.measurement_option_name, sdi.factor_id, f.factor_name
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
            sdi.results_path, 
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
