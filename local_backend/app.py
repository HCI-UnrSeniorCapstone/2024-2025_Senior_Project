"""
Used this tutorial for setting up Vue and Flask together
https://testdriven.io/blog/developing-a-single-page-app-with-flask-and-vuejs/
"""

import os
from flask import Flask, request, jsonify, send_file
import json
from flask_cors import CORS
import threading
from features.collect_all import get_all_measurements
import ctypes  # lib for pop up
import random
from PIL import ImageGrab
import cv2
import numpy as np  # type: ignore
import time  # temp for now
import csv
import zipfile
import shutil  # used to remove folder with stuff in it


def extract_mouse_movements(log_file):
    coordinates = []
    with open(log_file, "r") as f:
        reader = csv.reader(f)
        next(reader)  # skips the header
        for row in reader:
            # row[0] = time
            # row[1] = running_time
            # row[2] = x
            # row[3] = y
            x, y = int(row[2]), int(row[3])
            coordinates.append((x, y))
    return coordinates


def create_heatmap(coordinates, screenshot_shape):
    heatmap = np.zeros(screenshot_shape[:2], dtype=np.float32)

    for x, y in coordinates:
        if 0 <= x < screenshot_shape[1] and 0 <= y < screenshot_shape[0]:
            heatmap[y, x] += 1

    # Apply Gaussian blur to smooth the heatmap
    heatmap = cv2.GaussianBlur(heatmap, (15, 15), 0)
    return heatmap


def overlay_heatmap(heatmap, screenshot):
    heatmap_normalized = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
    heatmap_colored = cv2.applyColorMap(
        heatmap_normalized.astype(np.uint8), cv2.COLORMAP_JET
    )

    # Combine the heatmap with the original screenshot
    overlay = cv2.addWeighted(screenshot, 0.7, heatmap_colored, 0.3, 0)
    return overlay


# from the internet


def zip_folder(folder_path, zip_name):
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)


# ***********************************************************************************


# global variables
mouse_tracking_thread = None
keyboard_tracking_thread = None


def set_available_features(task_measurments):
    meaurement_id = []
    # makes sures the default taks are false
    default_tasks = {
        "Mouse Movement": False,
        "Mouse Scrolls": False,
        "Mouse Clicks": False,
        "Keyboard Inputs": False,
    }

    default_measurment_ids = {
        "Mouse Movement": 1,
        "Mouse Scrolls": 2,
        "Mouse Clicks": 3,
        "Keyboard Inputs": 4,
    }

    # checks if features are in the array, then it will change hash into true
    for task in task_measurments:
        if task in default_tasks:
            default_tasks[task] = True
            meaurement_id.append(default_measurment_ids[task])

    return default_tasks, meaurement_id


def Mbox(title, text, style):
    # pop up function (https://stackoverflow.com/questions/2963263/how-can-i-create-a-simple-message-box-in-python)
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)


# 1. I get the Task id, task_direction, factor_id, participant_session_id from vue session form page, add these to the new app.py (TaskName_FactorName_MeasurementType_ParticipantSessionId.csv) -

# 2. Randomization for task and factor combos
# 3. add the task directions and desction go the pop ups
# 4. add old zipfile code
# 5. Download executable


def get_measurments(
    study_name,
    user_Task,
    task_name,
    task_direction,
    task_duration,
    factor_name,
    random_factor_index,
    parti_id,
    study_id,
    user_task_id,
    default_measurment_ids,
    factor_ID,
):
    # Start getting measurements from task
    for measurment_id in range(len(user_Task)):
        global mouse_tracking_thread, keyboard_tracking_thread

        # pop up
        if measurment_id == 0:
            Mbox(
                f"{task_name[measurment_id]}",
                f"Directions: {task_direction[measurment_id]}\nFactor: {factor_name[random_factor_index]}\nDuration: {task_duration[measurment_id]} sec\n\nStart Task",
                0,
            )
        else:
            Mbox(
                f"{task_name[measurment_id]}",
                f"Directions: {task_direction[measurment_id]}\nFactor: {factor_name[random_factor_index]}\nDuration: {task_duration[measurment_id]} sec\n\nStart Next Task",
                0,
            )

        # checks to see if any task was added
        if True in user_Task[measurment_id].values():
            start_time = time.time()  # when exeriment starts

            if (
                user_Task[measurment_id]["Mouse Movement"] is not False
                or user_Task[measurment_id]["Mouse Clicks"] is not False
                or user_Task[measurment_id]["Mouse Scrolls"] is not False
                or user_Task[measurment_id]["Keyboard Inputs"] is not False
            ):
                tracking_thread = threading.Thread(
                    target=get_all_measurements,
                    args=(
                        study_name,
                        task_duration[measurment_id],
                        task_name[measurment_id],
                        start_time,
                        user_Task[measurment_id]["Keyboard Inputs"],
                        user_Task[measurment_id]["Mouse Movement"],
                        user_Task[measurment_id]["Mouse Clicks"],
                        user_Task[measurment_id]["Mouse Scrolls"],
                        factor_name[random_factor_index],
                        parti_id,
                        study_id,
                        user_task_id[measurment_id],
                        default_measurment_ids[measurment_id],
                        factor_ID[measurment_id],
                    ),
                )
                tracking_thread.start()
                app.logger.debug("tracking")
                tracking_thread.join()
            else:
                app.logger.debug("not tracking foo")

            # pop up
            Mbox(f"{task_name[measurment_id]}", "Task Ended", 0)

            # this portion is from the code vinh sent us
            if user_Task[measurment_id]["Mouse Movement"] is not False:
                # TAKES SCREENSHOT OF YOUR SCREEN
                app.logger.debug("Capturing Screen! Please wait a moment...")

                time.sleep(1)
                screenshot = ImageGrab.grab()
                screenshot.save(
                    f"screenshot_{task_name[measurment_id]}_{factor_name[random_factor_index]}_{parti_id}.png"
                )

                screenshot = cv2.imread(
                    f"screenshot_{task_name[measurment_id]}_{factor_name[random_factor_index]}_{parti_id}.png"
                )

                # Extract mouse movement coordinates
                coordinates = extract_mouse_movements(
                    f"./{study_name}/{task_name[measurment_id]}/{task_name[measurment_id]}_{factor_name[random_factor_index]}_Mouse Movement_{parti_id}_{study_id}_{user_task_id[measurment_id]}_{default_measurment_ids[measurment_id]}_{factor_ID[measurment_id]}_data.csv"
                )

                # Create the heatmap
                heatmap = create_heatmap(coordinates, screenshot.shape)

                # Overlay the heatmap on the screenshot
                overlay = overlay_heatmap(heatmap, screenshot)

                # Save the output
                cv2.imwrite(
                    f"./{study_name}/{task_name[measurment_id]}/heatmap_{task_name[measurment_id]}.png",
                    overlay,
                )

                # removes the initial screenshot
                os.remove(
                    f"./screenshot_{task_name[measurment_id]}_{factor_name[random_factor_index]}_{parti_id}.png"
                )

        else:
            app.logger.debug("No Task added")


# parses the factor data from the json
def parse_factor_data(data):
    factor_desc = []
    factor_ID = []
    factor_name = []

    # gets all the factor data
    factor_data = data.get("factors", [])

    # implement later, this is to randomly choose a task
    len_of_factors = len(factor_data)
    random_factor_index = random.randint(0, len_of_factors - 1)

    for i in range(len(factor_data)):
        factor_desc.append(factor_data[i]["factorDescription"])
        factor_ID.append(int(factor_data[i]["factorID"]))
        factor_name.append(factor_data[i]["factorName"])

    return factor_desc, factor_ID, factor_name, random_factor_index


# parses the task data from the json
def parse_task_data(data):
    task_measurements = []
    task_descripton = []
    task_direction = []
    task_duration = []
    task_id = []
    task_name = []

    tasks_data = data.get("tasks", [])
    # implement later, this is to randomly choose a task
    rand_tasks = sorted(tasks_data, key=lambda x: random.random())

    # gets all the factor data
    for i in range(len(rand_tasks)):
        task_measurements.append(rand_tasks[i]["measurementOptions"])
        task_descripton.append(rand_tasks[i]["taskDescription"])
        task_direction.append(rand_tasks[i]["taskDirections"])
        task_name.append(rand_tasks[i]["taskName"])
        task_id.append(rand_tasks[i]["taskID"])
        task_duration.append(float(rand_tasks[i]["taskDuration"]))

    return (
        task_measurements,
        task_descripton,
        task_direction,
        task_duration,
        task_id,
        task_name,
    )


# gets the rest of the data from the json
def parse_detail_data(data):
    parti_count = data.get("participantCount")
    study_desc = data.get("studyDescription")
    study_dsgn_type = data.get("studyDesignType")
    study_name = data.get("studyName")
    parti_id = data.get("participantSessId")
    study_id = data.get("study_id")

    return parti_count, study_desc, study_dsgn_type, study_name, parti_id, study_id


# creating app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS w/ specific routes
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/study_json", methods=["POST", "GET"])
def study_json():
    submissionData = request.get_json()

    json_object = json.dumps(submissionData, indent=4)
    with open(f"../frontend/public/demo3.json", "w") as f:
        f.write(json_object)

    return "finished"


# gets parameters from server and runs
@app.route("/run_study", methods=["POST", "GET"])
def run_study():
    user_Task = []

    # # gets the data from the json file
    # with open('../frontend/public/demo3.json', 'r') as file:
    #     data = json.load(file)
    data = request.get_json()
    app.logger.debug(f"{data}")
    factor_desc, factor_ID, factor_name, random_factor_index = parse_factor_data(data)
    (
        task_measurements,
        task_descripton,
        task_direction,
        task_duration,
        task_id,
        task_name,
    ) = parse_task_data(data)
    parti_count, study_desc, study_dsgn_type, study_name, parti_id, study_id = (
        parse_detail_data(data)
    )

    measurment_id = []
    # checks to see what rand_measurment were selected
    for task_amount in range(len(task_measurements)):
        rand_measurment, rand_measurment_id = set_available_features(
            task_measurements[task_amount]
        )
        # print(rand_measurment, rand_measurment_id)
        user_Task.append(rand_measurment)
        measurment_id.append(rand_measurment_id[0])

    # RECORDS EXPERIMENTS
    get_measurments(
        study_name,
        user_Task,
        task_name,
        task_direction,
        task_duration,
        factor_name,
        random_factor_index,
        parti_id,
        int(study_id),
        task_id,
        measurment_id,
        factor_ID,
    )

    # turns folder to zip file
    zip_file_name = f"{parti_id}.zip"
    zip_folder(f"./{study_name}", zip_file_name)
    shutil.rmtree(f"./{study_name}")

    return "finished"


@app.route("/retrieve_zip/<zip_name>", methods=["GET"])
def retrieve_zip(zip_name):
    z_path = os.path.join(os.getcwd(), zip_name)
    if os.path.exists(z_path) and zip_name.endswith(".zip"):
        return send_file(z_path, as_attachment=True)
    else:
        return "", 200


@app.route("/retrieve_csv/<csv_name>", methods=["GET"])
def retrieve_csv(csv_name):
    csv_path = os.path.join(os.getcwd(), csv_name)
    if os.path.exists(csv_path) and csv_name.endswith(".csv"):
        return send_file(csv_path, as_attachment=True)
    else:
        return "", 404


if __name__ == "__main__":
    app.run(host="localhost", port=5001, debug=True)
