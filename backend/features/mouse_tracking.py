'''
These functions come from the pynut website.
https://pynput.readthedocs.io/en/latest/
'''
from pynput import mouse
import time
from datetime import datetime

# threshold is for the mouse movement, this determine whether it not it can record data and if the mouse has moved within a certain oiubt
THRESHOLD = 10
PREV_XPOS = 0
PREV_YPOS = 0

listener = None


def on_move(x, y):
    global PREV_XPOS, PREV_YPOS
    # distane will determine whether or not it should record the mouse movement
    # good technique is using the euclidian distance. Very well known in ML/AI and Robotics
    distance = euclidian_distance(x, y, PREV_XPOS, PREV_YPOS)

    # if the distance is larger than the threshold, then it can record
    if distance > THRESHOLD:
        # stole from the code vinh provided lol
        with open('mouse_movment.txt', 'a') as f:
            f.write(
                f"{int(time.mktime(datetime.now().timetuple()))}|Mouse: moved({x}, {y})\n")
        PREV_XPOS = x
        PREV_YPOS = y


# not needed now, but this is from the original functions given
def on_click(x, y, button, pressed):
    with open('mouse_clicks.txt', 'a') as f:
        f.write(
            f"{int(time.mktime(datetime.now().timetuple()))}|Mouse: clicked({x}, {y})\n")


def on_scroll(x, y, dx, dy):
    with open('mouse_scroll.txt', 'a') as f:
        f.write(
            f"{int(time.mktime(datetime.now().timetuple()))}|Mouse: scrolled({x}, {y})\n")


def get_mouse_ps(run_time=10, move_flag=False, click_flag=False, scroll_flag=False):
    global listener
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
