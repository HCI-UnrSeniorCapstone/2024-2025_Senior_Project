#!/bin/bash

# Load environment variables from .env
eval $(grep -E '^RESULTS_BASE_DIR_PATH=|^VITE_APP_DEVELOPMENT_BACKEND_PORT=|^VITE_APP_PRODUCTION_BACKEND_PORT=|^MYSQL_DB=|^MYSQL_USER=|^MYSQL_PASSWORD=' ../.env | sed 's/\r//' | xargs -d '\n' -I {} echo export \"{}\")

# CLI argument: development or production
ENV_MODE=$1

# Sanitize environment variables (remove any carriage returns if Windows editing)
DB_NAME=$(echo "$MYSQL_DB" | tr -d '\r')
FLASK_PORT=$(echo "$VITE_APP_DEVELOPMENT_BACKEND_PORT" | tr -d '\r')
GUNICORN_PORT=$(echo "$VITE_APP_PRODUCTION_BACKEND_PORT" | tr -d '\r')

echo "Running in $ENV_MODE mode..."

if [ "$ENV_MODE" == "production" ]; then
  # Kill existing Gunicorn process if any
  GUNICORN_PID=$(lsof -t -i :$GUNICORN_PORT)
  if [ -n "$GUNICORN_PID" ]; then
    echo "Killing existing Gunicorn process on port $GUNICORN_PORT..."
    kill -9 $GUNICORN_PID
  fi

  echo "PRODUCTION: Starting Gunicorn on port $GUNICORN_PORT..."
  gunicorn -w 4 -b 0.0.0.0:$GUNICORN_PORT wsgi:app

elif [ "$ENV_MODE" == "development" ]; then
  # Kill existing Flask dev process if any
  FLASK_PID=$(lsof -t -i :$FLASK_PORT)
  if [ -n "$FLASK_PID" ]; then
    echo "Killing existing Flask process on port $FLASK_PORT..."
    kill -9 $FLASK_PID
  fi

  echo "DEVELOPMENT: Starting Flask app on port $FLASK_PORT..."
  export FLASK_ENV=development
  flask run --host=0.0.0.0 --port=$FLASK_PORT --debug

else
  echo "Unknown ENV_MODE: $ENV_MODE"
  echo "Please specify either 'development' or 'production'."
  exit 1
fi
