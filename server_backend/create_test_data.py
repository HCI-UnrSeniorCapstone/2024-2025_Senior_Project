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


def create_test_trials(
    connection, participant_session_ids, task_ids, factor_ids, measurement_option_ids
):
    """Create test trials and session data for participant sessions."""
    cursor = connection.cursor()
    trial_count = 0

    try:
        for session_id in participant_session_ids:
            # Get session timestamp to base trial times on
            cursor.execute(
                "SELECT created_at, ended_at FROM participant_session WHERE participant_session_id = %s",
                (session_id,),
            )
            session_start, session_end = cursor.fetchone()

            # Calculate time range for trials
            if session_end:
                session_length = (session_end - session_start).total_seconds()
            else:
                session_length = 3600  # Default 1 hour if no end time

            time_per_trial = session_length / (len(task_ids) * len(factor_ids))

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
                    else:
                        trial_end = None

                    cursor.execute(
                        """
                        INSERT INTO trial (participant_session_id, task_id, factor_id, started_at, ended_at)
                        VALUES (%s, %s, %s, %s, %s)
                    """,
                        (session_id, task_id, factor_id, trial_start, trial_end),
                    )

                    trial_id = cursor.lastrowid
                    trial_count += 1

                    # Create session data instances for selected measurement options
                    for option_id in measurement_option_ids:
                        # Use a dummy file path that would point to where data would be stored
                        results_path = f"/tmp/test_data/session_{session_id}/trial_{trial_id}/data_{option_id}.csv"

                        cursor.execute(
                            """
                            INSERT INTO session_data_instance (trial_id, measurement_option_id, results_path)
                            VALUES (%s, %s, %s)
                        """,
                            (trial_id, option_id, results_path),
                        )

        connection.commit()
        print(f"Created {trial_count} trials with data instances")
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
