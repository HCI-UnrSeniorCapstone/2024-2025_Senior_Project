'''
These functions come from the pynut website.
https://pynput.readthedocs.io/en/latest/
'''
from pynput import mouse
import time
from datetime import datetime


listener = None

def on_move(x, y):
    # stole from the code vinh provided lol
    with open('mouse_movment.txt', 'a') as f:
        f.write(
            f"{int(time.mktime(datetime.now().timetuple()))}|Mouse: moved({x}, {y})\n")


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
            time.sleep(1)

        stop_mouse_ps()


def stop_mouse_ps():
    global listener
    if listener is not None:
        listener.stop()
        listener = None
