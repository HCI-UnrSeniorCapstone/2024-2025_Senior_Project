#!/bin/bash

# Assuming you're already in the 'server_backend' directory and in venv

# Load specific environment variables from the .env file
export $(grep -E '^RESULTS_BASE_DIR_PATH=|^VUE_APP_BACKEND_PORT=' ../.env | xargs)

# Run the SQL files in the specified order
echo "Running drop_tables.sql..."
mysql < ../sql_database/drop_tables.sql
if [ $? -eq 0 ]; then
    echo "drop_tables.sql completed successfully."
else
    echo "Error running drop_tables.sql."
    exit 1
fi

echo "Running create_tables.sql..."
mysql < ../sql_database/create_tables.sql

if [ $? -eq 0 ]; then
    echo "create_tables.sql completed successfully."
else
    echo "Error running create_tables.sql."
    exit 1
fi

echo "Running inserts_all.sql..."
mysql < ../sql_database/sample_data/insert_all.sql

if [ $? -eq 0 ]; then
    echo "inserts_all.sql completed successfully."
else
    echo "Error running inserts_all.sql."
    exit 1
fi

echo "Removing directories within $RESULTS_BASE_DIR_PATH..."
rm -rf $RESULTS_BASE_DIR_PATH/*

if [ $? -eq 0 ]; then
    echo "Directories removed successfully."
else
    echo "Error removing directories."
fi


# Define the start time
start_time="21:46:20"

start_seconds=$(date -d "$start_time" +%s)
# Initialize seconds offset
seconds_offset=0

# Mouse Movements
for i in {1..1}; do
    file_path="/home/hci/Documents/participants_results/1_study_id/1_participant_session_id/1_session_data_instance_id/${i}.csv"
    mkdir -p "$(dirname "$file_path")"

    for j in {1..250}; do
        seconds_offset=$((seconds_offset + RANDOM % 2))

        # Calculate new time in seconds
        current_seconds=$((start_seconds + seconds_offset))
        # Convert back to HH:MM:SS format
        time=$(date -u -d "1970-01-01 $current_seconds sec" +"%H:%M:%S")

        value1=$(echo "scale=2; $RANDOM/1000" | bc)
        value2=$((RANDOM % 1000))
        value3=$((RANDOM % 500))
        echo "$time,$value1,$value2,$value3" >> "$file_path"
    done

    echo "CSV file created at: $file_path"

    create_session_data_instance="
        USE DEVELOP_fulcrum;
        INSERT INTO session_data_instance(participant_session_id, task_id, measurement_option_id, factor_id)
        VALUES (1, 1, 1, 1);
        "
    mysql -e "$(printf "$create_session_data_instance")"
    # Update session_data_instance with the generated CSV path
    update_path_session_data_instance="USE DEVELOP_fulcrum; UPDATE session_data_instance SET csv_results_path = '%s' WHERE session_data_instance_id = '%s'"

    # Run the update query
    echo "Updating session_data_instance with CSV path..."
    mysql -e "$(printf "$update_path_session_data_instance" "$file_path" "$i")"

    if [ $? -eq 0 ]; then
        echo "session_data_instance updated with CSV path."
    else
        echo "Error updating session_data_instance."
        exit 1
    fi
done

# Mouse Scrolls
for i in {2..2}; do
    file_path="/home/hci/Documents/participants_results/1_study_id/1_participant_session_id/1_session_data_instance_id/${i}.csv"
    mkdir -p "$(dirname "$file_path")"

    for j in {1..250}; do
        seconds_offset=$((seconds_offset + RANDOM % 2))

        # Calculate new time in seconds
        current_seconds=$((start_seconds + seconds_offset))
        # Convert back to HH:MM:SS format
        time=$(date -d @$current_seconds +"%H:%M:%S")

        # Calculate new time
        time=$(date -u -d "1970-01-01 $current_seconds sec" +"%H:%M:%S")

        value1=$(echo "scale=2; $RANDOM/1000" | bc)
        value2=$((400 + RANDOM % 801))
        value3=$((350 + RANDOM % 101))
        # Append to file
        echo "$time,$value1,$value2,$value3" >> "$file_path"
    done

    echo "CSV file created at: $file_path"

    create_session_data_instance="
        USE DEVELOP_fulcrum;
        INSERT INTO session_data_instance(participant_session_id, task_id, measurement_option_id, factor_id)
        VALUES (1, 1, 2, 1);
        "
    mysql -e "$(printf "$create_session_data_instance")"
    # Update session_data_instance with the generated CSV path
    update_path_session_data_instance="USE DEVELOP_fulcrum; UPDATE session_data_instance SET csv_results_path = '%s' WHERE session_data_instance_id = '%s'"

    # Run the update query
    echo "Updating session_data_instance with CSV path..."
    mysql -e "$(printf "$update_path_session_data_instance" "$file_path" "$i")"

    if [ $? -eq 0 ]; then
        echo "session_data_instance updated with CSV path."
    else
        echo "Error updating session_data_instance."
        exit 1
    fi
done

# Mouse Clicks
for i in {3..3}; do
    file_path="/home/hci/Documents/participants_results/1_study_id/1_participant_session_id/1_session_data_instance_id/${i}.csv"
    mkdir -p "$(dirname "$file_path")"

    for j in {1..250}; do
        seconds_offset=$((seconds_offset + RANDOM % 2))

        # Calculate new time in seconds
        current_seconds=$((start_seconds + seconds_offset))
        # Convert back to HH:MM:SS format
        time=$(date -u -d "1970-01-01 $current_seconds sec" +"%H:%M:%S")

        value1=$(echo "scale=2; $RANDOM/1000" | bc)
        value2=$((400 + RANDOM % 801))
        value3=$((350 + RANDOM % 101)) 
        # Append to file
        echo "$time,$value1,$value2,$value3" >> "$file_path"
    done

    echo "CSV file created at: $file_path"

    create_session_data_instance="
        USE DEVELOP_fulcrum;
        INSERT INTO session_data_instance(participant_session_id, task_id, measurement_option_id, factor_id)
        VALUES (1, 1, 3, 1);
        "
    mysql -e "$(printf "$create_session_data_instance")"
    # Update session_data_instance with the generated CSV path
    update_path_session_data_instance="USE DEVELOP_fulcrum; UPDATE session_data_instance SET csv_results_path = '%s' WHERE session_data_instance_id = '%s'"

    # Run the update query
    echo "Updating session_data_instance with CSV path..."
    mysql -e "$(printf "$update_path_session_data_instance" "$file_path" "$i")"

    if [ $? -eq 0 ]; then
        echo "session_data_instance updated with CSV path."
    else
        echo "Error updating session_data_instance."
        exit 1
    fi
done

# Keyboard Inputs
for i in {4..4}; do
    file_path="/home/hci/Documents/participants_results/1_study_id/1_participant_session_id/1_session_data_instance_id/${i}.csv"
    mkdir -p "$(dirname "$file_path")"

    for j in {1..50}; do
        seconds_offset=$((seconds_offset + RANDOM % 2))

        # Calculate new time in seconds
        current_seconds=$((start_seconds + seconds_offset))
        # Convert back to HH:MM:SS format
        time=$(date -u -d "1970-01-01 $current_seconds sec" +"%H:%M:%S")

        value1=$(echo "scale=2; $RANDOM/1000" | bc)
        value2=$((400 + RANDOM % 801))
        value3=$((350 + RANDOM % 101))
        # Append to file
        echo "$time,$value1,$value2,$value3" >> "$file_path"
    done

    echo "CSV file created at: $file_path"

    create_session_data_instance="
        USE DEVELOP_fulcrum;
        INSERT INTO session_data_instance(participant_session_id, task_id, measurement_option_id, factor_id)
        VALUES (1, 1, 4, 1);
        "
    mysql -e "$(printf "$create_session_data_instance")"
    # Update session_data_instance with the generated CSV path
    update_path_session_data_instance="USE DEVELOP_fulcrum; UPDATE session_data_instance SET csv_results_path = '%s' WHERE session_data_instance_id = '%s'"

    # Run the update query
    echo "Updating session_data_instance with CSV path..."
    mysql -e "$(printf "$update_path_session_data_instance" "$file_path" "$i")"

    if [ $? -eq 0 ]; then
        echo "session_data_instance updated with CSV path."
    else
        echo "Error updating session_data_instance."
        exit 1
    fi
done

# Get the Flask port from the environment variable
FLASK_PORT=$VUE_APP_BACKEND_PORT

# Stop any process running on the specified port
# Remove any carriage return (\r) that might exist if editing on Windows
FLASK_PORT=$(echo $FLASK_PORT | tr -d '\r')
MYSQL_HOST=$(echo $MYSQL_HOST | tr -d '\r')

# Find the PID of the process using the port and kill it
FLASK_PID=$(lsof -t -i :$FLASK_PORT)
if [ -z "$FLASK_PID" ]; then
  echo "No process found on port $FLASK_PORT."
else
  kill -9 $FLASK_PID
  echo "Process on port $FLASK_PORT has been stopped."
fi

# Start Flask in the background
echo "Starting Flask app on port $VUE_APP_BACKEND_PORT..."
flask run --host=0.0.0.0 --port=$VUE_APP_BACKEND_PORT --debug