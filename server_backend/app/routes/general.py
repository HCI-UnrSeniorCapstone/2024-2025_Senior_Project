from flask import Blueprint, jsonify
from app.utility.db_connection import get_db_connection
from app.routes.studies import get_data
# import logging

# logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
# logger = logging.getLogger(__name__)

bp = Blueprint('general', __name__)

# Basic ping
@bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "Pong!"})

# Test Database Connection and Fetch Data from 'user' table
@bp.route('/test_db')
def test_db():
    load_study()
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Test query
        cur.execute("SELECT * FROM user")

        # Get all rows
        results = cur.fetchall()

        # Close the cursor
        cur.close()

        return jsonify(results)

    except Exception as e:
        # Error message
        return jsonify({"error": str(e)})
    

def load_study(study_id=1):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Query to get study info (single row)
        get_study_info = """
        SELECT
            DATE_FORMAT(s.created_at, '%%m/%%d/%%Y') AS 'Date Created',
            s.study_id AS 'Study ID',
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

        # Convert study_res to dictionary
        study_info = {
            "Date Created": study_res[0],
            "Study ID": study_res[1],
            "User Study Name": study_res[2],
            "Description": study_res[3],
            "# Expected Participants": study_res[4],
            "Role": study_res[5],
            "Study Design Type": study_res[6]
        }

        # Query to get factors (multiple rows)
        get_factors = """
        SELECT
            f.factor_name AS 'Factor Name',
            f.factor_description AS 'Factor Description'
        FROM study_factor AS sf
        JOIN factor AS f
        ON f.factor_id = sf.factor_id
        WHERE sf.study_id = %s;
        """
        cur.execute(get_factors, (study_id,))
        factors = [{"Factor Name": row[0], "Factor Description": row[1]} for row in cur.fetchall()]

        # Query to get tasks (multiple rows)
        get_tasks = """
        SELECT
            t.task_id AS 'Task ID',
            t.task_name AS 'Task Name',
            t.task_description AS 'Task Description',
            t.task_directions AS 'Task Directions',
            t.duration AS 'Duration'
        FROM study_task AS st
        JOIN task AS t
        ON st.task_id = t.task_id
        WHERE st.study_id = %s;
        """
        cur.execute(get_tasks, (study_id,))
        tasks = [{"Task ID": row[0], "Task Name": row[1], "Task Description": row[2], "Task Directions": row[3], "Duration": row[4]} for row in cur.fetchall()]

        # Query to get task measurements (multiple rows)
        get_task_measurements = """
        SELECT
            tm.task_id AS 'Task ID',
            mo.measurement_option_name AS 'Measurement Option'
        FROM task_measurement AS tm
        JOIN measurement_option AS mo
        ON tm.measurement_option_id = mo.measurement_option_id
        WHERE tm.task_id IN (SELECT task_id FROM study_task WHERE study_id = %s);
        """
        cur.execute(get_task_measurements, (study_id,))
        task_measurements = cur.fetchall()

        # Organize measurements under their corresponding tasks
        measurements_by_task = {}
        for row in task_measurements:
            task_id = row[0]
            measurement_option = row[1]
            if task_id not in measurements_by_task:
                measurements_by_task[task_id] = []
            measurements_by_task[task_id].append(measurement_option)

        # Combine tasks and their measurements
        for task in tasks:
            task_id = task["Task ID"]
            task["Measurements"] = measurements_by_task.get(task_id, [])

        # Close the cursor and connection
        cur.close()
        conn.close()

        # Construct final JSON-friendly dictionary
        result = {
            "study_info": study_info,
            "factors": factors,
            "tasks": tasks
        }

        return jsonify(result)

    except Exception as e:
        # Log the error for debugging
        print(f"Error loading study: {e}")
        return jsonify({"error": str(e)})

    