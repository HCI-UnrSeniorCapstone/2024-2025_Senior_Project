import random
from flask import Blueprint, request, jsonify
import json
from app.utility.studies import set_available_features, get_study_detail


bp = Blueprint('studies', __name__)

# Gets and saves data from study form page and stores it into a json file. The json file is stored in
    # ./frontend/public/demo2.json
@bp.route("/create_study", methods=["POST", "GET"])
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