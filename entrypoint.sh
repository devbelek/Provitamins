#!/bin/bash

# Collect static files
echo "Collect static files"
python3 manage.py collectstatic --noinput

# migrate
echo "migrate"
python3 manage.py makemigrations
python3 manage.py migrate


# Start server
echo "Starting server"

uvicorn vitamins.asgi:application --host 0.0.0.0 --port 8000 --reload

exec "$@"
