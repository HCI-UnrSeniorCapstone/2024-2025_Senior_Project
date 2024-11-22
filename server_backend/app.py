from flask import Flask, jsonify, render_template, request
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from flask_cors import CORS
import random
import json
import os

# creating app
app = Flask(__name__)
app.config.from_object(__name__)

# Load environment variables from .env
load_dotenv()

# MySQL
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)


CORS(app, resources={r'/*': {'origins': '*'}})


def set_available_features(task_measurments):
    # makes sures the default taks are false
    default_tasks = {'Mouse Movement': False, 'Mouse Scrolls': False,
                     'Mouse Clicks': False, 'Keyboard Inputs': False}

    # checks if features are in the array, then it will change hash into true
    for task in task_measurments:
        if task in default_tasks:
            default_tasks[task] = True

    return default_tasks


def get_study_detail(subData):
    study_name = subData.get('studyName')
    study_desc = subData.get('studyDescription')
    study_design = subData.get('studyDesignType')
    people_count = subData.get('participantCount')

    return study_name, study_desc, study_design, people_count

# Basic ping


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "Pong!"})

# Test Database Connection and Fetch Data from 'user' table


@app.route('/test_db')
def test_db():
    try:
        cur = mysql.connection.cursor()

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

# Gets and saves data from study form page and stores it into a json file. The json file is stored in
    # ./frontend/public/demo2.json
@app.route("/create_study", methods=["POST", "GET"])
def create_study():
    task_name = []
    task_duration = []
    task_measurements = []
    user_Task = []

    # num will be whatever we set it as in vue
    # default for now will be on 10
    submissionData = request.get_json()
    default_tasks = submissionData.get('tasks', [])
    study_name, study_desc, study_design, people_count = get_study_detail(
        submissionData)

    # app.logger.debug(submissionData)

    # randominzing dataset for tasks (come back to this once we have factors added to the frontend)
    rand_tasks = sorted(default_tasks, key=lambda x: random.random())

    for i in range(len(rand_tasks)):
        task_name.append(rand_tasks[i]['taskName'])
        task_duration.append(int(rand_tasks[i]['taskDuration']))
        task_measurements.append(rand_tasks[i]['measurementOptions'])

    # checks to see what rand_tasks were selected
    for task_amount in range(len(task_measurements)):
        rand_tasks = set_available_features(task_measurements[task_amount])
        user_Task.append(rand_tasks)

    # This is reading and writing to a json file
        # https://www.geeksforgeeks.org/reading-and-writing-json-to-a-file-in-python/
    json_object = json.dumps(submissionData, indent=4)
    with open(f'../frontend/public/demo2.json', 'w') as f:
        f.write(json_object)
    # RECORDS EXPERIMENTS
    # get_measurments(user_Task, task_name, task_duration)
    return "finished"


# CHANGE THE HOST AND DEBUG WHEN PRODUCTION TIME
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
