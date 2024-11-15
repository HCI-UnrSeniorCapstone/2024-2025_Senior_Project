'''
These functions come from the pynut website.
https://pynput.readthedocs.io/en/latest/
'''
from pynput import mouse
import time
from datetime import datetime

# threshold is for the mouse movement, this determine whether it not it can record data and if the mouse has moved within a certain oiubt
THRESHOLD = 10  # We have to change this incase we dont want the record every point
PREV_XPOS = 0
PREV_YPOS = 0
TIME_TRACKER = 0

listener = None
tasks_name = None
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
    global PREV_XPOS, PREV_YPOS, tasks_name, curr_time, prev_time

    # distane will determine whether or not it should record the mouse movement
    # good technique is using the euclidian distance. Very well known in ML/AI and Robotics
    distance = euclidian_distance(x, y, PREV_XPOS, PREV_YPOS)
    curr_time = int(time.mktime(datetime.now().timetuple()))
    # if the distance is larger than the threshold, then it can record
    if distance > THRESHOLD:  # and curr_time != prev_time:
        # stole from the code vinh provided lol
        with open(f'mouse_movment_{tasks_name}.txt', 'a') as f:
            f.write(
                f"{curr_time}|Mouse: moved({x}, {y})\n")
        PREV_XPOS = x
        PREV_YPOS = y

        # also takes time
        # prev_time = curr_time


# not needed now, but this is from the original functions given
def on_click(x, y, button, pressed):
    with open(f'mouse_clicks_{tasks_name}.txt', 'a') as f:
        f.write(
            f"{int(time.mktime(datetime.now().timetuple()))}|Mouse: clicked({x}, {y})\n")


def on_scroll(x, y, dx, dy):
    with open(f'mouse_scroll_{tasks_name}.txt', 'a') as f:
        f.write(
            f"{int(time.mktime(datetime.now().timetuple()))}|Mouse: scrolled({x}, {y})\n")


def get_mouse_ps(run_time=10, move_flag=False, click_flag=False, scroll_flag=False, task_name=None):
    global listener, tasks_name

    tasks_name = task_name
    if listener is None or not listener.running:
        listener = mouse.Listener(
            on_move=on_move if move_flag else None,
            on_click=on_click if click_flag else None,
            on_scroll=on_scroll if scroll_flag else None
        )
        listener.start()

        # time of execution
        start_time = time.time()
        while listener.running and (time.time() - start_time) < run_time:
            None

        stop_mouse_ps()


def stop_mouse_ps():
    global listener
    if listener is not None:
        listener.stop()
        listener = None


def euclidian_distance(x1, y1, x2, y2):
    ed = ((x1-x2)**2 + (y1-y2)**2)**.5
    return ed
