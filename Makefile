.PHONY := pylint man test all
.DEFAULT_GOAL := all
PY = $(shell which python3)

pylint:
	-@$(PY) -m pylint $(shell find tchess -type f -name '*.py') test.py

manpage:
	-@$(PY) bin/generate-man-page.py

test:
	@$(PY) test.py

all: manpage test todo
	-@git status

clean:
	@rm dist build *.egg-info venv -rf

dep: clean
	@$(PY) setup.py sdist bdist_wheel
	#@$(PY) -m twine upload dist/*

todo:
	@for f in $(shell find tchess bin -type f -name '*.py') test.py bin/tchess; do \
		TODO=$$(cat $$f | grep 'TODO'); \
		if [ "$$TODO" != "" ]; then \
			echo $$f:; \
			cat $$f | grep 'TODO'; \
			echo ---------------; \
		fi; \
	done; \
