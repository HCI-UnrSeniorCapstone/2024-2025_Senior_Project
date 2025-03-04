#!/bin/bash

# Load specific environment variables from the .env file
export $(grep -E '^RESULTS_BASE_DIR_PATH=|^VUE_APP_BACKEND_PORT=|^MYSQL_DB=' ../.env | xargs)

DB_NAME=$(echo $MYSQL_DB | tr -d '\r')

# Record script running time
start_time=$(date +%s)

run_sql_file() {
    local file=$1
    echo "Running $file..." >&2
    mysql $DB_NAME < "../sql_database/$file"
    if [ $? -eq 0 ]; then
        echo "$file completed successfully." >&2
    else
        echo "Error running $file." >&2
        exit 1
    fi
}

run_sql_file "drop_tables.sql"
run_sql_file "create_tables.sql"
run_sql_file "sample_data/insert_all.sql"

clear_results_directory() {
    echo "Removing directories within $RESULTS_BASE_DIR_PATH..." >&2
    rm -rf "$RESULTS_BASE_DIR_PATH/*"
    if [ $? -eq 0 ]; then
        echo "Directories removed successfully." >&2
    else
        echo "Error removing directories." >&2
    fi
}

clear_results_directory

create_data_path_participant() {
    local study_id=$1
    local participant_id=$2
    local base_path="$RESULTS_BASE_DIR_PATH/${study_id}_study_id/${participant_id}_participant_session_id"
    mkdir -p "$base_path"
    echo "$base_path"
}

create_data_path_trial() {
    local trial_id=$1
    local participant_id=$2
    local study_id=$3
    local base_path="$RESULTS_BASE_DIR_PATH/${study_id}_study_id/${participant_id}_participant_session_id/${trial_id}_trial_id"
    mkdir -p "$base_path"
    echo "$base_path"
}

update_database_participant_session() {
    local participant_id=$1
    local ended_at=$(date -d "NOW + $((RANDOM % 60 + 1)) minute" +"'%Y-%m-%d %H:%M:%S'")
    local comments="'Good Data'"
    local is_valid=1

    # Generate the SQL INSERT statement for participant_session
    insert_participant_session="USE $DB_NAME;
    INSERT INTO participant_session (participant_id, study_id, ended_at, comments, is_valid)
    VALUES ($participant_id, $study_id, $ended_at, $comments, $is_valid);"
    
    # Execute the insert statement for participant_session
    participant_session_id=$(mysql -e "$insert_participant_session; SELECT LAST_INSERT_ID();" -s -N)

    # Check for successful execution of participant_session insert
    if [ $? -eq 0 ]; then
        echo "Participant Session $participant_session_id inserted successfully." >&2
    else
        echo "ERROR: Inserting Participant Session $participant_session_id." >&2
        exit 1
    fi

    # Check if participant_session_id is valid
    if [ -z "$participant_session_id" ]; then
        echo "ERROR: Failed to retrieve participant_session_id $participant_session_id" >&2
        exit 1
    fi

    echo "$participant_session_id"
}

update_database_trial() {
    local path=$1
    local participant_id=$2
    local study_id=$3
    local csv_counter=$4

    # Now insert into the trial table
    local task_id=1
    local factor_id=1
    insert_trial="USE $DB_NAME;
    INSERT INTO trial (participant_session_id, task_id, factor_id)
    VALUES ($participant_session_id, $task_id, $factor_id);"

    trial_id=$(mysql -e "$insert_trial; SELECT LAST_INSERT_ID();" -s -N)

    # Check for successful trial insert 
    if [ $? -eq 0 ]; then
        echo "Trial inserted successfully with trial_id $trial_id." >&2
    else
        echo "ERROR inserting trial for participant_session_id $participant_session_id." >&2
        exit 1
    fi

    # Check if trial_id is valid
    if [ -z "$trial_id" ]; then
        echo "ERROR: Failed to retrieve trial_id $trial_id" >&2
        exit 1
    fi

    # Insert into session_data_instance table for each CSV file
    for csv in {1..4}; do
        start_time="21:46:20"
        file_path="$path/${csv_counter}.csv"
        generate_data "$file_path" "$start_time"

        insert_session_data_instance="USE $DB_NAME;
        INSERT INTO session_data_instance (trial_id, measurement_option_id, results_path)
        VALUES ($trial_id, $csv, '$file_path');"
        
        session_data_instance_id=$(mysql -e "$insert_session_data_instance; SELECT LAST_INSERT_ID();" -s -N)
        # Check for successful session_data_instance insert
        if [ $? -eq 0 ]; then
            echo "Session data instance $session_data_instance_id for trial $trial_id inserted successfully." >&2
        else
            echo "ERROR: Inserting session data instance for trial $trial_id." >&2
            exit 1
        fi
        csv_counter=$((csv_counter + 1))
    done
    echo "$csv_counter"
}

generate_data() {
    local file_path=$1
    local start_time=$2
    local num_records=20
    
    for i in $(seq 1 $num_records); do
        local time=$(date -u -d "@$(( $(date -d "$start_time" +%s) + i ))" +"%H:%M:%S")
        local value1=$(echo "scale=2; $RANDOM/1000" | bc)
        local value2=$((RANDOM % 1000))
        local value3=$((RANDOM % 500))
        echo "$time,$value1,$value2,$value3" >> "$file_path"
    done
}

csv_counter=1
trial_counter=1
study_id=1
for participant_id in {1..3}; do
        path=$(create_data_path_participant 1 $participant_id)
        participant_session_id=$(update_database_participant_session "$participant_id")
    for trial_id in {1..4}; do
        path=$(create_data_path_trial $trial_counter $participant_id)  
        csv_counter=$(update_database_trial "$path" "$participant_id" "$study_id" "$csv_counter" "$participant_session_id")
        trial_counter=$((trial_counter + 1))
    done
done

end_time=$(date +%s)
elapsed_time=$((end_time - start_time))
echo "Time taken to reach Flask section: $elapsed_time seconds." >&2

FLASK_PORT=$(echo $VUE_APP_BACKEND_PORT | tr -d '\r')
FLASK_PID=$(lsof -t -i :$FLASK_PORT)
[ -n "$FLASK_PID" ] && kill -9 $FLASK_PID

echo "Starting Flask app on port $FLASK_PORT..." >&2
flask run --host=0.0.0.0 --port=$FLASK_PORT --debug
