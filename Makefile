.PHONY := pylint man test all
.DEFAULT_GOAL := all
PY = $(shell which python3)

pylint:
	-@$(PY) -m pylint $(shell find tchess -type f -name '*.py') test.py

manpage:
	-@$(PY) bin/generate-man-page.py

test:
	@$(PY) test.py

all: pylint manpage test
	-@git status
