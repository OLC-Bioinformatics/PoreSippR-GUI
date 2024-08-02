from cx_Freeze import setup, Executable
from pathlib import Path

# Import the version from version.py
from version import __version__

def collect_files_and_folders(directory, base_dir):
    """
    Collect all files and folders in the given directory and return their
    absolute and relative paths.

    :param directory: The directory to traverse.
    :param base_dir: The base directory to calculate relative paths.
    :return: A list of tuples containing absolute and relative paths.
    """
    collected_items = []
    base_path = Path(base_dir).resolve()
    for path in Path(directory).rglob('*'):
        norm_path = path.resolve()
        rel_path = norm_path.relative_to(base_path)
        if norm_path.is_file():
            collected_items.append((str(norm_path), str(rel_path)))
    return collected_items

# Collect files and folders from specified directories
config_files = collect_files_and_folders('config', 'config')
fonts_files = collect_files_and_folders('fonts', 'fonts')
icons_files = collect_files_and_folders('icons', 'icons')
venv_files = collect_files_and_folders('/home/adamkoziol/miniconda/envs/poresippr_gui', '/home/adamkoziol/miniconda/envs/poresippr_gui')

# Define build options for cx_Freeze
build_options = {
    'packages': [],
    'excludes': ['importlib_resources'],
    'include_files': [
        ('cfia.jpg', '.'),
        ('CFIA_logo.png', '.'),
        ('methods.py', '.'),
        ('poresippr_basecall_scheduler.py', '.'),
        ('poresippr_placeholder.py', '.'),
        ('report_template.html', '.'),
        ('ui_main.py', '.'),
        ('version.py', '.'),
        *config_files,
        *fonts_files,
        *icons_files,
        *venv_files,
    ],
}

# Define executables for cx_Freeze
executables = [
    Executable('main.py', base=None, target_name='PoreSippr', icon='cfia.jpg')
]

# Setup the build using cx_Freeze
setup(
    name='PoreSippr',
    version=__version__,
    description='PoreSippr Application',
    options={'build_exe': build_options},
    executables=executables
)