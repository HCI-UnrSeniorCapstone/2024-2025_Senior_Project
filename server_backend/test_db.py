import mysql.connector
import os


def test_db_connection():
    try:
        # Get database credentials from environment
        host = os.getenv("MYSQL_HOST", "localhost")
        user = os.getenv("MYSQL_USER", "root")
        password = os.getenv("MYSQL_PASSWORD", "flatRabbit86^")
        db = os.getenv("MYSQL_DB", "DEVELOP_fulcrum")

        # Connect to the database
        print(f"Connecting to database {db} at {host} with user {user}...")
        conn = mysql.connector.connect(
            host=host, user=user, password=password, database=db
        )
        print("Database connection successful!")

        # Test query to check the study table
        cursor = conn.cursor()
        print("\nTesting queries...")

        # Test study table
        print("\nStudy table query:")
        cursor.execute("SELECT study_id, study_name FROM study")
        print("  Column headers: study_id, study_name")
        for study_id, study_name in cursor:
            print(f"  ID: {study_id}, Name: {study_name}")

        # Test participant_session table
        print("\nParticipant_session table query:")
        cursor.execute(
            "SELECT participant_session_id, participant_id, study_id FROM participant_session LIMIT 5"
        )
        print("  Column headers: participant_session_id, participant_id, study_id")
        for session_id, participant_id, study_id in cursor:
            print(
                f"  Session ID: {session_id}, Participant ID: {participant_id}, Study ID: {study_id}"
            )

        # Test task table
        print("\nTask table query:")
        cursor.execute("SELECT task_id, study_id, task_name FROM task LIMIT 5")
        print("  Column headers: task_id, study_id, task_name")
        for task_id, study_id, task_name in cursor:
            print(f"  Task ID: {task_id}, Study ID: {study_id}, Name: {task_name}")

        # Close connection
        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"Database connection failed: {err}")


if __name__ == "__main__":
    test_db_connection()
