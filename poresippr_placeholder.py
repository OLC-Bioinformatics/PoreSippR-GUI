#!/usr/env/python 3
"""
A placeholder script for the PoreSippr. This script clears out any images in
the current working directory, and periodically copies a mock-up image into the
current working directory. This gives comparable functionality to what I
imagine the final PoreSippr will have
"""

# Standard imports
import argparse
from collections import defaultdict
import csv
from glob import glob
import multiprocessing
import os
import re
import shutil
import signal
import time


def process_config_file(config_file):
    """
    Process a CSV config file. This function reads the CSV file and extracts
    the output_dir value. It then determines the parent folder of output_dir.

    :param config_file: The path to the CSV config file
    """
    # Open the CSV file
    with open(config_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            output_dir = row['output_dir']

    # Determine the parent folder of output_dir
    parent_folder = os.path.dirname(output_dir)

    # Delete any CSV files in the output_dir
    csv_files = glob(os.path.join(output_dir, '*.csv'))
    for csv_file in csv_files:
        os.remove(csv_file)

    print(f"The output_dir is: {output_dir}")

    # Make the output_dir if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"The parent folder of output_dir is: {parent_folder}")

    return output_dir, parent_folder


def copy_csv_files(output_dir, parent_folder, sleep_time=20):
    """
    Copy CSV files from the csv_holding folder to the output_dir. This function
    groups the CSV files by iteration and sorts the iterations before copying
    the CSV files. Includes a countdown during sleep for better UX.
    :param output_dir: The output directory where the CSV files will be copied
    :param parent_folder: The parent folder of the output_dir
    :param sleep_time: The time to sleep between iterations. Default is 20
    """
    # Construct the csv_path
    csv_path = os.path.join(parent_folder, 'csv_holding')

    # Get all CSV files in the csv_path
    all_csv_files = glob(os.path.join(csv_path, '*.csv'))

    # Group the CSV files by iteration
    csv_files_by_iteration = defaultdict(list)
    for csv_file in all_csv_files:
        iteration_match = re.search(r'iteration(\d+)', csv_file)
        if iteration_match:
            iteration = int(iteration_match.group(1))
            csv_files_by_iteration[iteration].append(csv_file)

    # Sort the iterations
    sorted_iterations = sorted(csv_files_by_iteration.keys())

    for iteration in sorted_iterations:
        print(f"Iteration: {iteration}.")
        print(f"CSV files grouped by iteration: "
              f"{sorted(csv_files_by_iteration[iteration])}")
        # Copy the CSV files for the current iteration to output_dir
        for csv_file in sorted(csv_files_by_iteration[iteration]):
            try:
                shutil.copy(csv_file, output_dir)
            except shutil.Error:
                pass

        # Implement countdown for sleep_time
        for remaining in range(sleep_time, 0, -1):
            print(f"Sleeping for {remaining} seconds...", end="\r")
            time.sleep(1)

        # Clear line after countdown
        print("Sleep complete. Continuing...       ")


# Create a shared value for the complete flag
complete = multiprocessing.Value('b', False)


def signal_handler(_, __):
    """
    Handles termination signals sent to the process.

    This function is designed to be used as a signal handler for the
    SIGINT (Ctrl+C) and SIGTERM signals. When either of these signals
    is received, it sets the complete flag to True.
    """
    print('Signal received, stopping...')
    complete.value = True
    raise SystemExit


if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Process a CSV config file.')
    parser.add_argument(
        'config_file',
        type=str,
        help='Path to the CSV config file'
    )
    parser.add_argument(
        '--sleep_time',
        type=int,
        default=20,
        help='Time to sleep between iterations in seconds'
    )

    args = parser.parse_args()

    print(f"Running PoreSipprPlaceholder with config file: {args.config_file}")

    out_dir, parent_dir = process_config_file(args.config_file)

    # Create a subprocess for the copy_csv_files function, including
    # sleep_time in the arguments
    p = multiprocessing.Process(
        target=copy_csv_files,
        args=(out_dir, parent_dir, args.sleep_time)
    )

    # Register the signal handler for SIGINT (Ctrl+C) and SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start the subprocess
    p.start()

    # Wait for the subprocess to finish
    while not complete.value:
        try:
            p.join(timeout=1)
        except SystemExit:
            print('Terminating subprocess...')
            p.terminate()
            p.join()
        if complete.value:
            break
