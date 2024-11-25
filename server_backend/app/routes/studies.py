import random
from flask import Blueprint, request, jsonify
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
        INSERT INTO task (task_name, task_description, task_directions, duration)
        VALUES (%s, %s, %s, %s)
        """
        for task in submissionData['tasks']:
            task_name = task['taskName']
            task_description = task['taskDescription']
            task_directions = task['taskDirections']
            task_duration = task.get('taskDuration', None)

            # Error handling for bad duration inputs. Convert empty or invalid values to None
            try:
                task_duration = float(task_duration) if task_duration else None
            except ValueError:
                task_duration = None

            # Execute insert for each task
            cur.execute(insert_task_query, (task_name, task_description, task_directions, task_duration))

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

            # Insert tasks into study_task table
            insert_study_task_query = """
            INSERT INTO study_task (study_id, task_id)
            VALUES (%s, %s)
            """
            cur.execute(insert_study_task_query, (study_id, task_id))

        # Insert factors into the study_factor table
        for factor in submissionData['factors']:
            insert_factor_query = """
            INSERT INTO factor (factor_name, factor_description)
            VALUES (%s, %s)
            """
            factor_name = factor['factorName']
            factor_description = factor['factorDescription']
            cur.execute(insert_factor_query, (factor_name, factor_description,))

            # Get the factor_id of the newly inserted factor
            factor_id = cur.lastrowid

            # Insert study_factor 
            insert_study_factor_query = """
            INSERT INTO study_factor (study_id, factor_id)
            VALUES (%s, %s)
            """
            cur.execute(insert_study_factor_query, (study_id, factor_id))

        # CREATES NEW USER. THIS MUST BE CHANGED WHEN WE HAVE USER SESSION IDS
        select_user_query = """
        SELECT user_id FROM user WHERE first_name = 'TEST' AND last_name = 'TEST' AND email = 'broYrUreadingThis@example.com'
        """

        cur.execute(select_user_query)

        # If None then user doesn't exist
        existing_user = cur.fetchone()

        if existing_user: 
            user_id = existing_user[0]
        # Make user
        else:
            insert_user_query = """
            INSERT INTO user (first_name, last_name, email)
            VALUES ('TEST', 'TEST', 'broYrUreadingThis@example.com')
            """
    
            cur.execute(insert_user_query)
    
            # Get new user_id
            user_id = cur.lastrowid

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

        # Close connection
        conn.close()
        
        return 'finished'

    except Exception as e:
        # Error message
        return str(e)


@bp.route("/get_data/<int:user_id>", methods=["GET"])
def get_data(user_id):

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
            FROM participant_study_session
            GROUP BY study_id
        ) AS completed_sessions
            ON study.study_id = completed_sessions.study_id
        WHERE study_user_role.user_id = %s
        """
        
        # Execute get
        cur.execute(select_user_studies_info_query, (user_id,))

        # Get all rows
        results = cur.fetchall()

        # Close cursor
        cur.close()
        
        # Close connection
        conn.close()

        return jsonify(results)

    except Exception as e:
        # Error message
        return  str(e)