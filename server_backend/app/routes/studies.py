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
    submissionData = request.get_json()

    # This is reading and writing to a json file
    # https://www.geeksforgeeks.org/reading-and-writing-json-to-a-file-in-python/
    json_object = json.dumps(submissionData, indent=4)
    with open(f'../frontend/public/demo2.json', 'w') as f:
        f.write(json_object)

    return 'finished'

@bp.route("/get_data", methods=["GET"])
def get_data():

    # https://www.geeksforgeeks.org/read-json-file-using-python/
    # gets the json data from the db
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Test query
        cur.execute("SELECT study_name, study_description, study_design_type,expected participants, FROM user")

        # Get all rows
        results = cur.fetchall()

        # Close the cursor
        cur.close()

        return jsonify(results)

    except Exception as e:
        # Error message
        return jsonify({"error": str(e)})