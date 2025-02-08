# Purpose: All functionality specific to the measurement mechanisms Fulcrum currently supports 


from pynput import keyboard, mouse
import time
from datetime import datetime
import pandas as pd
import os


# Global listeners
mouse_listener = None
key_listener = None


# Global storage 
keyboard_data = []
mouse_move_data = []
mouse_click_data = []
mouse_scroll_data = []


#################### MOUSE FUNCTIONALITIES ####################

# Variables for reducing mouse movement pulling frequency by establishing a minimum pixel threshold before recording more data
THRESHOLD = 10
PREV_XPOS = 0
PREV_YPOS = 0
TIME_TRACKER = 0
curr_time = 0
prev_time = 0


def on_move(x, y):
    global PREV_XPOS, PREV_YPOS, curr_time, prev_time, running_time, mouse_move_data

    distance = euclidian_distance(x, y, PREV_XPOS, PREV_YPOS)
    curr_time = datetime.now().strftime('%H:%M:%S')
    
    # if the distance is larger than the threshold, then it can record
    if distance > THRESHOLD:  # and curr_time != prev_time:

        # inserts data into array
        mouse_move_data.append([curr_time, '%.2f' % (time.time() - running_time), x, y])

        PREV_XPOS = x
        PREV_YPOS = y


def on_click(x, y, button, pressed):
    global running_time, mouse_click_data
    mouse_click_data.append([datetime.now().strftime('%H:%M:%S'), '%.2f' % (time.time() - running_time), x, y])


def on_scroll(x, y, dx, dy):
    global running_time, mouse_scroll_data
    mouse_scroll_data.append([datetime.now().strftime('%H:%M:%S'), '%.2f' % (time.time() - running_time), x, y])
    
    
def euclidian_distance(x1, y1, x2, y2):
    ed = ((x1-x2)**2 + (y1-y2)**2)**.5
    return ed


def stop_mouse_ps():
    global mouse_listener
    if mouse_listener is not None:
        mouse_listener.stop()
        mouse_listener = None

##############################################################


################## KEYBOARD FUNCTIONALITIES ##################

def on_press(key):
    global keyboard_data, running_time
    try:
        keyboard_data.append(
            [datetime.now().strftime('%H:%M:%S'), '%.2f' % (time.time() - running_time), key.char])
    except AttributeError:
        keyboard_data.append(
            [datetime.now().strftime('%H:%M:%S'), '%.2f' % (time.time() - running_time), key])


def stop_keyboard_ps():
    global key_listener
    if key_listener is not None:
        key_listener.stop()
        key_listener = None


##############################################################


#################### CORE FUNCTIONALITIES ####################

# Does the actual data collection, using measurement flags to know what to collect for the current trial
def record_measurements(session_id, task, factor, exe_time, tracking_flags):
    global mouse_listener, key_listener, running_time, keyboard_data, running_time, mouse_move_data, mouse_click_data, mouse_scroll_data
    
    running_time = exe_time
    task_dur = float(task['taskDuration'])
    
    # Initialize mouse listener if needed
    if mouse_listener is None or not mouse_listener.running:
        mouse_listener = mouse.Listener(
            on_move=on_move if tracking_flags['mouse_movement'] else None,
            on_click=on_click if tracking_flags['mouse_clicks'] else None,
            on_scroll=on_scroll if tracking_flags['mouse_scrolls'] else None
        )

    # Initialize keyboard listener if needed
    if key_listener is None or not key_listener.running:
        key_listener = keyboard.Listener(
            on_press=on_press if tracking_flags['keyboard_inputs'] else None,
            on_release=None
        )
    
    # Start listeners
    mouse_listener.start()
    key_listener.start()

    # Run for set duration
    start_time = time.time()
    while (time.time() - start_time) < task_dur:
        pass

    # Stop listeners after full duration run 
    stop_mouse_ps()
    stop_keyboard_ps()

    # Makes csv and inserts the data to the csv
    create_csv(session_id, 'KeyboardInputs', 'keyboard', keyboard_data, tracking_flags['keyboard_inputs'], task, factor)
    create_csv(session_id, 'MouseMovement', 'mouse', mouse_move_data, tracking_flags['mouse_movement'], task, factor)
    create_csv(session_id, 'MouseClicks', 'mouse', mouse_click_data, tracking_flags['mouse_clicks'], task, factor)
    create_csv(session_id, 'MouseScrolls', 'mouse', mouse_scroll_data, tracking_flags['mouse_scrolls'], task, factor)

    # Resetting for next trial
    keyboard_data = []
    mouse_move_data = []
    mouse_click_data = []
    mouse_scroll_data = []


# Generating a unique csv for each measurement type for each trial 
def create_csv(session_id, measurement_type, feature, arr_data, is_used, task, factor):    
    if not is_used:
        return

    task_name = task['taskName'].replace(" ","")
    factor_name = factor['factorName'].replace(" ","")


    output_dir = os.path.join(f"Session_{session_id}", f"{task_name}_{factor_name}")
    os.makedirs(output_dir, exist_ok=True)

    if feature == 'mouse':
        df = pd.DataFrame(arr_data, columns=['Time', 'running_time', 'x', 'y'])

    elif feature == 'keyboard':
        df = pd.DataFrame(arr_data, columns=['Time', 'running_time', 'keys'])

    filename = f"{session_id}_{task_name}_{factor_name}_{measurement_type}_data.csv"
    output_path = os.path.join(output_dir, filename)
    df.to_csv(output_path, index=False)

##############################################################

