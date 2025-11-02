#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
