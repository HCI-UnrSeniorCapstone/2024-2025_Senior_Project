import pandas as pd
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


# Stores consent form in the study-level dir in the filesystem
def save_study_consent_form(study_id, file, cur, base_dir):
    # Check if the file is a PDF
    if not file.filename.lower().endswith(".pdf"):
        raise ValueError("Invalid file type. Only PDF files are allowed.")

    # User passed filename
    original_filename = file.filename

    # Constructing path
    full_path = os.path.join(base_dir, f"{study_id}_study_id")
    os.makedirs(full_path, exist_ok=True)

    # Full file path with PDF
    file_path = os.path.join(full_path, "consent_form.pdf")
    # Save the file to the system
    file.save(file_path)

    # If there is an existing consent form we replace it and update (versioning may be better later on)
    insert_consent_form = """
    INSERT INTO consent_form(study_id, file_path, original_filename)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE
        file_path = VALUES(file_path),
        original_filename = VALUES(original_filename),
        uploaded_at = CURRENT_TIMESTAMP;
    """
    cur.execute(insert_consent_form, (study_id, file_path, original_filename))


# Removing consent form
def remove_study_consent_form(study_id, cur):
    # Get file path if one exists
    look_path = """
    SELECT file_path
    FROM consent_form
    WHERE study_id = %s
    """
    cur.execute(look_path, (study_id,))
    result = cur.fetchone()

    if not result:
        return

    file_path = result[0]

    if file_path and os.path.isfile(file_path):
        try:
            os.remove(file_path)
        except Exception as err:
            print(f"Failed removing file at {file_path}: {err}")

    # Updating consent form tbl to reflect deletion
    delete_consent_tbl_entry = """
    DELETE
    FROM consent_form
    WHERE study_id = %s
    """
    cur.execute(delete_consent_tbl_entry, (study_id,))
