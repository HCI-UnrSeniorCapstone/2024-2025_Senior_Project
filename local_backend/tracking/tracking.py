# Purpose: Holds all functionality for facilitating a session (excluding measurement-specific functionality which is in measure.py)

import threading
import time
import os
from .utility.screenrecording import record_screen, recording_active, recording_stop
from .utility.measure import record_measurements, data_storage_complete_event
from .utility.heatmap import generate_heatmap, heatmap_generation_complete
from .utility.file_management import get_save_dir


# Running a single trial (task-factor combo) at this point
def conduct_trial(sess_id, task, factor, storage_path):
    # Debugging purposes
    print(f"Starting trial for task {task['taskName']}, factor {factor['factorName']}")

    measurements = task["measurementOptions"]

    # Set flags based on the measurement collection mechanisms selected for the given task
    measurement_flags = {
        "mouse_movement": "Mouse Movement" in measurements,
        "mouse_clicks": "Mouse Clicks" in measurements,
        "mouse_scrolls": "Mouse Scrolls" in measurements,
        "keyboard_inputs": "Keyboard Inputs" in measurements,
    }
    
    # Find the base trial dir path to save to
    dir_trial = get_save_dir(storage_path, sess_id, task, factor)
    os.makedirs(dir_trial, exist_ok=True)
    
    # Finding the base filename convention (excludes the file format and measurement type)
    task_name = task["taskName"].replace(" ", "")
    factor_name = factor["factorName"].replace(" ", "")
    filename_base = f"{sess_id}_{task_name}_{factor_name}"
    
    recorder_thread = threading.Thread(target = record_screen, args = (dir_trial, filename_base))
    recorder_thread.start()

    # Start tracking as long as at least 1 option was selected for the current task
    if any(measurement_flags.values()):
        data_storage_complete_event.clear()  # reset at the start of a trial
        record_measurements(task, measurement_flags, dir_trial, filename_base)

    # will want to change this eventually so only heatmap generated if the researcher requested it instead of always when mouse movement is involved
    if measurement_flags["mouse_movement"]:
        data_storage_complete_event.wait()
        heatmap_generation_complete.clear()
        heatmap_thread = threading.Thread(target = generate_heatmap, args = (dir_trial, filename_base))
        heatmap_thread.start()
    else: 
        heatmap_generation_complete.set()
    
    recording_stop.set()
    while recording_active.is_set():
        time.sleep(0.1)
        
