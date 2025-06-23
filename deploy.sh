#!/bin/bash

set -e

# Navigate to the repository root (directory of this script)
cd "$(dirname "$0")"

# Update repository
if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "Pulling latest changes..."
    git pull --ff-only
else
    echo "Not inside a git repository." >&2
    exit 1
fi

# Activate virtual environment or create it if missing
if [ -f "venv/bin/activate" ]; then
    echo "Activating existing virtual environment..."
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    echo "Activating existing Windows virtual environment..."
    source venv/Scripts/activate
else
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt
    else
        pip install flask
    fi
fi

# Start the Flask application
exec python app.py
