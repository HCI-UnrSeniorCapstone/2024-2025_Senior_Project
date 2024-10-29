'''
Used this tutorial for setting up Vue and Flask together
https://testdriven.io/blog/developing-a-single-page-app-with-flask-and-vuejs/
'''

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from features.mouse_tracking import get_mouse_ps

# creating app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS w/ specific routes
CORS(app, resources={r'/*': {'origins': '*'}})
# flask code for now
tracking_thread = None


@app.route("/start_tracking", methods=["POST", "GET"])
def start_tracking():
    # num will be whatever we set it as in vue
    # default for now will be on 10
    submissionData = request.get_json()
    tasks = submissionData.get('tasks', [])

    task_duration = int(tasks[0]['taskDuration'])
    task_measurements = tasks[0]['measurementTypes']

    # app.logger.debug(task_duration)
    # app.logger.debug(task_measurements)

    if 'Mouse Tracking' in task_measurements:
        global tracking_thread

        if tracking_thread is None or not tracking_thread.is_alive():
            tracking_thread = threading.Thread(
                target=get_mouse_ps, args=(task_duration,))
            tracking_thread.start()
            return "Mouse tracking started"
    else:
        return 'non foo'


if __name__ == "__main__":
    app.run(debug=True)
