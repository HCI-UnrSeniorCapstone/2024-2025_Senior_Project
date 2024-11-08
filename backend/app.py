'''
Used this tutorial for setting up Vue and Flask together
https://testdriven.io/blog/developing-a-single-page-app-with-flask-and-vuejs/
'''

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from features.mouse_tracking import get_mouse_ps
from features.keyboard_tracking import get_keyboard_ps
import ctypes  # lib for pop up
import random

# global variables
mouse_tracking_thread = None
keyboard_tracking_thread = None


def set_available_features(task_measurments):
    # makes sures the default taks are false
    default_tasks = {'Mouse Tracking': False, 'Mouse Scrolls': False,
                     'Mouse Clicks': False, 'Keyboard Inputs': False}

    # checks if features are in the array, then it will change hash into true
    for task in task_measurments:
        if task in default_tasks:
            default_tasks[task] = True

    return default_tasks


def Mbox(title, text, style):
    # pop up function (https://stackoverflow.com/questions/2963263/how-can-i-create-a-simple-message-box-in-python)
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)


def get_measurments(user_Task, task_name, task_duration):
    # Start getting measurements from task
    for task_id in range(len(user_Task)):
        global mouse_tracking_thread, keyboard_tracking_thread

        # pop up
        if task_id == 0:
            Mbox(f'{task_name[task_id]}', 'Start Task', 0)
        else:
            Mbox(f'{task_name[task_id]}', 'Start Next Task', 0)

        # checks to see if any task was added
        if True in user_Task[task_id].values():
            '''************************* MOUSE TRACKING  *************************'''
            # try changing this or looking into a different way of doing this that doesn't add more complexity time, it looks a little ugly
            if user_Task[task_id]['Mouse Tracking'] is not False or user_Task[task_id]['Mouse Clicks'] is not False or user_Task[task_id]['Mouse Scrolls'] is not False:
                mouse_tracking_thread = threading.Thread(target=get_mouse_ps, args=(
                    task_duration[task_id], user_Task[task_id]['Mouse Tracking'], user_Task[task_id]['Mouse Clicks'], user_Task[task_id]['Mouse Scrolls'], task_name[task_id]))
                mouse_tracking_thread.start()
                app.logger.debug("tracking mouse")
                mouse_tracking_thread.join()
            else:
                app.logger.debug("not tracking mouse foo")

            '''************************* KEYBOARD TRACKING  *************************'''
            # keyboard_tracking_thread is None or not keyboard_tracking_thread.is_alive() and
            if user_Task[task_id]['Keyboard Inputs'] is not False:
                keyboard_tracking_thread = threading.Thread(
                    target=get_keyboard_ps, args=(task_duration[task_id], user_Task[task_id]['Keyboard Inputs'], task_name[task_id]))
                keyboard_tracking_thread.start()
                app.logger.debug("tracking keyboard")
                keyboard_tracking_thread.join()
            else:
                app.logger.debug("no keyboard foo")

            # pop up
            Mbox(f'{task_name[task_id]}', 'Task Ended', 0)
        else:
            app.logger.debug('No Task added')


# creating app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS w/ specific routes
CORS(app, resources={r'/*': {'origins': '*'}})
# flask code for now


@app.route("/start_tracking", methods=["POST", "GET"])
def start_tracking():
    task_name = []
    task_duration = []
    task_measurements = []
    user_Task = []

    # num will be whatever we set it as in vue
    # default for now will be on 10
    submissionData = request.get_json()
    default_tasks = submissionData.get('tasks', [])

    # randominzing dataset for tasks (come back to this once we have factors added to the frontend)
    rand_tasks = sorted(default_tasks, key=lambda x: random.random())

    for i in range(len(rand_tasks)):
        task_name.append(rand_tasks[i]['taskName'])
        task_duration.append(int(rand_tasks[i]['taskDuration']))
        task_measurements.append(rand_tasks[i]['measurementTypes'])

    # checks to see what rand_tasks were selected
    for task_amount in range(len(task_measurements)):
        rand_tasks = set_available_features(task_measurements[task_amount])
        user_Task.append(rand_tasks)

    # RECORDS EXPERIMENTS
    get_measurments(user_Task, task_name, task_duration)
    return "finished"


if __name__ == "__main__":
    app.run(debug=True)
