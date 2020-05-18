#!/usr/bin/env bash

echo "Waiting for postgres..."

# Wait for the postgres server to spin up
python scripts/wait.py

echo "PostgreSQL started"

# Update and upgrade the database
if [[ $( flask db heads | wc -l ) != 1 ]]
then
  echo "configuring db . . ."
  flask db migrate -m "setup"
  flask db upgrade
else
  echo "db is up to date"
fi

# Check the integrity of the db User accounts
python manager.py user-health-check

# Run the web server
gunicorn wsgi:"create_app()" --worker-class eventlet --bind 0.0.0.0:8000
