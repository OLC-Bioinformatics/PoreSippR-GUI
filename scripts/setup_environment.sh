#!/usr/bin/env bash
# Install the environment, Dorado, and a basecalling model.
# Stop if an installation command fails.
set -e

# Work from the project folder, one level above this script.
cd "$(dirname "$0")/.."
conda_bin="${1:-conda}"
env_prefix="${2:-$PWD/.env}"
dorado_version=2.1.2
model=dna_r10.4.1_e8.2_400bps_fast@v5.2.0
tools_dir="$PWD/.tools"
models_dir="$tools_dir/models"

if ! command -v "$conda_bin" >/dev/null; then
    echo "Conda was not found. Install Miniconda or Miniforge first."
    exit 1
fi

# Reuse an existing Conda environment or create one for this checkout.
if [[ -f "$env_prefix/conda-meta/history" ]]; then
    "$conda_bin" env update --prefix "$env_prefix" --file environment.yml
else
    "$conda_bin" env create --prefix "$env_prefix" --file environment.yml --yes
fi
export PATH="$env_prefix/bin:$PATH"
# Save the PDF library path in the environment so make run can stay simple.
"$conda_bin" env config vars set --prefix "$env_prefix" LD_LIBRARY_PATH="$env_prefix/lib"
mkdir -p "$tools_dir" "$models_dir"

# Reuse Dorado if it is installed, otherwise download it into .tools.
if command -v dorado >/dev/null; then
    dorado="$(command -v dorado)"
else
    dorado="$tools_dir/dorado-$dorado_version-linux-x64/bin/dorado"
fi
if [[ ! -x "$dorado" ]]; then
    archive="$tools_dir/dorado-$dorado_version.tar.gz.part"
    # Remove the temporary download when the script exits.
    trap 'rm -f -- "$archive"' EXIT
    curl --fail --location --retry 3 \
        "https://cdn.oxfordnanoportal.com/software/analysis/dorado-$dorado_version-linux-x64.tar.gz" \
        --output "$archive"
    tar -xzf "$archive" -C "$tools_dir"
fi

"$dorado" --version
# Put Dorado on the environment's PATH for the GUI.
if [[ "$dorado" != "$env_prefix/bin/dorado" ]]; then
    ln -sfn "$dorado" "$env_prefix/bin/dorado"
fi

if [[ ! -f "$models_dir/$model/config.toml" ]]; then
    "$dorado" download --model "$model" --models-directory "$models_dir"
fi
test -f "$models_dir/$model/config.toml"

# Check Python package requirements and show the mapping tool versions.
"$conda_bin" run --prefix "$env_prefix" python -m pip check
"$conda_bin" run --prefix "$env_prefix" minimap2 --version
"$conda_bin" run --prefix "$env_prefix" samtools --version
echo "Setup finished. Start the GUI with: make run"
