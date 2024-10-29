'''
These functions come from the pynut website.
https://pynput.readthedocs.io/en/latest/
'''

from pynput.keyboard import Key
from pynput import mouse
import time
from datetime import datetime


listener = None


def time_exe(sec):
    return time.time() + sec


def on_move(x, y):
    # stole from the code vinh provided lol
    with open('out.txt', 'a') as f:
        f.write(
            f"{int(time.mktime(datetime.now().timetuple()))}|Mouse: moved({x}, {y})\n")


# not needed now, but this is from the original functions given
def on_click(x, y, button, pressed):
    print('{0} at {1}'.format(
        'Pressed' if pressed else 'Released',
        (x, y)))
    if not pressed:
        # Stop listener
        return False


def on_scroll(x, y, dx, dy):
    print('Scrolled {0} at {1}'.format(
        'down' if dy < 0 else 'up',
        (x, y)))


def get_mouse_ps(run_time):
    global listener
    if listener is None or not listener.running:
        listener = mouse.Listener(
            on_move=on_move, on_click=None, on_scroll=None)
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
