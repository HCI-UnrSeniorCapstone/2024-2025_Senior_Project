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

def parse_json(subData):
    study_name = subData.get('studyName')
    study_desc = subData.get('studyDescription')
    study_design = subData.get('studyDesignType')
    people_count = subData.get('participantCount')
    
    tasks = subData.get('tasks', [])
    factors = subData.get('factors', [])

    return study_name, study_desc, study_design, people_count, tasks, factors

# Test Database Connection and Fetch Data from 'user' table
@app.route('/test_db')
def test_db():
    try:
        cur = mysql.connection.cursor()

        # Test query
        cur.execute("SELECT * FROM study")

        # Get all rows
        results = cur.fetchall()

        # Close the cursor
        cur.close()

        return jsonify(results)

    except Exception as e:
        # Error message
        return jsonify({"error": str(e)})

@app.route('/insert')
def insert_db(subdata=None):
        # this is going to be the from the server
        # submissionData = request.get_json()

        #temp
    with open('../frontend/public/demo2.json', 'r') as file:
        data = json.load(file)

    study_name, study_desc, study_design, people_count, tasks, factors = parse_json(data)

    cur = mysql.connection.cursor()

    # gets the latest id_number for study_id
    cur.execute("SELECT MAX(study_id) FROM study")
    result = cur.fetchone()
    study_id = (result[0] or 0) + 1 # we dont need this if the study_id is auto incremeting on the db
    
    #inserting to study table
    sql = "INSERT INTO study (study_id, study_name, study_description, expected_participants) VALUES (%s, %s, %s, %s)"
    val = (study_id, study_name, study_desc, people_count)    
    cur.execute(sql, val)

    # #inserting to task table
    for task_id, task in enumerate(tasks, start=1):
        cur.execute("INSERT INTO ")



    mysql.connection.commit()
    cur.close()

    return 'finished'

# Gets and saves data from study form page and stores it into a json file. The json file is stored in
    # ./frontend/public/demo2.json
@app.route("/create_study", methods=["POST", "GET"])
def create_study():
    submissionData = request.get_json()

    # This is reading and writing to a json file
    # https://www.geeksforgeeks.org/reading-and-writing-json-to-a-file-in-python/
    json_object = json.dumps(submissionData, indent=4)
    with open(f'../frontend/public/demo2.json', 'w') as f:
        f.write(json_object)

    return 'finished'


@app.route("/get_data", methods=["POST", "GET"])
def get_data():

    # https://www.geeksforgeeks.org/read-json-file-using-python/
    # gets the json data from the folder (db in the future)
    with open('../frontend/public/demo2.json', 'r') as file:
        data = json.load(file)

    return data

# CHANGE THE HOST AND DEBUG WHEN PRODUCTION TIME
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
