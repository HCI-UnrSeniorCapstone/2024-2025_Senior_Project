from pynput import keyboard
import time
from datetime import datetime

listener = None


def on_press(key):
    with open('keyboard_press.txt', 'a') as f:
        try:
            f.write(
                f"{int(time.mktime(datetime.now().timetuple()))}|keyboard: {key.char} pressed\n")
        except AttributeError:
            f.write(
                f"{int(time.mktime(datetime.now().timetuple()))}|keyboard: {key} pressed\n")


'''dont need this since we just want to get the keys that were pressed, but good to have for now, my delete later '''
# def on_release(key):
#     print('{0} released'.format(
#         key))
#     if key == keyboard.Key.esc:
#         # Stop listener
#         return False


def get_keyboard_ps(run_time=10, key_input_flag=False):
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


def stop_keyboard_ps():
    global listener
    if listener is not None:
        listener.stop()
        listener = None
