#!/bin/bash
# Script synchronisation Bot -> Site

# Navigate to the repo directory (Sandbox path: /app)
cd /app

# Check if status.json exists
if [ -f status.json ]; then
    # Add status.json to staging
    git add status.json

    # Commit changes
    # Note: In a real environment with credentials, git push would follow.
    git commit -m "Auto-update trading metrics [V8.0]"

    # git push origin main
    echo "Metrics updated and committed."
else
    echo "status.json not found."
fi
