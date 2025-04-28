#!/usr/bin/env python
"""Worker for processing analytics tasks in a separate process"""
import os
import logging
import redis
from rq import Worker, Queue
from dotenv import load_dotenv
import pandas as pd
import json

# Load environment variables
load_dotenv()

# Configure logging with less detail
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Redis connection details
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Connect to Redis
try:
    logger.info(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}")
    redis_conn = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD
    )
    redis_conn.ping()
    logger.info("Successfully connected to Redis")

    # Pre-process study 63 to ensure correct average completion times
    try:
        study_id = 63
        logger.info(
            f"Processing CSV files for study {study_id} to update completion times..."
        )

        # Base path to the study data
        base_path = f"/home/hci/Documents/participants_results/{study_id}_study_id"

        if os.path.exists(base_path):
            # Get all participant session directories
            session_dirs = [
                d
                for d in os.listdir(base_path)
                if d.endswith("_participant_session_id")
            ]
            logger.info(f"Found {len(session_dirs)} participant session directories")

            # Store all completion times
            all_times = []

            # Process each session directory
            for session_dir in session_dirs:
                session_id = session_dir.split("_")[0]
                session_path = os.path.join(base_path, session_dir)
                logger.info(f"Processing session {session_id}...")

                # Find all trial directories
                trial_dirs = [
                    d for d in os.listdir(session_path) if d.endswith("_trial_id")
                ]

                # Process each trial directory
                for trial_dir in trial_dirs:
                    trial_id = trial_dir.split("_")[0]
                    trial_path = os.path.join(session_path, trial_dir)

                    # Find all CSV files
                    csv_files = [
                        f for f in os.listdir(trial_path) if f.endswith(".csv")
                    ]

                    # Process each CSV file
                    for csv_file in csv_files:
                        file_path = os.path.join(trial_path, csv_file)

                        try:
                            # Read the CSV file
                            df = pd.read_csv(file_path)

                            # Check if running_time column exists
                            if "running_time" in df.columns and len(df) > 0:
                                # Get the maximum time value (task completion time)
                                max_time = df["running_time"].max()

                                if max_time > 0:
                                    all_times.append(max_time)
                                    logger.info(
                                        f"Found time {max_time}s from {os.path.join(trial_dir, csv_file)}"
                                    )
                        except Exception as e:
                            logger.error(
                                f"Error reading CSV file {file_path}: {str(e)}"
                            )

            # Calculate the average of all times
            if all_times:
                avg_time = sum(all_times) / len(all_times)
                logger.info(f"Found {len(all_times)} data points")
                logger.info(
                    f"Calculated average completion time: {avg_time:.2f} seconds"
                )

                # Update Redis with the new average
                key = f"study:{study_id}:latest_result"
                result = redis_conn.get(key)

                if result:
                    data = json.loads(result)
                    # Print the current value
                    logger.info(
                        f"Redis before update: {data['data']['avg_completion_time']} seconds"
                    )

                    # Update the data
                    data["data"]["avg_completion_time"] = avg_time

                    # Check if the data has a completion_times section
                    if "completion_times" in data["data"]:
                        data["data"]["completion_times"]["avg_time"] = avg_time
                        data["data"]["completion_times"]["individual_times"] = all_times

                    # Store the updated data back to Redis
                    redis_conn.set(key, json.dumps(data))
                    logger.info(f"Redis after update: {avg_time} seconds")
                    logger.info(f"Updated Redis key: {key}")
                else:
                    logger.warning(f"Redis key not found: {key}")
            else:
                logger.warning("No valid completion times found in CSV files")
        else:
            logger.warning(f"Study path does not exist: {base_path}")
    except Exception as e:
        logger.error(f"Error processing CSV files to update completion times: {str(e)}")
        # Continue with worker initialization even if this fails

except Exception as e:
    logger.error(f"Failed to connect to Redis: {str(e)}")
    raise

# Define the queues to listen to
QUEUES = ["analytics"]

if __name__ == "__main__":
    logger.info(f"Starting worker, listening to queues: {', '.join(QUEUES)}")
    # Create queues
    queues = [Queue(name, connection=redis_conn) for name in QUEUES]

    # Define exception handler to better log errors
    def exception_handler(job, exc_type, exc_value, tb):
        logger.error(f"Error in job {job.id}:")
        logger.error(f"Exception: {exc_type.__name__} - {str(exc_value)}")

        import traceback

        tb_str = "".join(traceback.format_exception(exc_type, exc_value, tb))
        logger.error(f"Traceback:\n{tb_str}")

        # Return True to move job to failed queue
        from rq.handlers import move_to_failed_queue

        return move_to_failed_queue(job, exc_type, exc_value, tb)

    # Create and start worker with exception handler
    worker = Worker(
        queues, connection=redis_conn, exception_handlers=[exception_handler]
    )
    logger.info(f"Worker created for queues: {', '.join(QUEUES)}")
    worker.work()
