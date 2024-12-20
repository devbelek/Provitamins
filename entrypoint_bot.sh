#!/bin/bash

# Start server
echo "Starting server"

uvicorn telegram_bot.main:app --host 0.0.0.0 --port 8001 --reload

exec "$@"
