# Purpose: Holds all UI and functionality related to Global Toolbar


import sys
import json
import threading
import os
import time

# PyQt libraries
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QMessageBox,
)
from tracking.tracking import conduct_trial
from tracking.utility.file_management import package_session_results, get_save_dir
from tracking.utility.measure import (
    pause_event,
    stop_event,
    data_storage_complete_event,
)


# Ref https://www.pythonguis.com/tutorials/pyqt6-widgets/
class GlobalToolbar(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_session()
        self.trial_index = 0
        self.oldPos = None  # track toolbar pos on screen
        self.session_paused = False
        self.countdown = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)

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
            button.clicked.connect(action)
            vbox.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)

            tool_desc = QLabel(label)
            tool_desc.setStyleSheet("color: white; font-size: 10px")
            tool_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vbox.addWidget(tool_desc)

            return vbox, button

        # Start button
        start_layout, self.start_btn = create_btn(
            "./icons/start.svg", "Start", self.start_session
        )
        layout.addLayout(start_layout)

        # Pause/Resume button
        pause_layout, self.pause_btn = create_btn(
            "./icons/pause.svg", "Pause/Resume", self.pause_session
        )
        layout.addLayout(pause_layout)
        self.pause_btn.setEnabled(False)  # starts disabled

        # Next button
        next_layout, self.next_btn = create_btn(
            "./icons/next.svg", "Next Task", self.move_next_task
        )
        layout.addLayout(next_layout)
        self.next_btn.setEnabled(False)  # starts disabled

        # Timer countdown
        self.timer_label = QLabel("No Time Limit")
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

        # Help button
        help_layout, self.help_btn = create_btn(
            "./icons/help.svg", "Help", self.open_help_menu
        )
        layout.addLayout(help_layout)

        # Quit button
        quit_layout, self.quit_btn = create_btn(
            "./icons/quit.svg", "Quit", self.leave_session
        )
        layout.addLayout(quit_layout)

    def load_session(self):
        # Uses a sample json found in frontend/public for easier debugging and development so we dont have to initiate session from Vue
        with open("../frontend/public/sample_study.json", "r") as file:
            data = json.load(file)
        self.session_id, self.tasks, self.factors, self.trials = (
            self.parse_study_details(data)
        )

    # Getting all study info parsed
    def parse_study_details(self, data):
        session_id = data.get("participantSessId")
        tasks = data.get("tasks", {})
        factors = data.get("factors", {})
        trials = data.get("trials", [])
        return session_id, tasks, factors, trials

    def start_session(self):
        self.move_next_task()  # start btn treated same way as moving to next task essentially

    def move_next_task(self):
        if self.trial_index > 0:
            stop_event.set()
            pause_event.clear()
            data_storage_complete_event.wait()

        trial = self.trials[self.trial_index]
        task_id = str(trial["taskID"])
        task = self.tasks[task_id]
        task_dirs = task["taskDirections"]
        task_dur = task.get("taskDuration", None)
        factor_id = str(trial["factorID"])
        factor = self.factors[factor_id]

        # Show a similar pop-up as Mbox before when the participant clicks on the next task arrow, providing general directions
        trial_msg = QMessageBox()
        trial_msg.setWindowTitle(f"Task {self.trial_index + 1}")
        if task_dur:
            trial_msg.setText(f"Directions: {task_dirs}\nDuration: {task_dur} minutes")
        else:
            trial_msg.setText(f"Directions: {task_dirs}\nDuration: No time limit")
        trial_msg.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )

        if trial_msg.exec() == QMessageBox.StandardButton.Ok:
            self.start_btn.setEnabled(False)  # disable for the rest of the session
            self.session_paused = False
            pause_event.set()  # start tracking
            stop_event.clear()
            data_storage_complete_event.clear()

            trial_thread = threading.Thread(
                target=conduct_trial, args=(self.session_id, task, factor)
            )
            trial_thread.start()

            if task_dur:
                self.initiate_countdown(int(float(task_dur) * 1))
            else:
                self.next_btn.setEnabled(True)
                self.pause_btn.setEnabled(True)

            if (
                self.trial_index == len(self.trials) - 1
            ):  # cannot go to next task bc there is not one
                self.next_btn.setEnabled(False)

            self.trial_index += 1
            self.progress.setText(f"Task {self.trial_index} of {len(self.trials)}")

    # Starts the countdown timer
    def initiate_countdown(self, duration):
        self.next_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.countdown = duration
        self.format_countdown()
        self.timer.start(1000)

    # Updates the countdown (decreasing by 1 sec)
    def update_countdown(self):
        if self.countdown > 0 and not self.session_paused:
            self.countdown -= 1
            self.format_countdown()
        else:
            self.timer.stop()
            self.pause_btn.setEnabled(
                False
            )  # disable pause when task is at its end since no tracking occuring

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
            pause_event.clear()
            self.timer.stop()
        else:
            print("session resumed")
            pause_event.set()
            if self.countdown > 0:
                self.timer.start(1000)
            else:
                pause_event.set()

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
                data_storage_complete_event.wait(timeout=5)

                if os.path.exists(
                    os.path.join(get_save_dir(), f"Session_{self.session_id}")
                ):
                    try:
                        package_session_results(self.session_id)
                    except Exception as e:
                        print(f"Error packaging data: {e}")

            QApplication.quit()

    # Ref https://stackoverflow.com/questions/41784521/move-qtwidgets-qtwidget-using-mouse for how to make toolbar draggable
    def mousePressEvent(self, evt):
        self.oldPos = evt.globalPosition().toPoint()

    def mouseMoveEvent(self, evt):
        delta = evt.globalPosition().toPoint() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = evt.globalPosition().toPoint()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    toolbar = GlobalToolbar()
    toolbar.show()
    app.exec()
