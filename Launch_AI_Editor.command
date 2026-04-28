#!/bin/bash
# Move to the directory where this script is located
cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements quietly
echo "Installing dependencies..."
pip install -r requirements.txt -q

# Run the app window
echo "Starting AI Video Editor Assistant..."
python app_window.py
