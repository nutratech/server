SHELL=/bin/bash

.DEFAULT_GOAL := _help

# NOTE: must put a <TAB> character and two pound "\t##" to show up in this list.  Keep it brief! IGNORE_ME
.PHONY: _help
_help:
	@grep -h "##" $(MAKEFILE_LIST) | grep -v IGNORE_ME | sed -e 's/##//' | column -t -s $$'\t'



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# init, venv, and deps
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# TODO: should this just be "python3"?
PY_SYS_INTERPRETER ?= python3
PY_VIRTUAL_INTERPRETER ?= python

.PHONY: init
init:	## Set up a Python virtual environment
	git submodule update --init
	$(PY_SYS_INTERPRETER) -m venv .venv
	- direnv allow
	@echo NOTE: activate venv, and run 'make deps'
	@echo HINT: run 'source .venv/bin/activate'

PYTHON ?= $(shell which python)
PWD ?= $(shell pwd)
.PHONY: _venv
_venv:
	# Test to enforce venv usage across important make targets
	[ "$(PYTHON)" = "$(PWD)/.venv/bin/python" ] || [ "$(PYTHON)" = "$(PWD)/.venv/Scripts/python" ]

PIP ?= $(PY_VIRTUAL_INTERPRETER) -m pip
.PHONY: _deps
_deps:
	$(PIP) install wheel
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-test.txt
	$(PIP) install -r requirements-lint.txt

.PHONY: deps
deps: _venv	## Install requirements
deps: _deps



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Test
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TEST_HOME := tests/
IT_HOME := tests/integration/it*
.PHONY: _test
_test:
	coverage run -m pytest -v -s -p no:cacheprovider -o log_cli=true $(TEST_HOME)
	coverage report

.PHONY: test
test: _venv	## Run unit tests
test: _test



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Lint
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.PHONY: _format
_format:
	isort $(LINT_LOCS)
	autopep8 --recursive --in-place --max-line-length 88 $(LINT_LOCS)
	black $(LINT_LOCS)

.PHONY: format
format: _venv	## Format Python files
format: _format


APP_HOME := ntserv/
LINT_LOCS := $(APP_HOME) $(TEST_HOME) setup.py
YAML_LOCS := .*.yml .github/
RST_LOCS := *.rst

.PHONY: _lint
_lint:
	# check formatting: Python
	pycodestyle --max-line-length=88 --statistics $(LINT_LOCS)
	autopep8 --recursive --diff --max-line-length 88 --exit-code $(LINT_LOCS)
	isort --diff --check $(LINT_LOCS)
	black --check $(LINT_LOCS)
	# lint RST
	doc8 --quiet $(RST_LOCS)
	# lint YAML
	yamllint $(YAML_LOCS)
	# lint Python
	bandit -q -c .banditrc -r $(LINT_LOCS)
	mypy $(LINT_LOCS)
	flake8 --statistics --doctests $(LINT_LOCS)
	pylint $(LINT_LOCS)

.PHONY: lint
lint: _venv	## Lint code and documentation
lint: _lint



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Run
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.PHONY: _run
_run:
	$(PY_VIRTUAL_INTERPRETER) -m ntserv

.PHONY: run
run: _venv	## Start the server
run: _run



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Build & Install
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.PHONY: build
build: _venv	## Create an sdist
	$(PY_VIRTUAL_INTERPRETER) setup.py sdist


.PHONY: install
install:	## Pip install (user)
	echo COMMIT_SHA = \"$(shell git rev-parse --short HEAD)\" >ntserv/__sha__.py
	echo COMMIT_DATE = \"$(shell git show -s --format=%cs)\" >>ntserv/__sha__.py
	$(PY_SYS_INTERPRETER) -m pip install .



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Clean
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.PHONY: clean
clean:	## Clean up __pycache__ and leftover bits
	rm -f .coverage
	rm -rf .mypy_cache/ .pytest_cache/
	find $(APP_HOME) $(TEST_HOME) -name __pycache__ -o -name .pytest_cache | xargs rm -rf



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Extras
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CLOC_ARGS ?=

.PHONY: extras/cloc
extras/cloc:	## Count lines of source code
	- cloc \
	--exclude-dir=\
	.venv,venv,\
	.mypy_cache,.pytest_cache,\
	.idea,\
	build,dist \
	--exclude-ext=svg \
	$(CLOC_ARGS) \
	.
