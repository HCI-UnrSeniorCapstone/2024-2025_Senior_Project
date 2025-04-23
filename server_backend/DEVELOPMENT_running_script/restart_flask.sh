eval $(grep -E '^RESULTS_BASE_DIR_PATH=|^VITE_APP_BACKEND_PORT=|^MYSQL_DB=|^MYSQL_USER=|^MYSQL_PASSWORD=' ../.env | sed 's/\r//' | xargs -d '\n' -I {} echo export \"{}\")

# CLI argument
ENV_MODE=$1

DB_NAME=$(echo $MYSQL_DB | tr -d '\r')
FLASK_PORT=$(echo $VITE_APP_BACKEND_PORT | tr -d '\r')
# Kill anything using that port (only in dev mode)
if [ "$ENV_MODE" != "production" ]; then
  FLASK_PID=$(lsof -t -i :$FLASK_PORT)
  [ -n "$FLASK_PID" ] && kill -9 $FLASK_PID
fi

echo "Running in $ENV_MODE mode..."

if [ "$ENV_MODE" == "production" ]; then
  echo "PRODUCTION: Starting Gunicorn on port 8000..."
  gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app # uses wsgi.py
elif [ "$ENV_MODE" == "development" ]; then
  echo "DEVELOPMENT: Starting Flask app on port $FLASK_PORT..."
  python app.py development  # uses app.py
else
  echo "Unknown ENV_MODE: $ENV_MODE"
fi