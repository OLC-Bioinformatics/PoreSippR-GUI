#!/usr/env/python

"""
Methods for the PoreSippr-GUI
"""

# Standard imports
import os

# Third-party imports
import pandas as pd


def read_csv_file(file_path):
    """
    This function reads a CSV file and returns a pandas DataFrame.

    Parameters:
    file_path (str): The path to the CSV file.

    Returns:
    pd.DataFrame: The DataFrame containing the CSV data.
    """
    df = pd.read_csv(file_path)
    return df


def parse_dataframe(df):
    """
    This function parses a DataFrame and returns a dictionary where the keys
    are the column headers and the values are the values in the first row.

    Parameters:
    df (pd.DataFrame): The DataFrame to parse.

    Returns:
    dict: A dictionary where the keys are the column headers and the values
    are the values in the first row.

    Raises:
    ValueError: If the DataFrame is empty.
    """
    if df.empty:
        raise ValueError("The DataFrame is empty")

    # Get the first row of the DataFrame
    first_row = df.iloc[0]

    # Convert the first row to a dictionary
    data_dict = first_row.to_dict()

    return data_dict


def validate_headers(data_dict):
    """
    This function checks if all necessary headers are present in the dictionary

    Parameters:
    data_dict (dict): The dictionary to validate.

    Returns:
    str: A string containing all missing headers if any are missing,
    None otherwise.
    """
    necessary_headers = [
        "reference",
        "fast5_dir",
        "output_dir",
        "config",
        "barcode",
        "barcode_values"
    ]

    missing_headers = [
        header for header in necessary_headers if header not in data_dict
    ]

    if missing_headers:
        if len(missing_headers) == 1:
            return f"Missing necessary header: {', '.join(missing_headers)}"
        else:
            return f"Missing necessary headers: {', '.join(missing_headers)}"

    return None


def validate_file_exists(file_path, header):
    """
    This function checks if a file exists at the given path.

    Parameters:
    file_path (str): The path to the file.
    header (str): The header associated with the file path.

    Returns:
    str: An error message if the file does not exist, None otherwise.
    """
    if not os.path.isfile(file_path):
        return f"Could not locate {header} file: {file_path}"
    return None


def validate_or_create_directory(directory_path, header):
    """
    This function checks if a directory exists at the given path. If the
    directory does not exist, it attempts to create it.

    Parameters:
    directory_path (str): The path to the directory.
    header (str): The header associated with the directory path.

    Returns:
    str: An error message if the directory does not exist and cannot be
    created, None otherwise.
    """
    if not os.path.isdir(directory_path):
        try:
            os.makedirs(directory_path)
        except Exception as exc:
            return (
                f"Could not create {header} directory at {directory_path}. " 
                f"Error: {str(exc)}"
            )
    return None


def validate_data_dict(data_dict):
    """
    This function validates the values in the data_dict dictionary.

    Parameters:
    data_dict (dict): The dictionary to validate.

    Returns:
    str: A string containing all error messages if any values are not valid,
        None otherwise.
    """
    errors = []

    error = validate_file_exists(
        file_path=data_dict["reference"],
        header="reference"
    )
    if error:
        errors.append(error)

    error = validate_file_exists(
        file_path=data_dict["config"],
        header="config"
    )
    if error:
        errors.append(error)

    error = validate_or_create_directory(
        directory_path=data_dict["fast5_dir"],
        header="fast5_dir"
    )
    if error:
        errors.append(error)

    error = validate_or_create_directory(
        directory_path=data_dict["output_dir"],
        header="output_dir"
    )
    if error:
        errors.append(error)

    if errors:
        return "\n".join(errors)

    return None
