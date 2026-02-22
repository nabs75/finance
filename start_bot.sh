#!/bin/bash
echo "Starting Alpha-5 Production Bot..."
# Ensure dependencies are installed just in case
# pip install -r requirements.txt

while true; do
    echo "Launching bot.py at $(date)"
    python bot.py
    EXIT_CODE=$?
    echo "Bot exited with code $EXIT_CODE. Restarting in 5 seconds..."
    sleep 5
done
