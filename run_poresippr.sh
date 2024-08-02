#!/bin/bash

# Path to the conda environment
CONDA_ENV_PATH="$HOME/miniconda/envs/poresippr_gui"

# Log file path
LOG_FILE="$HOME/PycharmProjects/PoreSippR-GUI/run_poresippr.log"

# Initialize conda
{
    echo "Initializing conda..."
    source "$HOME/miniconda/etc/profile.d/conda.sh"

    # Activate the environment
    echo "Activating environment..."
    conda activate "$CONDA_ENV_PATH"

    # Run the application using the full path to the python executable
    echo "Running application..."
    python "$HOME/PycharmProjects/PoreSippR-GUI/main.py"

    # Deactivate the environment
    echo "Deactivating environment..."
    conda deactivate
} &> "$LOG_FILE"