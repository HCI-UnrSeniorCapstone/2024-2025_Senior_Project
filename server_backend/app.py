from flask import Flask, jsonify, render_template, request
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from flask_cors import CORS
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

# CHANGE THE HOST AND DEBUG WHEN PRODUCTION TIME
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
