# Purpose: holds all functionality for facilitating a session (excluding measurement-specific functionality which is in measure.py)


import time
import threading
import ctypes  # lib for pop up
from utility.measure import record_measurements
from utility.heatmap import generate_heatmap


# Getting all study info parsed except for task/factor/trial details 
def parse_study_details(data):
    session_id = data.get('participantSessId')
    study_id = data.get('study_id')
    study_name = data.get('studyName')
    study_desc = data.get('studyDescription')
    study_dsgn_type = data.get('studyDesignType')
    parti_count = data.get('participantCount')

    return session_id, study_id, study_name, study_desc, study_dsgn_type, parti_count


# Running a single trial (task-factor combo) at this point
def conduct_trial(sess_id, task, factor, logger):
    # Extract task details
    task_name = task['taskName']
    task_dirs = task['taskDirections']
    task_dur = float(task['taskDuration'])
    measurements = task['measurementOptions']
    
    # Extract factor details 
    factor_name = factor['factorName']
    
    # Set flags based on the measurement collection mechanisms selected for the given task
    measurement_flags = {
        'mouse_movement': 'Mouse Movement' in measurements,
        'mouse_clicks': 'Mouse Clicks' in measurements,
        'mouse_scrolls': 'Mouse Scrolls' in measurements,
        'keyboard_inputs': 'Keyboard Inputs' in measurements
    }
    
    # Start tracking as long as at least 1 option was selected for the current task
    if any(measurement_flags.values()):
        # Display pop-up when trial starts  
        Mbox(f'{task_name}', f'Directions: {task_dirs}\nFactor: {factor_name}\nDuration: {task_dur} sec\n\nStart Trial...', 0)
        
        track_activity(sess_id, task, factor, measurement_flags, logger)
        
        # Display pop-up when trial ends
        Mbox(f'{task_name}', 'Task Ended', 0)
        
    else:
        logger.debug("no measurement options selected for current task")


def track_activity(session_id, task, factor, tracking_flags, logger):
    # Start tracking
    start_time = time.time()
    tracking_thread = threading.Thread(target=record_measurements, args=(session_id, task, factor, start_time, tracking_flags))
    tracking_thread.start()
    logger.debug("tracking started...")
    tracking_thread.join()

    if tracking_flags['mouse_movement']:
        generate_heatmap(session_id, task, factor, logger)


# pop up boxes for trial-to-trial facilitation
def Mbox(title, text, style):
    # pop up function (https://stackoverflow.com/questions/2963263/how-can-i-create-a-simple-message-box-in-python)
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)