#!/usr/env/python

"""
Methods for the PoreSippr-GUI
"""

# Standard imports
import argparse
import base64
from collections import defaultdict
import csv
from datetime import datetime
import glob
import multiprocessing
import os
import re
import shutil
import subprocess
import sys
import threading
from time import sleep

# Third-party imports
from Bio import SeqIO
from bs4 import BeautifulSoup
from jinja2 import (
    Environment,
    FileSystemLoader
)
import pandas as pd

# Local imports
from version import __version__


def determine_script_path():
    """
    Determine the base path of the current Python file or executable.
    """
    # Attempt to determine the script path using __file__
    script_path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_path, 'cfia.jpg')

    if not os.path.exists(image_path):
        # If the image file does not exist, attempt to determine the script
        # path using sys.executable
        script_path = os.path.dirname(sys.executable)
        image_path = os.path.join(script_path, 'cfia.jpg')

        if not os.path.exists(image_path):
            raise SystemExit('Cannot determine path')

    return script_path


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


def is_valid_fasta(file_path):
    """
    This function checks if a file is a valid FASTA file.
    :param file_path:
    :return:
    """
    try:
        # Attempt to parse the file as FASTA
        records = list(SeqIO.parse(file_path, "fasta"))
        # Check if there is at least one record
        if len(records) > 0:
            return True
        else:
            return False
    except Exception as e:
        # If parsing fails, the file is not a valid FASTA file
        print(f"Error parsing file: {e}")
        return False


def get_sorted_barcode_values(data_dict):
    """
    Extracts and sorts the barcode values from the provided data dictionary,
    maintaining their original string format with leading zeros.

    Parameters:
    data_dict (dict): The dictionary containing the key 'barcode_values' with
        a string of comma-separated values or a single value.

    Returns:
    list: A sorted list of barcode values, maintaining their original string
        format with leading zeros.
    """
    # Extract the barcode values string from the data dictionary and ensure
    # it's a string
    barcode_values_str = str(data_dict.get('barcode_values', ''))

    # Return an empty list if barcode_values_str is empty
    if not barcode_values_str:
        return []

    # Split the string into a list based on commas
    barcode_values_list = barcode_values_str.split(',')

    # Sort the list of strings based on their integer value
    sorted_barcode_values = sorted(barcode_values_list, key=lambda x: int(x))

    # Format each element to ensure leading zeros are preserved
    formatted_barcode_values = [x.zfill(2) for x in sorted_barcode_values]

    return formatted_barcode_values


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


def get_csv_files_by_iteration(folder_path):
    """
    Get all CSV files in the specified folder and group them by iteration.

    Parameters:
    folder_path (str): The path to the folder.

    Returns:
    dict: A dictionary where the keys are iteration numbers and the values are
        lists of CSV file paths.
    """
    # Get all CSV files in the folder
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

    # Initialize a dictionary to store the CSV files grouped by iteration
    csv_files_by_iteration = defaultdict(list)

    # Regular expression to extract the iteration number from the file name
    regex = re.compile(r'iteration(\d+)\.csv$')

    # Group the CSV files by iteration
    for csv_file in csv_files:
        match = regex.search(csv_file)
        if match:
            iteration = int(match.group(1))
            csv_files_by_iteration[iteration].append(csv_file)

    return csv_files_by_iteration


def parse_csv_file(csv_file):
    """
    Parse a CSV file into a pandas DataFrame.

    Parameters:
    csv_file (str): The path to the CSV file.

    Returns:
    pd.DataFrame: The DataFrame containing the CSV data.
    """
    df = pd.read_csv(csv_file)
    return df


def create_data_dict(df, csv_file, metadata_dict):
    """
    Create a dictionary of data from a DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to parse.
    csv_file (str): The path to the CSV file.
    metadata_dict (dict): A dictionary containing links for seqid:olnid:barcode

    Returns:
    dict: A dictionary where the keys are the column headers and the values
    are the values in the first row.
    """
    # Remove 'X' from 'number_of_reads_mapped' values and convert to numeric
    df['number_of_reads_mapped'] = pd.to_numeric(
        df['number_of_reads_mapped'].str.replace('X', ''),
        errors='coerce'
    )
    
    # Serotype
    o_type = df[df['gene_name'].str.contains('O/')]

    # Extract the O-type from the 'gene_name' column
    df['O_type'] = df['gene_name'].str.extract(r'O/.*?(\d+)')

    # Group the DataFrame by 'O_type' and sum 'number_of_reads_mapped'
    grouped_o_type = df.groupby('O_type')[
        'number_of_reads_mapped'].sum().reset_index()

    # Filter the groups based on the sum of 'number_of_reads_mapped'
    o_type_with_reads = grouped_o_type[
        grouped_o_type['number_of_reads_mapped'] > 1]

    #
    h_type = df[df['gene_name'].str.contains('H/')]

    # Extract the H-type from the 'gene_name' column
    df['H_type'] = df['gene_name'].str.extract(r'H/.*?(\d+)')

    # Group the DataFrame by 'H_type' and sum 'number_of_reads_mapped'
    grouped_h_type = df.groupby('H_type')[
        'number_of_reads_mapped'].sum().reset_index()

    # Filter the groups based on the sum of 'number_of_reads_mapped'
    h_type_with_reads = grouped_h_type[
        grouped_h_type['number_of_reads_mapped'] > 1]

    # stx genes
    stx1_genes = df[df['gene_name'].str.contains('Stx1', case=False)]
    stx2_genes = df[df['gene_name'].str.contains('Stx2', case=False)]

    # Group the DataFrame by 'gene_name' and sum 'number_of_reads_mapped'
    grouped_stx1 = stx1_genes.groupby('gene_name')[
        'number_of_reads_mapped'].sum().reset_index()
    grouped_stx2 = stx2_genes.groupby('gene_name')[
        'number_of_reads_mapped'].sum().reset_index()

    # Filter the groups based on the sum of 'number_of_reads_mapped'
    stx1_with_reads = grouped_stx1[grouped_stx1['number_of_reads_mapped'] > 1]
    stx2_with_reads = grouped_stx2[grouped_stx2['number_of_reads_mapped'] > 1]

    # Virulence genes
    eae = df[df['gene_name'].str.contains('eae')]
    ehxa = df[df['gene_name'].str.contains('ehxA')]
    aggr = df[df['gene_name'].str.contains('aggR')]
    aaic = df[df['gene_name'].str.contains('aaiC')]
    uida = df[df['gene_name'].str.contains('uidA')]

    # Filter eae genes to only include those with at least two reads
    eae_with_reads = eae[eae['number_of_reads_mapped'] > 1]

    # Filter ehxA genes to only include those with at least two reads
    ehxa_with_reads = ehxa[ehxa['number_of_reads_mapped'] > 1]

    # Filter aggR genes to only include those with at least two reads
    aggr_with_reads = aggr[aggr['number_of_reads_mapped'] > 1]

    # Filter aaiC genes to only include those with at least two reads
    aaic_with_reads = aaic[aaic['number_of_reads_mapped'] > 1]

    # Filter uidA genes to only include those with at least two reads
    uida_with_reads = uida[uida['number_of_reads_mapped'] > 1]

    # GDCS genes
    gdcs_genes = df[~df['gene_name'].str.contains(
        'O/|H/|Stx|eae|ehxA|aggR|aaiC|#', case=False
    )]

    # Filter GDCS genes to only include those with at least two reads
    gdcs_genes_with_reads = \
        gdcs_genes[gdcs_genes['number_of_reads_mapped'] > 1]

    # Extract the barcode name from the CSV file name
    barcode_name = os.path.basename(csv_file).split('_')[0]

    # Find the genome coverage
    coverage = df[df['gene_name'].str.contains('genome_coverage')]
    
    # Extract the coverage value
    coverage_value = coverage['number_of_reads_mapped'].values[
        0] if not coverage.empty else 0

    # Convert the coverage value to a float and round to two decimal places
    coverage_value = round(float(coverage_value), 2)

    # Create a dictionary with the extracted information
    data_dict = {
        'SEQID': barcode_name,
        'OLN ID': metadata_dict[barcode_name]['OLNID'],
        'O-Type':
            f"{o_type['gene_name'].values[0].split('/')[1].split('-')[0]} "
            f"({int(o_type_with_reads['number_of_reads_mapped'].sum())})"
            if not o_type.empty and o_type_with_reads[
                'number_of_reads_mapped'].sum() > 0 else '-',
        'H-Type':
            f"{h_type['gene_name'].values[0].split('/')[1].split('-')[0]} "
            f"({int(h_type_with_reads['number_of_reads_mapped'].sum())})"
            if not h_type.empty and h_type_with_reads[
                'number_of_reads_mapped'].sum() > 0 else '-',
        'stx1': int(
            stx1_with_reads['number_of_reads_mapped'].sum()
            ) if not stx1_genes.empty and stx1_with_reads[
            'number_of_reads_mapped'].sum() > 0 else '-',
        'stx2': int(
            stx2_with_reads['number_of_reads_mapped'].sum()
            ) if not stx2_genes.empty and stx2_with_reads[
            'number_of_reads_mapped'].sum() > 0 else '-',
        'eae': int(
            eae_with_reads['number_of_reads_mapped'].sum()
            ) if not eae.empty and eae_with_reads[
            'number_of_reads_mapped'].sum() > 0 else '-',
        'hylA': int(
            ehxa_with_reads['number_of_reads_mapped'].sum()
            ) if not ehxa.empty and ehxa_with_reads[
            'number_of_reads_mapped'].sum() > 0 else '-',
        'aggR': int(
            aggr_with_reads['number_of_reads_mapped'].sum()
            ) if not aggr.empty and aggr_with_reads[
            'number_of_reads_mapped'].sum() > 0 else '-',
        'aaiC': int(
            aaic_with_reads['number_of_reads_mapped'].sum()
            ) if not aaic.empty and aaic_with_reads[
            'number_of_reads_mapped'].sum() > 0 else '-',
        'uidA': int(
            uida_with_reads['number_of_reads_mapped'].sum()
            ) if not uida.empty and uida_with_reads[
            'number_of_reads_mapped'].sum() > 0 else '-',
        'GDCS': f"{len(gdcs_genes_with_reads)}/325",
        'Coverage': coverage_value  # Use the modified coverage value
    }

    return data_dict


def visualize_data(all_data_df, output_path):
    """
    Visualize the data in a DataFrame as a table and save it to a file.

    Parameters:
    all_data_df (pd.DataFrame): The DataFrame to visualize.
    output_path (str): The path to the output file.
    """
    def color_cells(val):
        """
        Apply color formatting to the cells in the DataFrame.
        :param val: The cell value.
        :return: The CSS style string.
        """
        if pd.isnull(val) or val == '-':
            background_color = 'white'
            font_color = 'black'
        elif isinstance(val, str) and '/' in val and \
                int(val.split('/')[0]) < 320:
            # Grey color for "misses"
            background_color = '#D3D3D3'
            font_color = 'black'
        elif isinstance(val, str) and val.replace(
                '.', '', 1).isdigit() and float(val) < 7.5:
            background_color = '#D3D3D3'
            font_color = 'black'
        else:
            background_color = 'blue'
            font_color = 'white'
        return f'background-color: {background_color}; color: {font_color}'

    # Round the 'Coverage' column to two decimal places and convert to string
    all_data_df['Coverage'] = all_data_df['Coverage'].round(2).astype(str)

    # Apply the color formatting to the DataFrame
    styled_df = all_data_df.style.map(color_cells)

    # Apply a different style to the 'Barcode' column
    styled_df = styled_df.apply(
        lambda x: [
            'background-color: white; color: black'
            if x.name == 'Strain Name' else '' for _ in x
        ], axis=0
    )

    # Define CSS
    css = """
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
            font-family: Arial, sans-serif;
            font-size: 30px;  /* Add this line to set the font size */
        }
        th {
            background-color: #D3D3D3;
            color: white;
            text-align: left;
            padding: 8px;
        }
        td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;  /* Center the text in the cells */
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
    </style>
    """
    # Save the styled DataFrame to an HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(css)
        f.write(styled_df.to_html())


def remove_index_from_html(html_file_path):
    """
    Remove the index column from an HTML file.
    :param html_file_path: The path to the HTML file.
    """
    # Read the HTML file
    with open(html_file_path, 'r') as f:
        html = f.read()

    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Find the table
    table = soup.find('table')

    # Remove the first th element in the thead
    table.thead.tr.th.decompose()

    # Remove all th elements in the tbody
    for th in table.tbody.find_all('th'):
        th.decompose()

    # Write the modified HTML back to the file
    with open(html_file_path, 'w') as f:
        f.write(str(soup))


def image_to_base64(image_path):
    """
    Convert an image to a base64 string.
    :param image_path: Path to the image file.
    :return: base64 string. of the image
    """
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def create_pdf_report(html_file_path, lab_name, num_strains, report_folder,
                      run_name, version):
    """
    Create a PDF report from provided information and HTML table.

    Parameters:
    html_file_path (str): The path to the HTML file.
    lab_name (str): The name of the laboratory.
    num_strains (int): The number of strains processed.
    report_folder (str): The path to the report folder.
    run_name (str): The name of the run.
    version (str): The version of the software.
    """

    # Create the report folder if it doesn't exist
    os.makedirs(report_folder, exist_ok=True)

    # Define the lookup dictionary
    lab_info = {
        'GTA': ('2301 Midland Ave., Scarborough, ON, M1P 4R7', ''),
        'BUR': ('3155 Willington Green, Burnaby, BC, V5G 4P2', ''),
        'OLC': ('960 Carling Ave, Building 22 CEF, Ottawa, ON, K1A 0Y9', ''),
        'FFFM': ('960 Carling Ave, Building 22 CEF, Ottawa, ON, K1A 0Y9', ''),
        'DAR': ('1992 Agency Dr., Dartmouth, NS, B2Y 3Z7', ''),
        'CAL': ('3650 36 Street NW, Calgary, AB, T2L 2L1', ''),
        'STH': ('3400 Casavant Boulevard W., St. Hyacinthe, QC, J2S 8E3', '')
    }

    # Extract the laboratory information from the dictionary
    lab_details = lab_info.get(lab_name, ('', ''))[0]

    # Load the HTML table from the file
    with open(html_file_path, 'r') as file:
        table_html = file.read()

    # Get the script path
    script_path = determine_script_path()

    # Load the HTML template
    env = Environment(loader=FileSystemLoader(script_path))
    template = env.get_template('report_template.html')

    # Convert image to Base64
    image_base64 = image_to_base64(os.path.join(script_path, 'CFIA_logo.png'))

    # Render the HTML content with dynamic data
    html_content = template.render(
        lab_name=lab_name,
        lab_address=lab_details,
        number=num_strains,
        version=version,
        table_html=table_html,
        date=datetime.today().strftime('%Y-%m-%d'),
        image_base64=image_base64  # Use Base64 string
    )

    # Save the rendered HTML to a temporary file
    temp_html_path = os.path.join(report_folder, f'{run_name}_temp.html')
    with open(temp_html_path, 'w') as temp_html_file:
        temp_html_file.write(html_content)

    # Convert HTML to PDF using a system call to weasyprint
    output_pdf_path = os.path.join(report_folder, f'{run_name}_report.pdf')
    try:
        subprocess.run(
            ['weasyprint', temp_html_path, output_pdf_path], check=True
        )
    except subprocess.CalledProcessError as exc:
        print(f"Error creating PDF: {exc}")
    finally:
        # Clean up the temporary HTML file
        os.remove(temp_html_path)


def handle_output(stream, capture_list):
    """
    Reads from a subprocess stream, line by line and prints to console.
    """
    for line in iter(stream.readline, ''):
        # Remove trailing newline
        line = line.rstrip()
        print(line)
        capture_list.append(line)


def main(
            folder_path,
            output_folder,
            csv_path,
            complete,
            config_file=None,
            metadata_file=None,
            test=False,
            sleep_time=20,
            lab_name='OLC',
            run_name='None',
            pid_store=None):
    """
    Main function to process all CSV files in a folder grouped by iteration.

    Parameters:
    folder_path (str): The path to the folder.
    output_folder (str): The path to the output folder.
    csv_path (str): The path to the PoreSIPPR outputs.
    complete (multiprocessing.Value): A flag to indicate if the process should
        be stopped.
    config_file (str): The path to the configuration file. Default is None.
    test (bool): A flag to indicate if the function is being run in test mode.
    sleep_time (int): The time to sleep between iterations. Default is 20.
    """
    # Read the config file and extract the barcode_values
    with open(config_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            barcode_values = row['barcode_values'].split(',')

    # Create a dictionary to store the links for seqid:olnid:barcode
    link_dict = {}

    # Read the metadata file, and extract the links for seqid:olnid:barcode
    with open(metadata_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Populate link_dict with seqid as the key and a nested dictionary
            # {olnid: barcode} as the value
            link_dict[row['SEQID']] = {
                "OLNID": row['OLNID'],
                "Barcode": row['Barcode']
            }

    # Delete the output_folder if it exists and recreate it
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    # Delete the processed_folder if it exists and recreate it
    processed_folder = os.path.join(folder_path, 'processed')
    if os.path.exists(processed_folder):
        shutil.rmtree(processed_folder)
    os.makedirs(processed_folder, exist_ok=True)

    # Determine the path of the script
    script_path = os.path.dirname(os.path.abspath(__file__))

    # Run PoreSippr using subprocess.Popen. Capture stdout and stderr
    if test:
        command = [
            'python',
            '-u',
            os.path.join(script_path, 'poresippr_placeholder.py'),
            config_file,
            '--sleep_time',
            str(sleep_time)
        ]
    else:
        command = [
            'python',
            '-u',
            os.path.join(script_path, 'poresippr_basecall_scheduler.py'),
            config_file,
            metadata_file
        ]

    worker_process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    # Lists to capture stdout and stderr
    stdout_capture = []
    stderr_capture = []

    # Create and start threads for handling stdout and stderr
    stdout_thread = threading.Thread(
        target=handle_output, args=(worker_process.stdout, stdout_capture)
    )
    stderr_thread = threading.Thread(
        target=handle_output, args=(worker_process.stderr, stderr_capture)
    )
    stdout_thread.start()
    stderr_thread.start()

    # Store the PID in pid_store if it's provided
    if pid_store is not None:
        pid_store.append(worker_process.pid)

    while True:

        # Sleep for 1 second to allow the worker process to run
        sleep(1)

        # Check if the process should be stopped
        if complete.value:
            worker_process.terminate()
            break

        # Check if the worker process is still running
        if worker_process.poll() is not None:
            break

        # Get all CSV files in the csv_path
        all_csv_files = glob.glob(os.path.join(csv_path, '*.csv'))

        # Group the CSV files by iteration
        csv_files_by_iteration = defaultdict(list)
        for csv_file in all_csv_files:
            iteration_match = re.search(r'iteration(\d+)', csv_file)
            if iteration_match:
                iteration = int(iteration_match.group(1))
                csv_files_by_iteration[iteration].append(csv_file)

        # Sort the iterations
        sorted_iterations = sorted(csv_files_by_iteration.keys())

        # Initialize the current iteration and the all_data list
        current_iteration = None
        all_data = []

        for iteration in sorted_iterations:
            # Check if the process should be stopped
            if complete.value:
                worker_process.terminate()
                break

            # Check if all barcodes are present in the CSV files for
            # the iteration
            csv_files_for_iteration = csv_files_by_iteration[iteration]
            barcodes_for_iteration = [
                re.search(r'iteration(\d+)', csv_file).group(1)
                for csv_file in csv_files_for_iteration
            ]

            # Skip the iteration if not all barcodes are present
            if len(barcodes_for_iteration) < len(barcode_values):
                continue

            # If the iteration has changed, clear all_data
            if iteration != current_iteration:
                all_data = []

            # Create the output path
            output_path = os.path.join(
                output_folder, f'iteration_{iteration}.html'
            )

            # Extract the parent directory of folder_path
            parent_folder = os.path.dirname(folder_path)

            # Define the report folder inside the parent directory
            report_folder = os.path.join(parent_folder, 'reports')

            # Create the report folder if it doesn't exist
            os.makedirs(report_folder, exist_ok=True)

            for csv_file in sorted(csv_files_for_iteration):
                # Check if the CSV file has already been processed
                if os.path.exists(
                        os.path.join(
                            processed_folder,
                            os.path.basename(csv_file))):
                    continue
                
                # Process the CSV file
                df = parse_csv_file(csv_file)
                data_dict = create_data_dict(
                    df=df,
                    csv_file=csv_file,
                    metadata_dict=link_dict
                )
                all_data.append(data_dict)

                # Create the HTML table
                visualize_data(
                    all_data_df=pd.DataFrame(all_data),
                    output_path=output_path
                )

                # Remove the index column from the HTML file
                remove_index_from_html(
                    html_file_path=output_path
                )

                # Move the processed CSV file to a different folder
                shutil.move(csv_file, processed_folder)

            # Create the PDF report
            create_pdf_report(
                html_file_path=output_path,
                lab_name=lab_name,
                num_strains=len(barcode_values),
                report_folder=report_folder,
                run_name=run_name,
                version=__version__
            )

            # Update the current iteration
            current_iteration = iteration

            # Check if the worker process has completed
            if worker_process.poll() is not None:
                # Ensure all output is captured and printed by joining
                # the threads
                stdout_thread.join()
                stderr_thread.join()

                # Check if the subprocess exited with an error
                if worker_process.returncode != 0:
                    error_message = '\n'.join(
                        stderr_capture
                    ) if stderr_capture else 'An unknown error occurred'
                    # Raise an exception with the error message
                    raise RuntimeError(
                        f"Subprocess failed with error: {error_message}")
                break


if __name__ == "__main__":
    # Create a shared value for the complete flag
    process_complete = multiprocessing.Value('b', False)

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Construct the paths to the folders in the "test_files" directory
    test_files_dir = os.path.join(script_dir, 'test_files')

    # Create the parser and add arguments
    parser = argparse.ArgumentParser(description='Run PoreSippr tests.')
    parser.add_argument(
       'mode', type=str, nargs='?',
       choices=['prod', 'test'], default='prod',
       help='an optional argument to set the mode (default: prod)')

    # Parse the command line arguments
    args = parser.parse_args()

    # Check if a specific command line argument is provided
    if args.mode == 'test':
        # local_csv_path = os.path.join(test_files_dir, 'poresippr_out')
        local_csv_path = \
            '/home/adamkoziol/PycharmProjects/PoreSippR-GUI/config/' \
            'MIN-20240515'
        # local_folder_path = os.path.join(test_files_dir, 'output')
        local_folder_path = \
            '/home/adamkoziol/PycharmProjects/PoreSippR-GUI/config/output'
        # local_output_folder = os.path.join(test_files_dir, 'images')
        local_output_folder = \
            '/home/adamkoziol/PycharmProjects/PoreSippR-GUI/config/images'
        # local_config_file = os.path.join(test_files_dir, 'input.csv')
        local_config_file = \
            '/home/adamkoziol/PycharmProjects/PoreSippR-GUI/config/input.csv'
        local_metadata_file = \
            '/home/adamkoziol/PycharmProjects/PoreSippR-GUI/config/' \
            'metadata.csv'
        local_test = True

        local_run_name = 'MIN-20240515'
        local_lab_name = 'STH'
    else:
        local_csv_path = '/home/olcbio/Downloads/240125_MC26299/test_out'
        local_folder_path = '/home/olcbio/Downloads/240125_MC26299/output'
        local_output_folder = '/home/olcbio/Downloads/240125_MC26299/images'
        local_config_file = '/home/olcbio/PoreSippR-GUI/input.csv'
        local_metadata_file = '/home/olcbio/PoreSippR-GUI/metadata.csv'
        local_test = False
        local_run_name = '240125_MC26299'
        local_lab_name = 'OLC'

    main(
        csv_path=local_csv_path,
        folder_path=local_folder_path,
        output_folder=local_output_folder,
        complete=process_complete,
        config_file=local_config_file,
        metadata_file=local_metadata_file,
        test=local_test,
        sleep_time=20,
        run_name=local_run_name,
        lab_name=local_lab_name
      )
