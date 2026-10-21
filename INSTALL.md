# Install and run

## Before you start

Use Linux x86_64 Ubuntu. Install Git, GNU Make, and either
Miniconda or Miniforge. Check that Conda is available with `conda --version`.
Setup needs internet access and disk space for the environment, Dorado, and
the basecalling model. GPU basecalling also needs a supported NVIDIA GPU and
a compatible driver installed by your system administrator.

```bash
git clone --branch amin_updates https://github.com/OLC-Bioinformatics/PoreSippR-GUI.git poresippr
cd poresippr
make setup
make run
```

## What the commands do

`make setup` creates a Conda environment in `.env` and installs:

- Python 3.12 and the Python packages in `requirements.txt`.
- minimap2 and samtools.
- Libraries needed for PDF reports and the GUI.
- Dorado 2.1.2, when an installed Dorado is not already available.
- The R10.4.1/E8.2 400 bps FAST model, version 5.2.0.

The Conda packages are listed in `environment.yml`. Downloads and models go
in `.tools`. Running setup again reuses the environment, installed Dorado,
and existing model directory. Unrelated packages in the environment are kept.

Setup prints the tool versions and checks Python package requirements.
If a step fails, setup stops at that step.

`make run` launches the GUI using `.env`, manual env activation is no longer necessary.


## Change an installation location

If Conda is not on PATH, provide its location:

```bash
make setup CONDA=/path/to/conda
make run CONDA=/path/to/conda
```

Use `ENV_PREFIX=/path/to/environment` with both commands to choose another
environment. The Dorado version and model are set near the top of
`scripts/setup_environment.sh`.

