# Useful Makefile to automate tedious tasks.
# Ref: https://python.plainenglish.io/a-python-project-checklist-91242b4a2ca3

SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --silent

.DEFAULT_GOAL := help
help: Makefile
	@grep -E '(^[a-zA-Z_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'


# =============================================================================
# Common
# =============================================================================
# Set python command executor based on current environments because `pipenv run`
# does not support `--system`, unlike `pipenv install`.
PYTHON_COMMAND_EXECUTOR := pipenv run
ifeq (${USE_DOCKER}, yes)
	PYTHON_COMMAND_EXECUTOR :=
endif

install:  ## Install the app locally
	pipenv install --dev --verbose
.PHONY: install

init:  ## Initialize project repository
	git submodule update --init
	$(PYTHON_COMMAND_EXECUTOR) pre-commit install --install-hooks
	git secret reveal || true
.PHONY: init

ci: format lint typecheck test  ## Run all checks (typecheck, lint, test)
.PHONY: ci


# =============================================================================
# Formatters
# =============================================================================
format: black isort  ## Run autoformatters
.PHONY: format

black:  ## Run black
	$(PYTHON_COMMAND_EXECUTOR) black .
.PHONY: black

isort:  ## Run isort
	$(PYTHON_COMMAND_EXECUTOR) isort .
.PHONY: isort


# =============================================================================
# Linters
# =============================================================================
lint: black-c isort-c flake8 pydocstyle  ## Run linters
.PHONY: lint

black-c:  ## Run black, without modifying files
	$(PYTHON_COMMAND_EXECUTOR) black --check .
.PHONY: black-c

isort-c:  ## Run isort, without modifying files
	$(PYTHON_COMMAND_EXECUTOR) isort -c .
.PHONY: isort-c

flake8:  ## Run flake8
	$(PYTHON_COMMAND_EXECUTOR) pflake8 .
.PHONY: flake8

pylint:  ## Run pylint
	$(PYTHON_COMMAND_EXECUTOR) pylint ./*.py config docs earlypay || true
.PHONY: pylint

pydocstyle:  ## Run pydocstyle
	$(PYTHON_COMMAND_EXECUTOR) pydocstyle . || true
.PHONY: pydocstyle


# =============================================================================
# Type Checkers
# =============================================================================
typecheck: mypy  ## Run type checkers
.PHONY: typecheck

mypy:  ## Run mypy
	$(PYTHON_COMMAND_EXECUTOR) mypy --show-error-codes --pretty .
.PHONY: mypy


# =============================================================================
# Tests
# =============================================================================
test: pytest  ## Run all tests
.PHONY: test

pytest:  ## Run pytest
	$(PYTHON_COMMAND_EXECUTOR) pytest
.PHONY: pytest

