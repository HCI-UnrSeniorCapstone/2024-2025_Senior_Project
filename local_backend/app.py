import os
import json
from flask import Flask, request, send_file
from flask_cors import CORS
from utility.file_management import zip_folder
from utility.tracking import parse_study_details, conduct_trial
import shutil  # used to remove folder with stuff in it


# creating app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS w/ specific routes
CORS(app, resources={r'/*': {'origins': '*'}})


###################### ROUTES #####################

# Uses json sent from Vue to initiate monitoring of a session
# @app.route("/run_session", methods=["POST", "GET"])
def run_session():
    # Uses a sample json found in frontend/public for easier debugging and development so we dont have to initiate session from Vue
    with open('../frontend/public/sample_study.json', 'r') as file:
        data = json.load(file)
    
    # data = request.get_json()
    
    # Extract study details
    session_id, study_id, study_name, study_desc, study_dsgn_type, parti_count = parse_study_details(data)
    
    # Extract task details
    tasks = data.get('tasks', {})
    
    # Extract factor details
    factors = data.get('factors', {})
    
    # Extract trial sequence
    trials = data.get('trials', [])
    
    for curr_trial in trials:
        task_id = str(curr_trial['taskID'])
        factor_id = str(curr_trial['factorID'])
        
        conduct_trial(session_id, tasks[task_id], factors[factor_id], app.logger)

    # Turning folder into a zip and then removing folder
    zip_file_name = f"session_results_{session_id}.zip"
    zip_folder(f'./Session_{session_id}', zip_file_name)
    shutil.rmtree(f'./Session_{session_id}')

    return "finished"


@app.route("/retrieve_zip/<zip_name>", methods=["GET"])
def retrieve_zip(zip_name):
    z_path = os.path.join(os.getcwd(), zip_name)
    if os.path.exists(z_path) and zip_name.endswith('.zip'):
        return send_file(z_path, as_attachment=True)
    else:
        return "", 200
    
    
@app.route("/retrieve_csv/<csv_name>", methods=["GET"])
def retrieve_csv(csv_name):
    csv_path = os.path.join(os.getcwd(), csv_name)
    if os.path.exists(csv_path) and csv_name.endswith('.csv'):
        return send_file(csv_path, as_attachment=True)
    else:
        return "", 404 

###################################################


if __name__ == "__main__":
    # app.run(host='localhost', port=5001, debug=True)
    run_session()
