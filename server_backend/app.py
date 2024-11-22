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
    app.run(host='0.0.0.0', debug=True)
