from pynput import keyboard
import time
from datetime import datetime

listener = None
tasks_name = None


def on_press(key):
    global tasks_name
    with open(f'keyboard_press_{tasks_name}.txt', 'a') as f:
        try:
            f.write(
                f"{int(time.mktime(datetime.now().timetuple()))}|keyboard: {key.char} pressed\n")
        except AttributeError:
            f.write(
                f"{int(time.mktime(datetime.now().timetuple()))}|keyboard: {key} pressed\n")


def get_keyboard_ps(run_time=10, key_input_flag=False, task_name=None):
    global listener, tasks_name
    tasks_name = task_name
    if listener is None or not listener.running:
        listener = keyboard.Listener(
            on_press=on_press if key_input_flag else None,
            on_release=None
        )
        listener.start()

        # time of execution
        start_time = time.time()
        while listener.running and (time.time() - start_time) < run_time:
            None

        stop_keyboard_ps()


def stop_keyboard_ps():
    global listener
    if listener is not None:
        listener.stop()
        listener = None
