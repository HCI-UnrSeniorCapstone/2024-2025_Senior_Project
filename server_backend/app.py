from flask import Flask, jsonify
from flask_cors import CORS

# creating app
app = Flask(__name__)
app.config.from_object(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})

# Basic ping
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "Pong!"})

# CHANGE THE HOST AND DEBUG WHEN PRODUCTION TIME
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
