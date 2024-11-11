'''
Used this tutorial for setting up Vue and Flask together
https://testdriven.io/blog/developing-a-single-page-app-with-flask-and-vuejs/
'''

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from features.mouse_tracking import get_mouse_ps
from features.keyboard_tracking import get_keyboard_ps
import ctypes  # lib for pop up
import random
from PIL import ImageGrab
import cv2
import numpy as np
import time  # temp for now


def extract_mouse_movements(log_file):
    coordinates = []
    with open(log_file, 'r') as f:
        for line in f:
            parts = line.split('|')
            if len(parts) > 1 and 'moved(' in parts[1]:
                # Extracting the coordinates
                coord_part = parts[1].split('moved(')[1].split(')')[0]
                x, y = map(int, coord_part.split(','))
                coordinates.append((x, y))
    return coordinates


def create_heatmap(coordinates, screenshot_shape):
    heatmap = np.zeros(screenshot_shape[:2], dtype=np.float32)

    for (x, y) in coordinates:
        if 0 <= x < screenshot_shape[1] and 0 <= y < screenshot_shape[0]:
            heatmap[y, x] += 1

    # Apply Gaussian blur to smooth the heatmap
    heatmap = cv2.GaussianBlur(heatmap, (15, 15), 0)
    return heatmap


def overlay_heatmap(heatmap, screenshot):
    heatmap_normalized = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
    heatmap_colored = cv2.applyColorMap(
        heatmap_normalized.astype(np.uint8), cv2.COLORMAP_JET)

    # Combine the heatmap with the original screenshot
    overlay = cv2.addWeighted(screenshot, 0.7, heatmap_colored, 0.3, 0)
    return overlay

# ***********************************************************************************


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

            # this portion is from the code vinh sent us
            if user_Task[task_id]['Mouse Tracking'] is not False:
                # TAKES SCREENSHOT OF YOUR SCREEN
                app.logger.debug("Capturing Screen! Please wait a moment...")

                time.sleep(1)
                screenshot = ImageGrab.grab()
                screenshot.save(f"screenshot_{task_name[task_id]}.png")

                screenshot = cv2.imread(f"screenshot_{task_name[task_id]}.png")

                # Extract mouse movement coordinates
                coordinates = extract_mouse_movements(
                    f"mouse_movment_{task_name[task_id]}.txt")

                # Create the heatmap
                heatmap = create_heatmap(coordinates, screenshot.shape)

                # Overlay the heatmap on the screenshot
                overlay = overlay_heatmap(heatmap, screenshot)

                # Save the output
                cv2.imwrite(f"heatmap_{task_name[task_id]}.png", overlay)

                # removes the initial screenshot
                os.remove(f'./screenshot_{task_name[task_id]}.png')

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
