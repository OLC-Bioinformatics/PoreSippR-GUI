# added by Amin
# to automate setup and run

# Keep the project's packages in its own Conda environment.
CONDA ?= conda
ENV_PREFIX ?= $(CURDIR)/.env
# Save the program's messages and errors here. Each run starts a new log.
LOG_FILE ?= $(CURDIR)/run_poresippr.log

.PHONY: setup run clean

# Install dependencies, prepare Dorado and its model, then check the setup.
setup:
	bash scripts/setup_environment.sh "$(CONDA)" "$(ENV_PREFIX)"

# Start the GUI using the environment created by make setup.
# --prefix selects .env, even if another environment is active in your terminal.
run:
	"$(CONDA)" run --prefix "$(ENV_PREFIX)" python src/poresippr/main.py > "$(LOG_FILE)" 
clean:
	echo "cleaning"
