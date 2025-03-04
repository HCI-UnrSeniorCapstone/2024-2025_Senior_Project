#!/bin/bash

# Assuming you're already in the 'server_backend' directory and in venv

# Load specific environment variables from the .env file
export $(grep -E '^RESULTS_BASE_DIR_PATH=|^VUE_APP_BACKEND_PORT=|^MYSQL_DB=' ../.env | xargs)

DB_NAME=$MYSQL_DB
# Remove any carriage return (\r) that might exist if editing on Windows
DB_NAME=$(echo $DB_NAME | tr -d '\r')

# Run the SQL files in the specified order
echo "Running drop_tables.sql..."
mysql $DB_NAME < ../sql_database/drop_tables.sql
if [ $? -eq 0 ]; then
    echo "drop_tables.sql completed successfully."
else
    echo "Error running drop_tables.sql."
    exit 1
fi

echo "Running create_tables.sql..."
mysql $DB_NAME < ../sql_database/create_tables.sql

if [ $? -eq 0 ]; then
    echo "create_tables.sql completed successfully."
else
    echo "Error running create_tables.sql."
    exit 1
fi

echo "Running inserts_all.sql..."
mysql $DB_NAME < ../sql_database/sample_data/insert_all.sql

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


# Insert participants into participant_session dynamically
insert_participant_sessions() {
    #local participant_id=$1
    for i in {1..3}; do
        participant_id=$i
        study_id=1
        # Generate a random ended_at time
        ended_at=$(date -d "NOW + $((RANDOM % 60 + 1)) minute" +"'%Y-%m-%d %H:%M:%S'")
        
        # Generate a random comment
        if (( $i == 1 )); then
            comments="'Participant is too smart. Terminate him'"
            is_valid=0
        else
            comments="'They were very nice'"
            is_valid=1
        fi
        # Generate the SQL INSERT statement for participant_session
        insert_stmt="USE DEVELOP_fulcrum;
        INSERT INTO participant_session (participant_id, study_id, ended_at, comments, is_valid)
        VALUES ($participant_id, $study_id, $ended_at, $comments, $is_valid);"
        
        # Execute the insert statement using mysql
        mysql -e "$(printf "$insert_stmt" "$participant_id" "$study_id" "$ended_at" "$comments" "$is_valid")"

        if [ $? -eq 0 ]; then
            echo "Participant $participant_id inserted successfully."
        else
            echo "Error inserting Participant $participant_id."
            exit 1
        fi
    done
}
insert_participant_sessions
update_database() {
    local file_path=$1 
    local i=$2
    local measurement_option_id=$3
    # Insert the session data instance
    create_session_data_instance="USE DEVELOP_fulcrum;
        INSERT INTO session_data_instance(participant_session_id, task_id, measurement_option_id, factor_id)
        VALUES ($i, 1, $measurement_option_id, $i);
    "

    # Execute the insert and retrieve the last inserted ID in the same session
    session_data_instance_id=$(mysql -e "$create_session_data_instance; SELECT LAST_INSERT_ID();" -s -N)

    if [ $? -eq 0 ]; then
        echo "Last inserted session_data_instance_id: $session_data_instance_id"
    else
        echo "Error inserting into session_data_instance."
        exit 1
    fi

    # Update session_data_instance with the generated CSV path
    update_path_session_data_instance="USE DEVELOP_fulcrum;
    UPDATE session_data_instance SET csv_results_path = '$file_path'
    WHERE session_data_instance_id = '$session_data_instance_id'"

    # Run the update query
    echo "Updating session_data_instance with CSV path..."
    mysql -e "$update_path_session_data_instance"

    if [ $? -eq 0 ]; then
        echo "session_data_instance updated with CSV path."
    else
        echo "Error updating session_data_instance."
        exit 1
    fi
}

# Mouse Movements
generate_mouse_movements() {
    local file_path=$1        
    local start_seconds=$2      
    local seconds_offset=$3
    local num=$4

    for i in {1..25}; do
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
    update_database "$file_path" "$num" "1"
}

# Mouse Scrolls
generate_mouse_scrolls() {
    local file_path=$1        
    local start_seconds=$2      
    local seconds_offset=$3
    local num=$4

    for i in {1..25}; do
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
    update_database "$file_path" "$num" "2"
}

# Mouse clicks
generate_mouse_clicks() {
    local file_path=$1        
    local start_seconds=$2      
    local seconds_offset=$3
    local num=$4

    for i in {1..25}; do
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
    update_database "$file_path" "$num" "3"
}

generate_keyboard_inputs() {
    local file_path=$1        
    local start_seconds=$2      
    local seconds_offset=$3
    local num=$4

    for i in {1..25}; do
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
    update_database "$file_path" "$num" "4"
}
# Make data for the 3 participants in the database
csv_counter=1
for i in {1..3}; do
    file_path_dir="/home/hci/Documents/participants_results/1_study_id/${i}_participant_session_id/"
    mkdir -p "$(dirname "$file_path_dir")"
    index=$i
    #insert_participant_sessions "$i"

    #for j in {1..4}; do
        j=1 
        file_path="${file_path_dir}${csv_counter}_session_data_instance_id/${csv_counter}.csv"
        mkdir -p "$(dirname "$file_path")"
        generate_mouse_movements "$file_path" "$start_seconds" "$seconds_offset" "$index"
        csv_counter=$((csv_counter + 1))

        j=2
        file_path="${file_path_dir}${csv_counter}_session_data_instance_id/${csv_counter}.csv"
        mkdir -p "$(dirname "$file_path")"
        generate_mouse_scrolls "$file_path" "$start_seconds" "$seconds_offset" "$index"
        csv_counter=$((csv_counter + 1))

        j=3
        file_path="${file_path_dir}${csv_counter}_session_data_instance_id/${csv_counter}.csv"
        mkdir -p "$(dirname "$file_path")"
        generate_mouse_clicks "$file_path" "$start_seconds" "$seconds_offset" "$index"
        csv_counter=$((csv_counter + 1))

        j=4
        file_path="${file_path_dir}${csv_counter}_session_data_instance_id/${csv_counter}.csv"
        mkdir -p "$(dirname "$file_path")"
        generate_keyboard_inputs "$file_path" "$start_seconds" "$seconds_offset" "$index"
        csv_counter=$((csv_counter + 1))
    #done
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