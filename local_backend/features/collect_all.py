from pynput import keyboard
from pynput import mouse
import time
from datetime import datetime
import pandas as pd

mouse_listener = None
key_listener = None

keyboard_data = []
mouse_move_data = []
mouse_click_data = []
mouse_scroll_data = []

'''***************************************************  Mouse Functions ***************************************************'''
# threshold is for the mouse movement, this determine whether it not it can record data and if the mouse has moved within a certain oiubt
THRESHOLD = 10  # We have to change this incase we dont want the record every point
PREV_XPOS = 0
PREV_YPOS = 0
TIME_TRACKER = 0

curr_time = 0
prev_time = 0

# while True:
#     curr_time = int(time.mktime(datetime.now().timetuple()))
#     if curr_time != prev_time:
#         print(f'1:curr time: {curr_time} | prev time: {prev_time}')
#         prev_time = curr_time
#         print(f'2:curr time: {curr_time} | prev time: {prev_time}')

'''
Couple ways of doing this:
- One way, using time to record the data points.
    Ex: every 1 second record a point
    pros: creates less lag
    cons: less data points


- Second way, record using distance from previous points
    Ex: Record every 100 pixels
    pros: more data
    cons: creates a little lag
'''

def on_move(x, y):
    global PREV_XPOS, PREV_YPOS, curr_time, prev_time, running_time, mouse_move_data

    # distane will determine whether or not it should record the mouse movement
    # good technique is using the euclidian distance. Very well known in ML/AI and Robotics
    distance = euclidian_distance(x, y, PREV_XPOS, PREV_YPOS)
    curr_time = datetime.now().strftime('%H:%M:%S')
    # if the distance is larger than the threshold, then it can record
    if distance > THRESHOLD:  # and curr_time != prev_time:

        # inserts data into array
        mouse_move_data.append([curr_time, '%.2f' % (time.time() - running_time), x, y])

        PREV_XPOS = x
        PREV_YPOS = y

        # also takes time
        # prev_time = curr_time

# not needed now, but this is from the original functions given
def on_click(x, y, button, pressed):
    global running_time, mouse_click_data
    mouse_click_data.append([datetime.now().strftime('%H:%M:%S'), '%.2f' % (time.time() - running_time), x, y])

def on_scroll(x, y, dx, dy):
    global running_time, mouse_scroll_data
    mouse_scroll_data.append([datetime.now().strftime('%H:%M:%S'), '%.2f' % (time.time() - running_time), x, y])

'''************************************************************************************************************************'''


'''***************************************************  Keyboard Functions ***************************************************'''
def on_press(key):
    global keyboard_data, running_time
    try:
        keyboard_data.append(
            [datetime.now().strftime('%H:%M:%S'), '%.2f' % (time.time() - running_time), key.char])
    except AttributeError:
        keyboard_data.append(
            [datetime.now().strftime('%H:%M:%S'), '%.2f' % (time.time() - running_time), key])
        
'''***************************************************************************************************************************'''

# Gets all the measurments
def get_all_measurements(run_time=10, task_name=None, exe_time=None, key_input_flag=False, move_flag=False, click_flag=False, scroll_flag=False, factor_name=0, parti_id=0):
    global mouse_listener, key_listener, running_time, keyboard_data, running_time, mouse_move_data, mouse_click_data, mouse_scroll_data
    running_time = exe_time

    if mouse_listener is None or not mouse_listener.running:
        mouse_listener = mouse.Listener(
            on_move=on_move if move_flag else None,
            on_click=on_click if click_flag else None,
            on_scroll=on_scroll if scroll_flag else None
        )

    if key_listener is None or not key_listener.running:
        key_listener = keyboard.Listener(
            on_press=on_press if key_input_flag else None,
            on_release=None
        )
        mouse_listener.start()
        key_listener.start()

        # time of execution
        start_time = time.time()
        while mouse_listener.running and key_listener.running and (time.time() - start_time) < run_time:
            None

        stop_mouse_ps()
        stop_keyboard_ps()

        # makes csv and inserts the data to the csv
        create_csv(task_name, 'keyboard', 'keyboard', keyboard_data, key_input_flag, factor_name, parti_id)
        create_csv(task_name, 'mouse_movement', 'mouse', mouse_move_data, move_flag, factor_name, parti_id)
        create_csv(task_name, 'mouse_clicks', 'mouse', mouse_click_data, click_flag, factor_name, parti_id)
        create_csv(task_name, 'mouse_scroll', 'mouse', mouse_scroll_data, scroll_flag, factor_name, parti_id)
        keyboard_data = []
        mouse_move_data = []
        mouse_click_data = []
        mouse_scroll_data = []

def stop_mouse_ps():
    global mouse_listener
    if mouse_listener is not None:
        mouse_listener.stop()
        mouse_listener = None

def stop_keyboard_ps():
    global key_listener
    if key_listener is not None:
        key_listener.stop()
        key_listener = None

def create_csv(task_name, measur_name, feature, arr_data, is_used, factor_name, parti_id):
    if is_used and (feature == 'mouse'):
        df = pd.DataFrame(arr_data, columns=['Time', 'running_time', 'x', 'y'])
        df.to_csv(f'{task_name}_{factor_name}_{measur_name}_{parti_id}_data.csv', index=False)
    #TaskName_FactorName_MeasurementType_ParticipantSessionId.csv
    if is_used and (feature == 'keyboard'):
        df = pd.DataFrame(arr_data, columns=['Time', 'running_time', 'keys'])
        df.to_csv(f'{task_name}_{factor_name}_{measur_name}_{parti_id}_data.csv', index=False)

def euclidian_distance(x1, y1, x2, y2):
    ed = ((x1-x2)**2 + (y1-y2)**2)**.5
    return ed
