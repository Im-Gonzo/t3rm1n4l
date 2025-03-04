#!/bin/bash
# Wrapper script for t3rm1n4l music player

# Find the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Run the Python app
python3 main.py "$@"
