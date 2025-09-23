#!/bin/bash

set -e

source ./.venv/bin/activate

until pg_isready --host=dev-db --port=5432 --dbname=${DEV_DB_NAME} --username=${DEV_DB_USER}; do
  echo "Waiting for the database to be ready.."
  sleep 2
done

echo "Database is ready!!"

if ! [ -d ./migrations/ ]; then
  echo "Path doesn't exist: migrations."
  echo "Creating...."
  flask --app run.py db init
  flask --app run.py db migrate -m "initial migration"
fi
echo "Done."

if [ -z "$(ls -A migrations/versions 2>/dev/null)" ]; then
  flask --app run.py db migrate -m "initial migration"
fi

echo "Running Flask database migration"
flask --app run.py db upgrade

echo "Startting the flask application...."
exec uv run python run.py
