import random
from flask import Blueprint, request, jsonify
import json
from app.utility.studies import set_available_features, get_study_detail


bp = Blueprint('studies', __name__)

# Gets and saves data from study form page and stores it into a json file. The json file is stored in
    # ./frontend/public/demo2.json
@bp.route("/create_study", methods=["POST", "GET"])
def create_study():
    submissionData = request.get_json()

    # This is reading and writing to a json file
    # https://www.geeksforgeeks.org/reading-and-writing-json-to-a-file-in-python/
    json_object = json.dumps(submissionData, indent=4)
    with open(f'../frontend/public/demo2.json', 'w') as f:
        f.write(json_object)

    return 'finished'

@bp.route("/get_data", methods=["POST", "GET"])
def get_data():

    # https://www.geeksforgeeks.org/read-json-file-using-python/
    # gets the json data from the folder (db in the future)
    with open('../frontend/public/demo2.json', 'r') as file:
        data = json.load(file)

    return data