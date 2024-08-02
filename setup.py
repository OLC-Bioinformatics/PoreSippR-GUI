"""
Setup script for the PoreSippr package.
"""

from setuptools import setup

# Import the version from version.py
from version import __version__

# Read dependencies from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Set up the package
setup(
    name='PoreSippr',
    version=__version__,
    description='PoreSippr Application',
    long_description='PoreSippr is a GUI application for processing and "'
                     '"analyzing MinION sequencing data in real-time.',
    author='Adam Koziol',
    author_email='adam.koziol@inspection.gc.ca',
    url='https://github.com/OLC-Bioinformatics/PoreSippr',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    packages=['poresippr'],
    include_package_data=True,
    install_requires=requirements,
)
