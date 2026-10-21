# added by Amin
# to automate setup and run
# Use the Python from your activated environment.
PYTHON ?= python

.PHONY: setup run

setup:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) main.py
