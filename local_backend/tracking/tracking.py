# Purpose: Holds all functionality for facilitating a session (excluding measurement-specific functionality which is in measure.py)

import threading
import time
from .utility.screenrecording import record_screen, recording_active, recording_stop
from .utility.measure import record_measurements, data_storage_complete_event
from .utility.heatmap import generate_heatmap


# Running a single trial (task-factor combo) at this point
def conduct_trial(sess_id, task, factor):
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
    
    
    recorder_thread = threading.Thread(target = record_screen, args = (sess_id, task, factor))
    recorder_thread.start()

    # Start tracking as long as at least 1 option was selected for the current task
    if any(measurement_flags.values()):
        data_storage_complete_event.clear()  # reset at the start of a trial
        record_measurements(sess_id, task, factor, measurement_flags)

        # will want to change this eventually so only heatmap generated if the researcher requested it instead of always when mouse movement is involved
        if measurement_flags["mouse_movement"]:
            generate_heatmap(sess_id, task, factor)
    
    recording_stop.set()
    while recording_active.is_set():
        time.sleep(0.1)
