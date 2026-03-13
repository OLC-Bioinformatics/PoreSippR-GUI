#!/bin/bash

# Log file path
LOG_FILE="/home/olcbio/PoreSippR-GUI/run_poresippr.log"

# Run the application using the full path to the python executable
echo "Running application..."
/home/olcbio/mambaforge/bin/python "/home/olcbio/PoreSippR-GUI/main.py" &> "$LOG_FILE"

