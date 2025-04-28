#!/bin/bash
# Export environment variables from .env file
eval $(grep -E '^RESULTS_BASE_DIR_PATH=|^VUE_APP_BACKEND_PORT=|^MYSQL_DB=|^MYSQL_USER=|^MYSQL_PASSWORD=' ../.env | sed 's/\r//' | xargs -d '\n' -I {} echo export \"{}\")

DB_NAME=$(echo $MYSQL_DB | tr -d '\r')
FLASK_PORT=$(echo $VUE_APP_BACKEND_PORT | tr -d '\r')

# Kill any existing Flask instance
FLASK_PID=$(lsof -t -i :$FLASK_PORT)
[ -n "$FLASK_PID" ] && kill -9 $FLASK_PID

# Kill any existing worker processes
echo "Stopping any existing worker.py processes..." >&2
pkill -f "python ../worker.py" || true

# Start the worker.py in the background
echo "Starting worker.py in the background..." >&2
cd ..
python worker.py > worker.log 2>&1 &
WORKER_PID=$!
echo "Worker started with PID: $WORKER_PID" >&2
cd - > /dev/null

# Start the Flask app
echo "Starting Flask app on port $FLASK_PORT..." >&2
flask run --host=0.0.0.0 --port=$FLASK_PORT --debug

