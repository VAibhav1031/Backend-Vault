#!/bin/bash

set -e

source ./.venv/bin/activate

until pg_isready --host=dev-db --port=5432 --dbname=${DEV_DB_NAME} --username=${DEV_DB_USER}; do
  echo "Waiting for the database to be ready.."
  sleep 2
done

echo "Database is ready!!"

echo "Running Flask database migration"
flask --app run.py db upgrade

echo "Startting the flask application...."
exec uv run python run.py
