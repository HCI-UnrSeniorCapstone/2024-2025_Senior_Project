# Purpose: Holds all UI and functionality related to Global Toolbar


import sys
import json
import threading
import os
import time
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# PyQt libraries
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, pyqtSlot, QObject
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QMessageBox,
    QDialog,
    QFileDialog,
)
from tracking.tracking import conduct_trial
from tracking.utility.file_management import package_session_results, get_save_dir
from tracking.utility.measure import (
    pause_event,
    stop_event,
    data_storage_complete_event,
)
from tracking.utility.screenrecording import (
    recording_stop,
    recording_active,
    adjustments_finished,
)
from tracking.utility.heatmap import heatmap_generation_complete
from routes.send_server import send_to_server


class SignalBridge(QObject):
    session_data_received = pyqtSignal(dict)


# Ref https://www.pythonguis.com/tutorials/pyqt6-widgets/
class GlobalToolbar(QWidget):
    def __init__(self, signal_bridge):
        super().__init__()
        self.signal_bridge = signal_bridge
        self.signal_bridge.session_data_received.connect(self.on_session_data_received)

        self.session_json = {}
        self.setup_ui()
        self.facilitator_setup()  # so facilitator can specify output path beforehand rather than during the session (cleaner)
        self.trial_index = 0
        self.oldPos = None  # track toolbar pos on screen
        self.session_paused = False
        self.countdown = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)

    @pyqtSlot(dict)
    def on_session_data_received(self, session_data):
        self.session_json.clear()
        self.session_json = session_data
        self.session_id, self.tasks, self.factors, self.trials = (
            self.parse_study_details(session_data)
        )

        self.show()

        self.start_btn.setEnabled(True)

    # All UI related
    def setup_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setFixedSize(800, 50)
        screen_width = QApplication.primaryScreen().geometry().width()
        toolbar_width = self.frameGeometry().width()
        self.move((screen_width - toolbar_width) // 2, 0)

        layout = QHBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        # Format all buttons
        btn_style = """
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #36383b;
            }
            QPushButton:disabled {
                background-color: transparent;
                border: none;
                opacity: 0.3
            }
        """

        # Ties an icon (.svg), an associated label, and an action together to produce a button
        def create_btn(icon, label, action):
            vbox = QVBoxLayout()
            vbox.setSpacing(1)
            button = QPushButton()
            button.setIcon(QIcon(icon))
            if label == "Start":
                button.setIconSize(QSize(35, 35))
            else:
                button.setIconSize(QSize(25, 25))
            button.setStyleSheet(btn_style)

            if action is not None:
                button.clicked.connect(action)

            vbox.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)

            tool_desc = QLabel(label)
            tool_desc.setStyleSheet("color: white; font-size: 10px")
            tool_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vbox.addWidget(tool_desc)

            return vbox, button, tool_desc

        # Start button
        start_layout, self.start_btn, self.start_label = create_btn(
            "./icons/start.svg", "Start", self.start_session
        )
        layout.addLayout(start_layout)
        self.start_btn.setEnabled(False)

        # Pause/Resume button
        pause_layout, self.pause_btn, self.pause_label = create_btn(
            "./icons/resume.svg", "Resume", self.pause_session
        )
        layout.addLayout(pause_layout)
        self.pause_btn.setEnabled(False)  # starts disabled

        # Next button
        next_layout, self.next_btn, self.next_label = create_btn(
            "./icons/next.svg", "Next Task", self.move_next_task
        )
        layout.addLayout(next_layout)
        self.next_btn.setEnabled(False)  # starts disabled

        # Timer countdown
        self.timer_label = QLabel("             ")
        self.timer_label.setStyleSheet(
            "color: white; font-size: 16px; padding: 5px 10px; border-radius: 12px; border: 1px solid #444"
        )
        layout.addWidget(self.timer_label)

        # Participant's progress
        self.progress = QLabel("           ")
        self.progress.setStyleSheet(
            "color: white; font-size: 16px; padding: 5px 10px; border-radius: 12px; border: 1px solid #444"
        )
        layout.addWidget(self.progress)

        # Recording status (button but does nothing, however, making it this ways makes it consistent with the rest of the ui)
        recording_layout, self.recording_btn, self.recording_label = create_btn(
            "./icons/not_recording.svg", "Recording", None
        )
        layout.addLayout(recording_layout)
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_recording_status)
        self.recording_timer.start(500)

        # Help button
        help_layout, self.help_btn, self.help_label = create_btn(
            "./icons/help.svg", "Help", self.open_help_menu
        )
        layout.addLayout(help_layout)

        # Quit button
        quit_layout, self.quit_btn, self.quit_label = create_btn(
            "./icons/quit.svg", "Quit", self.leave_session
        )
        layout.addLayout(quit_layout)

    # Getting all study info parsed
    def parse_study_details(self, data):
        session_id = data.get("participantSessId")
        tasks = data.get("tasks", {})
        factors = data.get("factors", {})
        trials = data.get("trials", [])
        return session_id, tasks, factors, trials

    def facilitator_setup(self):
        welcome_msg = QDialog(self)
        welcome_msg.setWindowTitle("Facilitator Use Only")
        welcome_msg.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
        )

        welcome_msg.setFixedSize(450, 200)

        x_pos, y_pos = self.get_dialog_placement_pos(welcome_msg)
        welcome_msg.move(x_pos, y_pos)

        layout = QVBoxLayout(welcome_msg)

        welcome_label = QLabel("Welcome to the Experiment Setup!")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("color: white; font-size: 18pt; font-weight: bold;")

        instuctions_label = QLabel("Please select a folder to store session results.")
        instuctions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instuctions_label.setStyleSheet("color: white; font-size: 14pt;")

        select_btn = QPushButton("Select Folder")
        select_btn.setStyleSheet(
            "color: white; font-size: 14pt; padding: 8px 20px; border-radius: 5px; border: 1px solid white;"
        )
        select_btn.clicked.connect(welcome_msg.accept)

        layout.addWidget(welcome_label)
        layout.addWidget(instuctions_label)
        layout.addWidget(select_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        welcome_msg.exec()

        self.storage_dir = self.get_storage_loc()

        self.session_ready()

    def session_ready(self):
        ready_msg = QDialog(self)
        ready_msg.setWindowTitle("End of Facilitator Use")
        ready_msg.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
        )

        ready_msg.setFixedSize(450, 300)

        x_pos, y_pos = self.get_dialog_placement_pos(ready_msg)
        ready_msg.move(x_pos, y_pos)

        layout = QVBoxLayout(ready_msg)

        ready_label = QLabel("Ready to Go!")
        ready_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ready_label.setStyleSheet("color: white; font-size: 18pt; font-weight: bold;")

        checkmark_label = QLabel("✅")
        checkmark_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        checkmark_label.setStyleSheet("font-size: 48pt")

        instructions_label = QLabel(
            "Once the Participant is ready,\n click Continue to begin"
        )
        instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions_label.setStyleSheet("color: white; font-size: 14pt;")

        continue_btn = QPushButton("Continue")
        continue_btn.setStyleSheet(
            "color: white; font-size: 14pt; padding: 8px 20px; border-radius: 5px; border: 1px solid white;"
        )
        continue_btn.clicked.connect(ready_msg.accept)

        layout.addWidget(ready_label)
        layout.addWidget(checkmark_label)
        layout.addWidget(instructions_label)
        layout.addWidget(continue_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        ready_msg.exec()

    # Need to get a dir path to know where to save the results locally (for redundancy)
    def get_storage_loc(self):
        while True:
            storage_dir = QFileDialog.getExistingDirectory(
                self, "Select Storage Location"
            )

            if not storage_dir:
                QMessageBox.warning(
                    self,
                    "Selection Required",
                    "Storage location is mandatory. Please try again!",
                )

            elif not self.validate_storage_loc(storage_dir):
                QMessageBox.warning(
                    self,
                    "Invalid Folder Selected",
                    "No permission to write to this location. Try a new folder!",
                )

            else:
                return storage_dir

    # Some locations like OneDrive are currently problematic so avoid accepting those until I can figure out a way to validate paths better
    def validate_storage_loc(self, output_path):
        if not output_path or not os.path.exists(output_path):
            return False

        unsupported_locations = ["OneDrive", "Google Drive", "Dropbox"]
        if any(
            keyword.lower() in output_path.lower() for keyword in unsupported_locations
        ):
            return False

        return True

        # temp_dir = os.path.join(output_path, "temp_folder")
        # temp_file = os.path.join(temp_dir, "temp_file.txt")

        # try:
        #     os.makedirs(temp_dir, exist_ok=True)
        #     with open(temp_file, "w") as f:
        #         f.write("X" * 1024)
        #     os.remove(temp_file)
        #     os.rmdir(temp_dir)
        #     return True

        # except PermissionError:
        #     return False

        # except Exception as e:
        #     print(f"Error trying to validate storage directory: {e}")
        #     return False

    def start_session(self):
        self.move_next_task()  # start btn treated same way as moving to next task essentially

    def move_next_task(self):
        # Confirm user wants to move on
        trial_end_msg = QMessageBox()
        if self.trial_index > 0:
            trial_end_msg.setWindowTitle(f"End Task {self.trial_index}?")
        else:
            trial_end_msg.setWindowTitle(f"Begin")
        trial_end_msg.setText(f"Are you ready to start Task {self.trial_index + 1}?")
        trial_end_msg.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )

        if trial_end_msg.exec() == QMessageBox.StandardButton.Ok:
            if self.trial_index == 0:
                # Timestamp useful for saving to filesytem
                sess_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.session_json["sessionStartTime"] = sess_start_time
                print(f"Session start time: {sess_start_time}")
            if self.trial_index > 0:
                # Make sure prior trial's details are saved before moving fwd
                stop_event.set()
                pause_event.clear()
                recording_stop.set()
                self.wait_trial_save()

            # Get next trial's details
            trial = self.trials[self.trial_index]
            task_id = str(trial["taskID"])
            task = self.tasks[task_id]
            task_dirs = task["taskDirections"]
            task_dur = task.get("taskDuration", None)
            factor_id = str(trial["factorID"])
            factor = self.factors[factor_id]

            # Display info for new trial
            self.display_new_trial_info(task_dur, task_dirs)

            # Get trial start timestamp here for JSON
            trial_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.trials[self.trial_index]["startedAt"] = trial_start_time
            print(f"Trial {self.trial_index + 1} start time: {trial_start_time}")

            # Update session_json trials
            self.session_json["trials"] = self.trials

            self.start_btn.setEnabled(False)  # disable for the rest of the session
            self.session_paused = False

            self.pause_btn.setEnabled(True)
            self.pause_btn.setIcon(QIcon("./icons/pause.svg"))
            self.pause_label.setText("Pause")

            pause_event.set()  # start tracking
            stop_event.clear()
            data_storage_complete_event.clear()
            heatmap_generation_complete.clear()

            trial_thread = threading.Thread(
                target=conduct_trial,
                args=(
                    self.session_id,
                    task,
                    factor,
                    self.storage_dir,
                    (self.trial_index + 1),
                ),
            )
            trial_thread.start()

            if task_dur:
                self.initiate_countdown(int(float(task_dur) * 1))
            else:
                self.timer_label.setText("No Time Limit")
                self.next_btn.setEnabled(True)
                self.pause_btn.setEnabled(True)
                self.pause_btn.setIcon(QIcon("./icons/pause.svg"))
                self.pause_label.setText("Pause")

            if (
                self.trial_index == len(self.trials) - 1
            ):  # cannot go to next task bc there is not one
                self.next_btn.setEnabled(False)

            self.trial_index += 1
            self.progress.setText(f"Task {self.trial_index} of {len(self.trials)}")

    # Show details of current trial in pop-up
    def display_new_trial_info(self, dur, dir):
        trial_start_msg = QMessageBox()
        trial_start_msg.setWindowTitle(f"Task {self.trial_index + 1}")
        
        contents = ""
        if dir:
            contents += f"Directions: {dir}\n"
        if dur:
            contents += f"Duration: {dur} minutes"
        else:
            contents += f"Duration: No time limit"
        
        trial_start_msg.setText(contents)

        trial_start_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        # Customize to prevent close button from actually working
        trial_start_msg.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
        )

        trial_start_msg.exec()

    # Starts the countdown timer
    def initiate_countdown(self, duration):
        self.next_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)

        self.countdown = duration
        self.format_countdown()
        self.timer.start(1000)

    # Updates the countdown (decreasing by 1 sec)
    def update_countdown(self):
        # Added this because of a delay where the pause button would briefly be enabled even though the countdown hit zero, breaking program when clicked so I added a buffer to resolve
        if self.countdown == 1:
            self.pause_btn.setEnabled(
                False
            )  # disable pause when task is at its end since no tracking occuring
            self.pause_btn.setIcon(QIcon("./icons/resume.svg"))
            self.pause_label.setText("Resume")
        if self.countdown > 0 and not self.session_paused:
            self.countdown -= 1
            self.format_countdown()
        else:
            self.timer.stop()

            if self.trial_index < len(self.trials):
                self.next_btn.setEnabled(
                    True
                )  # allow participant to move on since time is out
            else:
                self.next_btn.setEnabled(False)  # no more tasks to move on to

            self.session_paused = True
            pause_event.clear()
            stop_event.set()

    # Showing time in HH:MM:SS format
    def format_countdown(self):
        hrs = self.countdown // 3600
        mins = (self.countdown % 3600) // 60
        secs = self.countdown % 60
        self.timer_label.setText(f"Time Remaining: {hrs:02}:{mins:02}:{secs:02}")

    # Inverting state, as if we are running we pause and if we are paused we resume
    def pause_session(self):
        self.session_paused = not self.session_paused  # toggle

        if self.session_paused:
            print("session paused")
            self.pause_btn.setIcon(QIcon("./icons/resume.svg"))
            self.pause_label.setText("Resume")
            pause_event.clear()
            self.timer.stop()
        else:
            print("session resumed")
            self.pause_btn.setIcon(QIcon("./icons/pause.svg"))
            self.pause_label.setText("Pause")
            pause_event.set()
            if self.countdown > 0:
                self.timer.start(1000)
            else:
                pause_event.set()

    def update_recording_status(self):
        if recording_active.is_set():
            self.recording_btn.setIcon(QIcon("./icons/recording.svg"))
        else:
            self.recording_btn.setIcon(QIcon("./icons/not_recording.svg"))

    def open_help_menu(self):
        help_msg = QMessageBox()
        help_msg.setWindowTitle("Help")

        if self.trial_index > 0:
            curr_trial = self.trials[
                self.trial_index - 1
            ]  # -1 (unlike move_next_task) because we want info for current task not the next one
            task_id = str(curr_trial["taskID"])
            task = self.tasks[task_id]
            task_dirs = task["taskDirections"]
            if not task_dirs:
                task_dirs = 'Ask facilitator for directions if needed'
            help_msg.setText(
                f"<b>Directions:</b>\n"
                f"<ul><li>{task_dirs}</li></ul>"
                f"<b>Toolbar Guide:</b>\n"
                "<ul>"
                "<li><b>Start:</b> Begins a new session (<b>NOT</b> a new task). This is only available at the start of a session</li>"
                "<li><b>Pause/Resume:</b> Will pause the current task if needed. Clicking again will resume the current task</li>"
                "<li><b>Next Task:</b> Will advance the session to the next task. For timed tasks, this action is disabled until the timer hits zero. <b>WARNING -</b> For non-timed tasks please confirm with the facilitator before moving forward</li>"
                "<li><b>Quit:</b> Ends the session and closes the application. <b>WARNING -</b> Quitting the session before completing all tasks may invalidate results. Please confirm with the facilitator before exiting</li>"
                "</ul>"
            )
        else:  # have not started a task yet, aka still on start screen
            help_msg.setText(
                f"<b>Directions:</b>\n"
                f"<ul><li>Click the Start button to begin the session</li></ul>"
            )

        help_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        help_msg.exec()

    def leave_session(self):
        if self.trial_index == 0:
            QApplication.quit()
            return

        trial = self.trials[self.trial_index - 1]
        task_id = str(trial["taskID"])
        task = self.tasks[task_id]
        task_dur = task.get("taskDuration", None)

        confirmation_msg = ""
        is_last_task = self.trial_index == len(self.trials)
        is_task_finished = task_dur is not None and self.countdown == 0

        # unique messaging when trying to quit based on the current session state
        if is_last_task and is_task_finished:
            confirmation_msg = "Are you sure you want to exit?"
        elif is_last_task and task_dur is None:  # untimed last task
            confirmation_msg = "Are you sure you want to exit? Please confirm with facilitator before exiting."
        else:  # quitting early
            confirmation_msg = "Are you sure you want to exit before completing the session? Ending early may invalidate results. Please confirm with facilitator before exiting."

        confirm_quit = QMessageBox.question(
            self,
            "Confirmation Required",
            confirmation_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm_quit == QMessageBox.StandardButton.Yes:
            if (
                self.trial_index > 0
            ):  # only attempt to save results if they completed at least 1 trial

                pause_event.clear()
                stop_event.set()

                self.wait_trial_save()

                session_path = get_save_dir(self.storage_dir, self.session_id)

                if os.path.exists(session_path):
                    try:
                        package_session_results(self.session_id, self.storage_dir)
                    except Exception as e:
                        print(f"Error packaging data: {e}")

                zip_path = os.path.join(
                    self.storage_dir, f"session_results_{self.session_id}.zip"
                )

                if os.path.exists(zip_path):
                    try:
                        send_to_server(zip_path, self.session_json)
                        # print(self.session_json)

                    except Exception as e:
                        print(f"Error sending json: {e}")

            QApplication.quit()

    # Used to make sure the current trial's data saved before advancing to avoid race conditions and data loss of fatter prior trials
    def wait_trial_save(self):
        # Add pop-up in case local saving results (mp4, heatmap, csv's) takes a while before the app can close so user doesn't mistake for frozen
        save_msg = QDialog(self)
        save_msg.setWindowTitle("Task Complete!")
        save_msg.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
        )

        save_msg.setFixedSize(400, 100)

        x_pos, y_pos = self.get_dialog_placement_pos(save_msg)
        save_msg.move(x_pos, y_pos)

        layout = QVBoxLayout(save_msg)
        save_label = QLabel("Saving results... This may take a while.")
        save_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        save_label.setStyleSheet("color: white; font-size: 12pt;")
        layout.addWidget(save_label)

        save_msg.show()
        QApplication.processEvents()

        curr_trial = self.trials[self.trial_index - 1]
        curr_task_id = str(curr_trial["taskID"])
        curr_task = self.tasks[curr_task_id]
        curr_measurements = curr_task["measurementOptions"]
        
        # Accounting for future expansion where the user may bave specified "Other" collection mechanisms which we do not handle tracking for
        supported_measurements = {
            "Mouse Movement",
            "Mouse Clicks",
            "Mouse Scrolls",
            "Keyboard Inputs",
            "Screen Recording",
            "Heat Map",
        }
        
        if set(curr_measurements) & supported_measurements:
            # Have to use while loops here or else while waiting the overlaying pop-up will freeze. Using this we can invoke an update to UI
            if not data_storage_complete_event.is_set():
                while not data_storage_complete_event.is_set():
                    time.sleep(0.1)
                    QApplication.processEvents()
                    
            if "Heat Map" in curr_measurements and not heatmap_generation_complete.is_set():
                while not heatmap_generation_complete.is_set():
                    time.sleep(0.1)
                    QApplication.processEvents()

            if recording_active.is_set():
                recording_stop.set()
                while recording_active.is_set():
                    time.sleep(0.1)
                    QApplication.processEvents()

            if (
                "Screen Recording" in curr_measurements
                and not adjustments_finished.is_set()
            ):
                while not adjustments_finished.is_set():
                    time.sleep(0.1)
                    QApplication.processEvents()

        save_msg.close()

    # Ref https://stackoverflow.com/questions/41784521/move-qtwidgets-qtwidget-using-mouse for how to make toolbar draggable
    def mousePressEvent(self, evt):
        self.oldPos = evt.globalPosition().toPoint()

    def mouseMoveEvent(self, evt):
        delta = evt.globalPosition().toPoint() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = evt.globalPosition().toPoint()

    def get_dialog_placement_pos(self, box):
        screen = QApplication.primaryScreen().geometry()
        x_pos = (screen.width() - box.width()) // 2
        y_pos = (screen.height() - box.height()) // 2

        return x_pos, y_pos


class FlaskWrapper:
    def __init__(self, signal_bridge):
        self.app = Flask(__name__)
        self.app.config.from_object(__name__)
        self.signal_bridge = signal_bridge

        # enable CORS w/ specific routes
        CORS(self.app, resources={r"/*": {"origins": "*"}})

        self.app.route("/run_study", methods=["POST"])(self.run_study)

    def run_study(self):
        try:
            session_data = request.get_json()
            # with open("../frontend/public/sample_study.json", "r") as file:
            #     session_data = json.load(file)
            if not session_data:
                return jsonify({"error": "No JSON payload received"}), 400

            print("Session Data Received:", session_data)
            for _, task_data in session_data["tasks"].items():
                if task_data["taskDuration"] == "None":
                    task_data["taskDuration"] = None

            self.signal_bridge.session_data_received.emit(session_data)

            return jsonify({"message": "Session successfully started"}), 200

        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return jsonify({"error": str(e)}), 500

    def start(self):
        self.app.run(host="127.0.0.1", port=5001, debug=False, threaded=True)


def start_flask(flask_app):
    flask_app.start()


if __name__ == "__main__":
    qt_app = QApplication(sys.argv)

    bridge = SignalBridge()

    toolbar = GlobalToolbar(bridge)

    flask_app = FlaskWrapper(bridge)

    server_thread = threading.Thread(target=start_flask, args=(flask_app,), daemon=True)
    server_thread.start()

    sys.exit(qt_app.exec())
