#!/bin/sh

echo "Waiting for Postgres to start..."
while ! nc -z backend-db 5432; do
    sleep 0.1
done
echo "Postgres started."

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn --workers 3 --bind 0.0.0.0:8000 wsgi:app
