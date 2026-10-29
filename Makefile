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
	"$(CONDA)" run --no-capture-output --prefix "$(ENV_PREFIX)" python -u src/poresippr/main.py > "$(LOG_FILE)" 2>&1 || { \
		echo "See $(LOG_FILE) for errors."; \
		exit 1; \
	}
	
.PHONY: list-runs clean-analysis clean-runs clean

# Show the available analysis folders.
list-runs:
	@ls -d runs/MIN-*/analysis_*

# Delete the analysis supplied on the command line.
clean-analysis:
	@test -n "$(ANALYSIS)" || { echo "Specify ANALYSIS=MIN-YYYYMMDD/analysis_YYYYMMDD_HHMMSS"; exit 1; }
	rm -rf -- "runs/$(ANALYSIS)"

# Delete all analysis folders, keeping runs/README.md.
clean-runs:
	rm -rf -- runs/MIN-*/analysis_*

# Delete generated outputs from the old folder layout.
clean:
	rm -rf -- MIN-20260421 references/MIN-20260421 references/images references/output references/reports output/processed
	rm -f -- images/iteration_*.html reports/MIN-*_report.pdf

