from pynput import keyboard
import pandas as pd
import time
from datetime import datetime

listener = None
keyboard_data = []


def on_press(key):
    global keyboard_data
    try:
        keyboard_data.append(
            [int(time.mktime(datetime.now().timetuple())), key.char])
    except AttributeError:
        keyboard_data.append(
            [int(time.mktime(datetime.now().timetuple())), key])


def get_keyboard_ps(run_time=10, key_input_flag=False, task_name=None):
    global listener

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

        # makes csv and inserts the data to the csv
        df = pd.DataFrame(keyboard_data, columns=["Time", "Key_Press"])
        df.to_csv(f"{task_name}_keyboard_data.csv", index=False)


def stop_keyboard_ps():
    global listener
    if listener is not None:
        listener.stop()
        listener = None
