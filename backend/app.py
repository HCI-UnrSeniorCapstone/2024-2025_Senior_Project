'''
Used this tutorial for setting up Vue and Flask together
https://testdriven.io/blog/developing-a-single-page-app-with-flask-and-vuejs/
'''

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from features.mouse_tracking import get_mouse_ps
from features.keyboard_tracking import get_keyboard_ps

# checks if features are in the array, then it will change hash into true


def set_available_features(task_measurments, default_tasks):
    for task in task_measurments:
        print(task)
        if task in default_tasks:
            default_tasks[task] = True


# creating app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS w/ specific routes
CORS(app, resources={r'/*': {'origins': '*'}})
# flask code for now
mouse_tracking_thread = None
keyboard_tracking_thread = None


@app.route("/start_tracking", methods=["POST", "GET"])
def start_tracking():

    default_tasks = {'Mouse Tracking': False, 'Mouse Scrolls': False,
                     'Mouse Clicks': False, 'Keyboard Inputs': False}

    # num will be whatever we set it as in vue
    # default for now will be on 10
    submissionData = request.get_json()
    tasks = submissionData.get('tasks', [])

    task_duration = int(tasks[0]['taskDuration'])
    task_measurements = tasks[0]['measurementTypes']

    # app.logger.debug(task_duration)
    # app.logger.debug(task_measurements)

    # checks to see what tasks were selected
    set_available_features(task_measurements, default_tasks)
    # app.logger.debug(default_tasks)

    '''************************* MOUSE TRACKING  *************************'''

    global mouse_tracking_thread, keyboard_tracking_thread
    if mouse_tracking_thread is None or not mouse_tracking_thread.is_alive():
        mouse_tracking_thread = threading.Thread(
            target=get_mouse_ps, args=(task_duration, default_tasks['Mouse Tracking'], default_tasks['Mouse Clicks'], default_tasks['Mouse Scrolls']))
        mouse_tracking_thread.start()
        app.logger.debug("mouse tracking")
    else:
        app.logger.debug("not tracking mouse foo")

    '''************************* KEYBOARD TRACKING  *************************'''

    if keyboard_tracking_thread is None or not keyboard_tracking_thread.is_alive():
        keyboard_tracking_thread = threading.Thread(
            target=get_keyboard_ps, args=(task_duration, default_tasks['Keyboard Inputs']))
        keyboard_tracking_thread.start()
        app.logger.debug("tracking keyboard")
    else:
        app.logger.debug("no keyboard foo")

    return "finished"


if __name__ == "__main__":
    app.run(debug=True)
