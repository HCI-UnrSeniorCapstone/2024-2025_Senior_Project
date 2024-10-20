'''
Used this tutorial for setting up Vue and Flask together
https://testdriven.io/blog/developing-a-single-page-app-with-flask-and-vuejs/
'''

from flask import Flask, jsonify
from flask_cors import CORS

# creating app
app = Flask (__name__)
app.config.from_object(__name__)

# enable CORS w/ specific routes 
CORS(app, resources={r'/*': {'origins': '*'}})

@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('test back!')

if __name__ == '__main__':
    app.run()