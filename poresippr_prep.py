#!/usr/bin/env python3

"""
A script to prepare the PoreSippr GUI for use. This script creates a desktop
entry file and copies it to the applications directory. It also makes the
desktop entry file executable. The script takes the path to the conda
environment as an argument. If the conda environment path is not provided,
the default path is used.
"""

# Standard library imports
import argparse
import os
import shutil


def read_version(version_file):
    """
    Read the version from the version.py file.

    Args:
        version_file (str): Path to the version.py file.

    Returns:
        str: The version string.
    """
    version = {}
    with open(version_file) as f:
        exec(f.read(), version)
    return version['__version__']


def create_desktop_entry_content(version, script_dir):
    """
    Create the content for the desktop entry file.

    Args:
        version (str): The version string.
        script_dir (str): The directory of the script.

    Returns:
        str: The desktop entry content.
    """
    return f"""[Desktop Entry]
Version={version}
Name=PoreSippr
Comment=Run PoreSippr Application
Exec={os.path.join(script_dir, 'run_poresippr.sh')}
Icon={os.path.join(script_dir, 'cfia.jpg')}
Terminal=false
Type=Application
Categories=Utility;
"""


def write_desktop_entry(desktop_file, content):
    """
    Write the desktop entry content to a file.

    Args:
        desktop_file (str): Path to the desktop entry file.
        content (str): The desktop entry content.
    """
    with open(desktop_file, 'w') as file:
        file.write(content)


def copy_desktop_file(desktop_file, target_dir):
    """
    Copy the desktop file to the desired directory.

    Args:
        desktop_file (str): Path to the desktop entry file.
        target_dir (str): Path to the target directory.
    """
    os.makedirs(target_dir, exist_ok=True)
    shutil.copy(desktop_file, target_dir)


def make_executable(file_path):
    """
    Make a file executable.

    Args:
        file_path (str): Path to the file.
    """
    os.chmod(file_path, os.stat(file_path).st_mode | 0o111)


def create_run_script(script_dir, conda_env_path):
    """
    Create the run_poresippr.sh script.

    Args:
        script_dir (str): The directory of the script.
        conda_env_path (str): Path to the conda environment.
    """
    # Check if conda_env_path is "test"
    if conda_env_path == "test":
        conda_env_path = "$HOME/miniconda/envs/poresippr_gui"

    # Create the run_poresippr.sh script
    run_script_content = f"""#!/bin/bash

# Log file path
LOG_FILE="{os.path.join(script_dir, 'run_poresippr.log')}"
"""

    # Add conda environment activation if provided
    if conda_env_path:
        run_script_content += f"""
# Path to the conda environment
CONDA_ENV_PATH="{conda_env_path}"

# Initialize conda
{{
    echo "Initializing conda..."
    source "$HOME/miniconda/etc/profile.d/conda.sh"

    # Activate the environment
    echo "Activating environment..."
    conda activate "$CONDA_ENV_PATH"
}}
"""

    run_script_content += f"""
# Run the application using the full path to the python executable
echo "Running application..."
python "{os.path.join(script_dir, 'main.py')}"
"""

    if conda_env_path:
        run_script_content += """
# Deactivate the environment
echo "Deactivating environment..."
conda deactivate
"""

    run_script_content += f"""
}} &> "$LOG_FILE"
"""

    run_script_file = os.path.join(script_dir, 'run_poresippr.sh')
    with open(run_script_file, 'w') as file:
        file.write(run_script_content)
    make_executable(run_script_file)


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Prepare the PoreSippr GUI for use."
    )
    parser.add_argument(
        'conda_env_path',
        nargs='?',
        default=None,
        help="Path to the conda environment (default: None)"
    )
    return parser.parse_args()


def main(conda_env_path):
    """
    Main function to create and copy the desktop entry file.

    Args:
        conda_env_path (str): Path to the conda environment.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    version_file = os.path.join(script_dir, 'version.py')
    desktop_file = os.path.join(script_dir, 'PoreSippr.desktop')
    target_dir = os.path.expanduser('~/.local/share/applications')

    version = read_version(version_file)
    content = create_desktop_entry_content(version, script_dir)
    write_desktop_entry(desktop_file, content)
    copy_desktop_file(desktop_file, target_dir)

    print(f"Desktop entry created and copied to {target_dir}")

    create_run_script(script_dir, conda_env_path)

    print(f"Run script created at {script_dir}/run_poresippr.sh")


if __name__ == "__main__":
    args = parse_arguments()
    main(conda_env_path=args.conda_env_path)
