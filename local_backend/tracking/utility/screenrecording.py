# Handle all screen recording of trials


import mss
import cv2
import numpy as np
import time
import os
import subprocess
import threading
from tracking.utility.file_management import get_file_path
from imageio_ffmpeg import get_ffmpeg_exe

ffmpeg_path = get_ffmpeg_exe()


# Global recording events
recording_stop = threading.Event()
recording_active = threading.Event()
adjustments_finished = threading.Event()


def record_screen(dir_output_base):
    # Reset
    recording_stop.clear()
    adjustments_finished.clear()

    # Signal we are recording
    recording_active.set()

    file_path = get_file_path(dir_output_base, "Screen Recording", "mp4")

    temp_fps = 15
    delay = 1 / temp_fps

    with mss.mss() as sct:
        monitor = sct.monitors[1]
        codec = cv2.VideoWriter_fourcc(*"mp4v")
        # Creating a VideoWriter object
        out = cv2.VideoWriter(
            file_path, codec, temp_fps, (monitor["width"], monitor["height"])
        )

        start_time = time.time()
        next_frame_time = start_time
        frame_count = 0

        while not recording_stop.is_set():  # Until signaled to stop from toolbar GUI
            curr_time = time.time()

            if curr_time >= next_frame_time:
                # Screenshot
                image = sct.grab(monitor)

                # Convert to numpy array
                frame = np.array(image)

                # Convert from BGRA to BGR
                frame = frame[:, :, :3]

                # Writing to output file
                out.write(frame)

                frame_count += 1
                next_frame_time += delay
            else:
                time.sleep(0.001)

        out.release()
        cv2.destroyAllWindows()

        time_elapsed = time.time() - start_time
        fps = frame_count / time_elapsed

        recording_active.clear()

        adjuster_thread = threading.Thread(target=adjust_video, args=(file_path, fps))
        adjuster_thread.daemon = True
        adjuster_thread.start()


# Need this function because fps varies for each person so we have to correct the video using calculated fps using ffmpeg or else play speed and video length will be incorrect
def adjust_video(f_path, fps):
    temp_f_path = f_path.replace(".mp4", "_temp.mp4")

    # Ref FFmpeg https://trac.ffmpeg.org/wiki/How%20to%20speed%20up%20/%20slow%20down%20a%20video
    command = [
        ffmpeg_path,
        "-y",
        "-i",
        f_path,
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-vf",
        f"setpts={15 / fps}*PTS",
        temp_f_path,
    ]

    subprocess.run(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )  # stop FFmpeg terminal output details

    if os.path.exists(temp_f_path):
        os.replace(temp_f_path, f_path)

    adjustments_finished.set()
