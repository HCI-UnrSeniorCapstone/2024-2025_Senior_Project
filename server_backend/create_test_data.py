#!/usr/bin/env python3
"""
Script to create test data for analytics testing.
This will create a study with fake participants, sessions, trials, and data.
"""

import MySQLdb
import os
import random
import datetime
import argparse
import sys
from datetime import timedelta


def get_database_connection():
    """Get connection to the database using environment variables."""
    db_host = os.environ.get("MYSQL_HOST")
    db_user = os.environ.get("MYSQL_USER")
    db_pass = os.environ.get("MYSQL_PASSWORD")
    db_name = os.environ.get("MYSQL_DB")

    if not all([db_host, db_user, db_pass, db_name]):
        print("Error: Database environment variables not set.")
        print("Please set MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DB")
        sys.exit(1)

    try:
        connection = MySQLdb.connect(
            host=db_host, user=db_user, passwd=db_pass, db=db_name
        )
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        sys.exit(1)


def create_test_study(connection, owner_user_id, study_name=None):
    """Create a test study owned by the specified user."""
    cursor = connection.cursor()

    # Default study name if not provided
    if not study_name:
        study_name = (
            f"Test Study - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    try:
        # Get a valid study_design_type_id
        cursor.execute("SELECT study_design_type_id FROM study_design_type LIMIT 1")
        study_design_type_id = cursor.fetchone()[0]

        # Create the study
        cursor.execute(
            """
            INSERT INTO study (study_name, study_description, expected_participants, study_design_type_id) 
            VALUES (%s, %s, %s, %s)
        """,
            (
                study_name,
                "Test study created for analytics testing",
                20,  # Expected participants
                study_design_type_id,
            ),
        )
        study_id = cursor.lastrowid

        # Get the owner role type
        cursor.execute(
            "SELECT study_user_role_type_id FROM study_user_role_type WHERE study_user_role_description = 'Owner'"
        )
        result = cursor.fetchone()
        if not result:
            # Try to get any role if "Owner" doesn't exist
            cursor.execute(
                "SELECT study_user_role_type_id FROM study_user_role_type LIMIT 1"
            )
            result = cursor.fetchone()

        owner_role_id = result[0]

        # Assign the user as owner
        cursor.execute(
            """
            INSERT INTO study_user_role (user_id, study_id, study_user_role_type_id)
            VALUES (%s, %s, %s)
        """,
            (owner_user_id, study_id, owner_role_id),
        )

        connection.commit()
        print(f"Created new study '{study_name}' with ID {study_id}")
        return study_id

    except Exception as e:
        connection.rollback()
        print(f"Error creating study: {e}")
        return None


def create_test_tasks(connection, study_id, num_tasks=2):
    """Create test tasks for the study."""
    cursor = connection.cursor()
    task_ids = []

    task_names = [
        "Memory Recall",
        "Pattern Recognition",
        "Reaction Time",
        "Attention Test",
        "Cognitive Load",
        "Visual Search",
    ]

    try:
        for i in range(num_tasks):
            task_name = task_names[i % len(task_names)]
            task_desc = f"Description for {task_name} task"
            task_directions = f"Directions for completing the {task_name} task"
            duration = random.uniform(60, 300)  # Between 1-5 minutes

            cursor.execute(
                """
                INSERT INTO task (study_id, task_name, task_description, task_directions, duration)
                VALUES (%s, %s, %s, %s, %s)
            """,
                (study_id, task_name, task_desc, task_directions, duration),
            )

            task_ids.append(cursor.lastrowid)

        connection.commit()
        print(f"Created {len(task_ids)} tasks for study {study_id}")
        return task_ids

    except Exception as e:
        connection.rollback()
        print(f"Error creating tasks: {e}")
        return []


def create_test_factors(connection, study_id, num_factors=2):
    """Create test factors for the study."""
    cursor = connection.cursor()
    factor_ids = []

    factor_names = [
        "Control Group",
        "Experimental Group",
        "High Complexity",
        "Low Complexity",
        "Time Limited",
        "Unlimited Time",
    ]

    try:
        for i in range(num_factors):
            factor_name = factor_names[i % len(factor_names)]
            factor_desc = f"Description for {factor_name} factor"

            cursor.execute(
                """
                INSERT INTO factor (study_id, factor_name, factor_description)
                VALUES (%s, %s, %s)
            """,
                (study_id, factor_name, factor_desc),
            )

            factor_ids.append(cursor.lastrowid)

        connection.commit()
        print(f"Created {len(factor_ids)} factors for study {study_id}")
        return factor_ids

    except Exception as e:
        connection.rollback()
        print(f"Error creating factors: {e}")
        return []


def create_test_measurement_options(connection, num_options=3):
    """Create test measurement options if they don't exist."""
    cursor = connection.cursor()
    measurement_option_ids = []

    option_names = [
        "Mouse Movement",
        "Mouse Clicks",
        "Keyboard Input",
        "Eye Tracking",
        "Screen Recording",
    ]

    try:
        # Check which options already exist
        cursor.execute(
            "SELECT measurement_option_id, measurement_option_name FROM measurement_option"
        )
        existing_options = {row[1]: row[0] for row in cursor.fetchall()}

        # Create any needed options
        for i in range(min(num_options, len(option_names))):
            option_name = option_names[i]

            if option_name in existing_options:
                measurement_option_ids.append(existing_options[option_name])
            else:
                cursor.execute(
                    """
                    INSERT INTO measurement_option (measurement_option_name)
                    VALUES (%s)
                """,
                    (option_name,),
                )

                measurement_option_ids.append(cursor.lastrowid)

        connection.commit()
        print(f"Using {len(measurement_option_ids)} measurement options")
        return measurement_option_ids

    except Exception as e:
        connection.rollback()
        print(f"Error creating measurement options: {e}")
        return []


def create_test_participants(connection, study_id, num_participants=5):
    """Create test participants and sessions for the study."""
    cursor = connection.cursor()
    participant_session_ids = []

    try:
        # Get gender types
        cursor.execute("SELECT gender_type_id FROM gender_type LIMIT 3")
        gender_ids = [row[0] for row in cursor.fetchall()]

        # Get education types
        cursor.execute(
            "SELECT highest_education_type_id FROM highest_education_type LIMIT 3"
        )
        education_ids = [row[0] for row in cursor.fetchall()]

        # Create participants
        for i in range(num_participants):
            # Create participant
            age = random.randint(18, 65)
            gender_id = random.choice(gender_ids) if gender_ids else None
            education_id = random.choice(education_ids) if education_ids else None
            tech_competence = random.randint(1, 10)

            cursor.execute(
                """
                INSERT INTO participant (age, gender_type_id, highest_education_type_id, technology_competence)
                VALUES (%s, %s, %s, %s)
            """,
                (age, gender_id, education_id, tech_competence),
            )

            participant_id = cursor.lastrowid

            # Create participant session
            start_date = datetime.datetime.now() - timedelta(days=random.randint(0, 30))
            end_date = start_date + timedelta(minutes=random.randint(30, 120))

            cursor.execute(
                """
                INSERT INTO participant_session (participant_id, study_id, created_at, ended_at)
                VALUES (%s, %s, %s, %s)
            """,
                (participant_id, study_id, start_date, end_date),
            )

            participant_session_ids.append(cursor.lastrowid)

        connection.commit()
        print(
            f"Created {len(participant_session_ids)} participants with sessions for study {study_id}"
        )
        return participant_session_ids

    except Exception as e:
        connection.rollback()
        print(f"Error creating participants and sessions: {e}")
        return []


def generate_mouse_movement_data(duration_seconds, frequency=10):
    """Generate synthetic mouse movement data for a trial.

    Args:
        duration_seconds: Length of the trial in seconds
        frequency: Number of data points per second

    Returns:
        List of (time, running_time, x, y) data points
    """
    data = []

    # Start time (just use a dummy time)
    start_time = datetime.datetime.now().replace(microsecond=0)

    # Current position
    current_x = random.randint(500, 1500)
    current_y = random.randint(300, 700)

    # Generate data points
    total_points = int(duration_seconds * frequency)
    for i in range(total_points):
        running_time = i / frequency

        # Update time
        point_time = start_time + timedelta(seconds=running_time)

        # Move the mouse in a somewhat realistic way (small movements with occasional jumps)
        if random.random() < 0.1:  # 10% chance of a bigger jump
            current_x += random.randint(-200, 200)
            current_y += random.randint(-100, 100)
        else:
            current_x += random.randint(-20, 20)
            current_y += random.randint(-15, 15)

        # Keep within screen bounds
        current_x = max(0, min(current_x, 1920))
        current_y = max(0, min(current_y, 1080))

        # Add to dataset
        data.append(
            (
                point_time.strftime("%H:%M:%S"),
                f"{running_time:.2f}",
                current_x,
                current_y,
            )
        )

    return data


def generate_keyboard_data(duration_seconds, typing_speed=2):
    """Generate synthetic keyboard input data.

    Args:
        duration_seconds: Length of the trial in seconds
        typing_speed: Average keypresses per second

    Returns:
        List of (time, running_time, key) data points
    """
    data = []

    # Start time
    start_time = datetime.datetime.now().replace(microsecond=0)

    # Generate data points
    total_keypresses = int(duration_seconds * typing_speed)

    # Possible keys (simplified)
    alphabet = list("abcdefghijklmnopqrstuvwxyz")
    special_keys = ["Key.space", "Key.backspace", "Key.shift", "Key.enter"]
    all_keys = alphabet + special_keys

    for i in range(total_keypresses):
        # Randomize timing slightly
        running_time = i / typing_speed + random.uniform(-0.1, 0.3)
        running_time = max(0, running_time)  # Ensure not negative

        # Update time
        point_time = start_time + timedelta(seconds=running_time)

        # Pick a random key with weighted probability
        if random.random() < 0.2:  # 20% chance of special key
            key = random.choice(special_keys)
        else:
            key = random.choice(alphabet)

        # Add to dataset
        data.append((point_time.strftime("%H:%M:%S"), f"{running_time:.2f}", key))

    # Sort by running time to ensure proper time ordering
    data.sort(key=lambda x: float(x[1]))

    return data


def generate_mouse_clicks_data(duration_seconds, click_frequency=0.5):
    """Generate synthetic mouse click data.

    Args:
        duration_seconds: Length of the trial in seconds
        click_frequency: Average clicks per second

    Returns:
        List of (time, running_time, x, y) data points
    """
    data = []

    # Start time
    start_time = datetime.datetime.now().replace(microsecond=0)

    # Generate data points
    total_clicks = int(duration_seconds * click_frequency)

    for i in range(total_clicks):
        # Distribute clicks throughout the duration
        running_time = random.uniform(0, duration_seconds)

        # Update time
        point_time = start_time + timedelta(seconds=running_time)

        # Random screen position
        x = random.randint(0, 1920)
        y = random.randint(0, 1080)

        # Add to dataset
        data.append((point_time.strftime("%H:%M:%S"), f"{running_time:.2f}", x, y))

    # Sort by running time to ensure proper time ordering
    data.sort(key=lambda x: float(x[1]))

    return data


def write_csv_file(data, headers, filepath):
    """Write data to a CSV file, creating directories as needed.

    Args:
        data: List of data tuples
        headers: List of column headers
        filepath: Path to write the file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w") as f:
            # Write headers
            f.write(",".join(headers) + "\n")

            # Write data
            for row in data:
                f.write(",".join(str(val) for val in row) + "\n")

        return True
    except Exception as e:
        print(f"Error writing CSV file {filepath}: {e}")
        return False


def create_test_trials(
    connection, participant_session_ids, task_ids, factor_ids, measurement_option_ids
):
    """Create test trials and session data for participant sessions."""
    cursor = connection.cursor()
    trial_count = 0

    # Directory for test data files
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_data"))
    os.makedirs(data_dir, exist_ok=True)
    print(f"Storing test data files in: {data_dir}")

    # Get measurement option names
    cursor.execute(
        "SELECT measurement_option_id, measurement_option_name FROM measurement_option"
    )
    measurement_options = {row[0]: row[1] for row in cursor.fetchall()}

    # Get task names
    cursor.execute("SELECT task_id, task_name FROM task")
    task_names = {row[0]: row[1] for row in cursor.fetchall()}

    # Get factor names
    cursor.execute("SELECT factor_id, factor_name FROM factor")
    factor_names = {row[0]: row[1] for row in cursor.fetchall()}

    created_data_files = []

    try:
        for session_id in participant_session_ids:
            # Get session timestamp to base trial times on
            cursor.execute(
                "SELECT created_at, ended_at, study_id FROM participant_session WHERE participant_session_id = %s",
                (session_id,),
            )
            session_start, session_end, study_id = cursor.fetchone()

            # Calculate time range for trials
            if session_end:
                session_length = (session_end - session_start).total_seconds()
            else:
                session_length = 3600  # Default 1 hour if no end time

            time_per_trial = session_length / (len(task_ids) * len(factor_ids))

            # Create session directory
            session_dir = os.path.join(
                data_dir, f"{study_id}_study_id", f"{session_id}_participant_session_id"
            )
            os.makedirs(session_dir, exist_ok=True)

            # Create trials for each task and factor combination
            for task_id in task_ids:
                for factor_id in factor_ids:
                    # Create trial with randomized completion status
                    trial_start = session_start + timedelta(
                        seconds=random.uniform(0, session_length * 0.8)
                    )
                    completed = random.random() > 0.2  # 80% completion rate

                    if completed:
                        trial_end = trial_start + timedelta(
                            seconds=random.uniform(30, time_per_trial)
                        )
                        trial_duration = (trial_end - trial_start).total_seconds()
                    else:
                        trial_end = None
                        trial_duration = random.uniform(
                            30, 120
                        )  # Assume some activity before abandonment

                    cursor.execute(
                        """
                        INSERT INTO trial (participant_session_id, task_id, factor_id, started_at, ended_at)
                        VALUES (%s, %s, %s, %s, %s)
                    """,
                        (session_id, task_id, factor_id, trial_start, trial_end),
                    )

                    trial_id = cursor.lastrowid
                    trial_count += 1

                    # Create trial directory
                    trial_dir = os.path.join(session_dir, f"{trial_id}_trial_id")
                    os.makedirs(trial_dir, exist_ok=True)

                    # Generate data files for this trial
                    task_name = task_names.get(task_id, f"Task_{task_id}")
                    factor_name = factor_names.get(factor_id, f"Factor_{factor_id}")

                    # Create session data instances for selected measurement options
                    for option_id in measurement_option_ids:
                        option_name = measurement_options.get(
                            option_id, f"Option_{option_id}"
                        )

                        # Insert the session data instance record first to get the ID
                        cursor.execute(
                            """
                            INSERT INTO session_data_instance (trial_id, measurement_option_id)
                            VALUES (%s, %s)
                        """,
                            (trial_id, option_id),
                        )

                        # Get the session data instance ID
                        session_data_instance_id = cursor.lastrowid

                        # Create the file with the right name
                        file_name = f"{session_data_instance_id}.csv"
                        filepath = os.path.join(trial_dir, file_name)

                        # Generate appropriate data based on measurement type
                        if "Mouse Movement" in option_name:
                            headers = ["Time", "running_time", "x", "y"]
                            data = generate_mouse_movement_data(trial_duration)
                            success = write_csv_file(data, headers, filepath)

                        elif "Keyboard" in option_name:
                            headers = ["Time", "running_time", "keys"]
                            data = generate_keyboard_data(trial_duration)
                            success = write_csv_file(data, headers, filepath)

                        elif "Mouse Clicks" in option_name:
                            headers = ["Time", "running_time", "x", "y"]
                            data = generate_mouse_clicks_data(trial_duration)
                            success = write_csv_file(data, headers, filepath)

                        else:
                            # For other types, create an empty file as placeholder
                            with open(filepath, "w") as f:
                                f.write(f"# Test data for {option_name}\n")
                            success = True

                        if success:
                            created_data_files.append(filepath)

                        # Update the database with the file path
                        cursor.execute(
                            """
                            UPDATE session_data_instance 
                            SET results_path = %s
                            WHERE session_data_instance_id = %s
                        """,
                            (filepath, session_data_instance_id),
                        )

        connection.commit()
        print(f"Created {trial_count} trials with data instances")
        print(f"Generated {len(created_data_files)} data files")
        return trial_count

    except Exception as e:
        connection.rollback()
        print(f"Error creating trials and data: {e}")
        return 0


def create_complete_test_dataset(
    user_id, study_name=None, num_participants=5, num_tasks=2, num_factors=2
):
    """Create a complete test dataset for a user."""
    print(f"Creating test dataset for user ID {user_id}")

    connection = get_database_connection()

    # Create study
    study_id = create_test_study(connection, user_id, study_name)
    if not study_id:
        connection.close()
        return False

    # Create tasks
    task_ids = create_test_tasks(connection, study_id, num_tasks)
    if not task_ids:
        connection.close()
        return False

    # Create factors
    factor_ids = create_test_factors(connection, study_id, num_factors)
    if not factor_ids:
        connection.close()
        return False

    # Create or get measurement options
    measurement_option_ids = create_test_measurement_options(connection)
    if not measurement_option_ids:
        connection.close()
        return False

    # Create participants with sessions
    participant_session_ids = create_test_participants(
        connection, study_id, num_participants
    )
    if not participant_session_ids:
        connection.close()
        return False

    # Create trials and data
    trial_count = create_test_trials(
        connection,
        participant_session_ids,
        task_ids,
        factor_ids,
        measurement_option_ids,
    )

    # Link tasks to measurement options
    cursor = connection.cursor()
    try:
        for task_id in task_ids:
            for option_id in measurement_option_ids:
                cursor.execute(
                    """
                    INSERT IGNORE INTO task_measurement (task_id, measurement_option_id)
                    VALUES (%s, %s)
                """,
                    (task_id, option_id),
                )
        connection.commit()
    except Exception as e:
        connection.rollback()
        print(f"Error linking tasks to measurement options: {e}")

    # Summarize creation
    print("\nTest Dataset Creation Summary:")
    print(f"- Created study '{study_name or 'Test Study'}' with ID {study_id}")
    print(f"- Added {len(task_ids)} tasks and {len(factor_ids)} factors")
    print(f"- Created {len(participant_session_ids)} participant sessions")
    print(f"- Generated {trial_count} trials with data")
    print(f"- Used {len(measurement_option_ids)} measurement options")

    connection.close()
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create test data for analytics testing"
    )
    parser.add_argument("user_id", type=int, help="User ID to own the test study")
    parser.add_argument(
        "--name", "-n", type=str, help="Study name (defaults to auto-generated)"
    )
    parser.add_argument(
        "--participants",
        "-p",
        type=int,
        default=5,
        help="Number of participants to create",
    )
    parser.add_argument(
        "--tasks", "-t", type=int, default=2, help="Number of tasks to create"
    )
    parser.add_argument(
        "--factors", "-f", type=int, default=2, help="Number of factors to create"
    )

    args = parser.parse_args()

    success = create_complete_test_dataset(
        args.user_id, args.name, args.participants, args.tasks, args.factors
    )

    if success:
        print("\nTest data creation completed successfully!")
    else:
        print("\nTest data creation failed.")
        sys.exit(1)
