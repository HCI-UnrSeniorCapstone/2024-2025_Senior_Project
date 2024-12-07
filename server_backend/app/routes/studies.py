import random
import os
import csv
from flask import Blueprint, current_app, request, jsonify
import json
from app.utility.studies import set_available_features, get_study_detail
from app.utility.db_connection import get_db_connection


bp = Blueprint('studies', __name__)

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

        # Get study_design_type
        cur.execute("SELECT study_design_type_id FROM study_design_type WHERE study_design_type_description = %s", (submissionData['studyDesignType'],))
        result = cur.fetchone()
        study_design_type_id = result[0]

        # Insert study
        insert_study_query = """
        INSERT INTO study (study_name, study_description, study_design_type_id, expected_participants)
        VALUES (%s, %s, %s, %s)
        """
        study_name = submissionData['studyName']
        study_description = submissionData['studyDescription']
        expected_participants = submissionData['participantCount']

        # Execute study insert
        cur.execute(insert_study_query, (study_name, study_description, study_design_type_id, expected_participants))

        # Get the study_id of the newly inserted study
        study_id = cur.lastrowid

        # Insert tasks
        insert_task_query = """
        INSERT INTO task (task_name, study_id, task_description, task_directions, duration)
        VALUES (%s, %s, %s, %s, %s)
        """
        for task in submissionData['tasks']:
            task_name = task['taskName']
            task_description = task['taskDescription']
            task_directions = task['taskDirections']
            task_duration = task.get('taskDuration', None)

            # Error handling for bad duration inputs. Convert empty or invalid values to None
            if task_duration is not None:
                try:
                    task_duration = float(task_duration) if task_duration else None
                except ValueError:
                    task_duration = None

            # Execute insert for each task
            cur.execute(insert_task_query, (task_name, study_id, task_description, task_directions, task_duration))

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
            for measurement_option in task['measurementOptions']:
                # Get id for each measurement option
                cur.execute(select_measurement_option_query, (measurement_option,))
                result = cur.fetchone()
                if result:
                    measurement_option_id = result[0]

                    # Insert task-to-measurement
                    cur.execute(insert_measurement_query, (task_id, measurement_option_id))

        # Insert factors
        for factor in submissionData['factors']:
            insert_factor_query = """
            INSERT INTO factor (study_id, factor_name, factor_description)
            VALUES (%s, %s, %s)
            """
            factor_name = factor['factorName']
            factor_description = factor['factorDescription']
            cur.execute(insert_factor_query, (study_id, factor_name, factor_description,))

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
        cur.execute(insert_study_user_role_query, (user_id, study_id, study_user_role_type_id))


        # Commit changes to the database
        conn.commit()        
        
        # Close cursor
        cur.close()  
        return 'finished'

    except Exception as e:
        # Error message
        error_type = type(e).__name__ 
        error_message = str(e) 
        
        # 500 means internal error, AKA the database probably broke
        return jsonify({
                "error_type": error_type,
                "error_message": error_message
            }), 500 

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
        
        
        #column_names = [desc[0] for desc in cur.description]  # Extract column names

        # Format results as a list of dictionaries
        #json_results = [dict(zip(column_names, row)) for row in results]
        
        # Close cursor
        cur.close() 

        return jsonify(results)

    except Exception as e:
        # Error message
        error_type = type(e).__name__ 
        error_message = str(e) 
        
        # 500 means internal error, AKA the database probably broke
        return jsonify({
                "error_type": error_type,
                "error_message": error_message
            }), 500  
    
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
                    "measurementOptions": []
                }
                for task in task_res
            ],
            "factors": [
                {"factorName": factor[0], "factorDescription": factor[1] or "No factor description provided"}
                for factor in factor_res
            ]
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
                measurement[1] for measurement in measurement_res if measurement[0] == task["taskID"]
            ]
        # Discard the taskID's
        for task in study_data["tasks"]:
            del task["taskID"]
        
        
        cur.close()
        
        return jsonify(study_data)
        
    except Exception as e:
        # Error message
        error_type = type(e).__name__ 
        error_message = str(e) 
        
        # 500 means internal error, AKA the database probably broke
        return jsonify({
                "error_type": error_type,
                "error_message": error_message
            }), 500 
    
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
        return jsonify({
                "error_type": error_type,
                "error_message": error_message
            }), 500 
        
   
# Saves tracked data to server file system, db will have a file path to the CSVs
@bp.route("/save_session_data_instance/<int:participant_session_id>/<int:study_id>/<int:task_id>/<int:measurement_option_id>/<int:factor_id>", methods=["POST"])
def save_session_data_instance(participant_session_id, study_id, task_id, measurement_option_id, factor_id): 

    # Check if the request contains the file part
    # pretty sure vue has to name is input_csv
    if 'input_csv' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['input_csv']

    # Check if the file is a CSV by its MIME type
    if not file.content_type == 'text/csv':
        return jsonify({"error": "Invalid file type. Only CSV files are allowed."}), 400    
    
    try:     
        
        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Base directory for participant results
        base_dir = current_app.config.get('RESULTS_BASE_DIR_PATH')
             
        # CSV path not included yet
        create_session_data_instance = """
        INSERT INTO session_data_instance(participant_session_id, task_id, measurement_option_id, factor_id)
        VALUES (%s, %s, %s, %s)
        """
        cur.execute(create_session_data_instance, (participant_session_id, task_id, measurement_option_id, factor_id,))
        
        # Get the session_data_instance_id of the newly inserted study
        session_data_instance_id = cur.lastrowid
        
        # Construct file path
        full_path = os.path.join(base_dir, str(study_id), str(participant_session_id))

        # Create directory (this will also create parts of the directory that don't exist)
        os.makedirs(full_path, exist_ok=True)

        # Full file path with CSV
        file_path = os.path.join(full_path, f"{session_data_instance_id}.csv")

        # Check if CSV already exists
        # Want to terminate early because we dont want to overwrite study data
        if os.path.exists(file_path):
            return jsonify({
                    "error_type": "Duplicate session_data_instance",
                    "error_message": "CSV with same name already exists"
                }), 500 

        # Save the file to the system (overwrite if exists)
        file.save(file_path) 
            
        # Add pathway for database
        update_path_session_data_instance = """
        UPDATE session_data_instance
        SET csv_results_path = %s
        WHERE session_data_instance = %s
        """
        cur.execute(update_path_session_data_instance, (file_path,session_data_instance_id))    
        
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
        return jsonify({
                "error_type": error_type,
                "error_message": error_message
            }), 500 
   