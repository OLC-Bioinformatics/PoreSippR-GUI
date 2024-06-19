#!/usr/env/python

"""
Methods for the PoreSippr-GUI
"""

# Standard imports
from collections import defaultdict
import glob
import os
import re

# Third-party imports
from bs4 import BeautifulSoup
import fitz
import pandas as pd
from weasyprint import HTML


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


def create_data_dict(df, csv_file):
    """
    Create a dictionary of data from a DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to parse.
    csv_file (str): The path to the CSV file.

    Returns:
    dict: A dictionary where the keys are the column headers and the values
    are the values in the first row.
    """
    # Convert 'number_of_reads_mapped' to numeric
    df['number_of_reads_mapped'] = pd.to_numeric(
        df['number_of_reads_mapped'],
        errors='coerce'
    )

    # Extract the necessary information
    o_type = df[df['gene_name'].str.contains('O/')]
    h_type = df[df['gene_name'].str.contains('H/')]
    eae = df[df['gene_name'].str.contains('eae')]
    hlya = df[df['gene_name'].str.contains('hlyA')]
    aggr = df[df['gene_name'].str.contains('aggR')]
    aaic = df[df['gene_name'].str.contains('aaiC')]
    gdcs_genes = df[~df['gene_name'].str.contains(
        'O/|H/|Stx|eae|hlyA|aggR|aaiC'
    )]
    gdcs_genes_with_reads = \
        gdcs_genes[gdcs_genes['number_of_reads_mapped'] > 0]
    coverage = df[df['gene_name'] == 'mock_coverage']

    # Extract the barcode name from the CSV file name
    barcode_name = os.path.basename(csv_file).split('_')[0]

    # Create a sorted list of all formatted stx genes returned
    stx_genes = df[df['gene_name'].str.contains('Stx')].copy()
    stx_genes['formatted_gene_name'] = \
        stx_genes['gene_name'].apply(lambda x: x.split('_')[0])

    # Calculate the threshold for the number of mapped reads
    other_genes = df[~df['gene_name'].str.contains('Stx')]
    threshold = other_genes['number_of_reads_mapped'].median()

    # Adjust the threshold to be 20% of the original threshold
    threshold *= 0.2

    # Filter the stx genes based on the threshold
    stx_genes = stx_genes[stx_genes['number_of_reads_mapped'] >= threshold]

    stx_genes_sorted = stx_genes.sort_values(
        by='number_of_reads_mapped',
        ascending=False
    )

    # Convert the list to a set and then back to a list to remove duplicates
    stx_genes_list = list(
        set(
            stx_genes_sorted['formatted_gene_name'].tolist()
        )
    )

    # Join the stx_genes_list into a sorted, comma-separated string
    stx_genes_str = ', '.join(
        sorted(stx_genes_list)) if stx_genes_list else '-'

    # Extract the coverage value
    coverage_value = coverage['number_of_reads_mapped'].values[
        0] if not coverage.empty else '-'

    # Check if the coverage value ends with 'X'
    if isinstance(coverage_value, str) and coverage_value.endswith('X'):
        # Remove the 'X' and convert the remaining part to a float
        coverage_value = float(coverage_value.rstrip('X'))
    elif isinstance(coverage_value, (int, float)):
        # Convert the coverage value to a float
        coverage_value = float(coverage_value)

    # Create a dictionary with the extracted information
    data_dict = {
        'Barcode': barcode_name,
        'O-Type': o_type['gene_name'].values[0].split('/')[1].split('-')[
            0] if not o_type.empty else '-',
        'H-Type': h_type['gene_name'].values[0].split('/')[1].split('-')[
            0] if not h_type.empty else '-',
        'stx genes': stx_genes_str,  # Use the sorted, comma-separated string
        'eae': eae['gene_name'].values[0] if not eae.empty else '-',
        'hlyA': hlya['gene_name'].values[0] if not hlya.empty else '-',
        'aggR': aggr['gene_name'].values[0] if not aggr.empty else '-',
        'aaiC': aaic['gene_name'].values[0] if not aaic.empty else '-',
        'GDCS': f"{len(gdcs_genes_with_reads)}/330",
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
        elif isinstance(val, float) and val < 7.5:
            background_color = '#D3D3D3'
            font_color = 'black'
        else:
            background_color = 'blue'
            font_color = 'white'
        return f'background-color: {background_color}; color: {font_color}'

    # Apply the color formatting to the DataFrame
    styled_df = all_data_df.style.map(color_cells)

    # Apply a different style to the 'Barcode' column
    styled_df = styled_df.apply(
        lambda x: ['background-color: white; color: black'
                   if x.name == 'Barcode' else '' for _ in x], axis=0
    )

    # Define CSS
    css = """
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
            font-family: Arial, sans-serif;
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
            text-align: center;  # Center the text in the cells
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
    </style>
    """

    # Save the styled DataFrame to an HTML file
    with open(output_path, 'w') as f:
        f.write(css)
        f.write(styled_df.to_html())  # Use to_html without index=False


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


def html_to_pdf(html_file_path, pdf_file_path):
    """
    Convert an HTML file to a PDF document.

    Parameters:
    html_file_path (str): The path to the HTML file.
    pdf_file_path (str): The path to the output PDF file.
    """
    HTML(html_file_path).write_pdf(pdf_file_path)


def pdf_to_png(pdf_file_path, png_file_path):
    """
    Convert a PDF file to a PNG image.

    Parameters:
    pdf_file_path (str): The path to the PDF file.
    png_file_path (str): The path to the output PNG file.
    """
    # Open the PDF file
    doc = fitz.open(pdf_file_path)

    # Get the first page of the PDF
    page = doc.load_page(0)

    # Render the page to a pixmap with a transparent background
    pixmap = page.get_pixmap(alpha=True)

    # Save the pixmap to a PNG file
    pixmap.save(png_file_path)  # Corrected from 'writePNG' to 'save'


def main(folder_path, output_folder):
    """
    Main function to process all CSV files in a folder grouped by iteration.

    Parameters:
    folder_path (str): The path to the folder.
    output_folder (str): The path to the output folder.
    """
    # Get all CSV files in the folder
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

    # Extract iteration and barcode from each CSV file name
    csv_files_info = []
    for csv_file in csv_files:
        iteration_match = re.search(r'iteration(\d+)', csv_file)
        barcode_match = re.search(r'barcode(\d+)', csv_file)
        if iteration_match and barcode_match:
            csv_files_info.append(
                (
                    csv_file, int(iteration_match.group(1)),
                    int(barcode_match.group(1))
                )
            )

    # Sort the CSV files first by iteration and then by barcode
    csv_files_info.sort(key=lambda x: (x[1], x[2]))

    # Initialize the current iteration and the all_data list
    current_iteration = None
    all_data = []

    for csv_file, iteration, _ in csv_files_info:
        # If the iteration has changed, clear all_data
        if iteration != current_iteration:
            all_data = []

        df = parse_csv_file(csv_file)
        data_dict = create_data_dict(df, csv_file)
        all_data.append(data_dict)

        # Create the output path
        output_path = os.path.join(
            output_folder, f'iteration_{iteration}.html'
        )

        visualize_data(pd.DataFrame(all_data), output_path)

        remove_index_from_html(output_path)

        # Convert the HTML file to a PDF document
        pdf_file_path = os.path.join(
            output_folder, f'iteration_{iteration}.pdf'
        )
        html_to_pdf(output_path, pdf_file_path)

        # Convert the PDF file to a PNG image
        png_file_path = os.path.join(
            output_folder, f'iteration_{iteration}.png'
        )
        pdf_to_png(pdf_file_path, png_file_path)

        # Update the current iteration
        current_iteration = iteration


if __name__ == "__main__":
    main('/home/adamkoziol/Bioinformatics/poresippr_gui/poresippr_out/',
         '/home/adamkoziol/Bioinformatics/poresippr_gui/images')
