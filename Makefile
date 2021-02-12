.PHONY := pylint
PY = $(shell which python3)

pylint:
	-@$(PY) -m pylint $(shell find tchess -type f -name '*.py') test.py
