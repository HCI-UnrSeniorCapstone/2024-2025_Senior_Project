eval $(grep -E '^RESULTS_BASE_DIR_PATH=|^VUE_APP_BACKEND_PORT=|^MYSQL_DB=|^MYSQL_USER=|^MYSQL_PASSWORD=' ../.env | sed 's/\r//' | xargs -d '\n' -I {} echo export \"{}\")


DB_NAME=$(echo $MYSQL_DB | tr -d '\r')

FLASK_PORT=$(echo $VUE_APP_BACKEND_PORT | tr -d '\r')
FLASK_PID=$(lsof -t -i :$FLASK_PORT)
[ -n "$FLASK_PID" ] && kill -9 $FLASK_PID

echo "Starting Flask app on port $FLASK_PORT..." >&2
flask run --host=0.0.0.0 --port=$FLASK_PORT --debug

