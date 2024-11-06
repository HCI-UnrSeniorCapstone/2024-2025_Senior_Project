'''
Used this tutorial for setting up Vue and Flask together
https://testdriven.io/blog/developing-a-single-page-app-with-flask-and-vuejs/
'''

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from features.mouse_tracking import get_mouse_ps
from features.keyboard_tracking import get_keyboard_ps


def set_available_features(task_measurments):
    # makes sures the default taks are false
    default_tasks = {'Mouse Tracking': False, 'Mouse Scrolls': False,
                     'Mouse Clicks': False, 'Keyboard Inputs': False}

    # checks if features are in the array, then it will change hash into true
    for task in task_measurments:
        if task in default_tasks:
            default_tasks[task] = True

    return default_tasks


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
    task_duration = []
    task_measurements = []
    user_Task = []

    # num will be whatever we set it as in vue
    # default for now will be on 10
    submissionData = request.get_json()
    tasks = submissionData.get('tasks', [])

    for i in range(len(tasks)):
        app.logger.debug(i)
        task_duration.append(int(tasks[i]['taskDuration']))
        task_measurements.append((tasks[i]['measurementTypes']))

    # app.logger.debug('')
    # app.logger.debug(task_duration)
    # app.logger.debug(task_measurements)

    # app.logger.debug(task_measurements)
    # app.logger.debug(task_duration)

    # checks to see what tasks were selected
    for task_amount in range(len(task_measurements)):
        tasks = set_available_features(task_measurements[task_amount])
        user_Task.append(tasks)
    app.logger.debug('user task: ')
    app.logger.debug(user_Task)

    '''************************* MOUSE TRACKING  *************************'''
    for task_id in range(len(user_Task)):
        global mouse_tracking_thread, keyboard_tracking_thread
        if True in user_Task[task_id].values():
            # try changing this or looking into a different way of doing this that doesn't add more complexity time, it looks a little ugly
            if user_Task[task_id]['Mouse Tracking'] is not False or user_Task[task_id]['Mouse Clicks'] is not False or user_Task[task_id]['Mouse Scrolls'] is not False:
                mouse_tracking_thread = threading.Thread(target=get_mouse_ps, args=(
                    task_duration[task_id], user_Task[task_id]['Mouse Tracking'], user_Task[task_id]['Mouse Clicks'], user_Task[task_id]['Mouse Scrolls']))
                mouse_tracking_thread.start()
                app.logger.debug("tracking mouse")
                mouse_tracking_thread.join()
            else:
                app.logger.debug("not tracking mouse foo")
            # terminates mouse thread

            '''************************* KEYBOARD TRACKING  *************************'''
            # keyboard_tracking_thread is None or not keyboard_tracking_thread.is_alive() and
            if user_Task[task_id]['Keyboard Inputs'] is not False:
                keyboard_tracking_thread = threading.Thread(
                    target=get_keyboard_ps, args=(task_duration[task_id], user_Task[task_id]['Keyboard Inputs']))
                keyboard_tracking_thread.start()
                app.logger.debug("tracking keyboard")
                keyboard_tracking_thread.join()
            else:
                app.logger.debug("no keyboard foo")
        else:
            app.logger.debug('No Task added')
        # here I add the pop up where it won't start recording until they move into the next task
        app.logger.debug('')
        app.logger.debug('*************Switching tasks*************')
        app.logger.debug('')

    return "finished"


if __name__ == "__main__":
    app.run(debug=True)
