.PHONY: test all
.DEFAULT_GOAL := default_target

PROJECT_NAME := pyroot
PYTHON_VERSION := 3.6.6
VENV_NAME := $(PROJECT_NAME)-$(PYTHON_VERSION)

setup:
	pip install -r requirements.txt

test:
	pytest -v --cov=src --cov-fail-under=70 --cov-report=term-missing --cov-report=html

.create-venv:
	pyenv install -s $(PYTHON_VERSION)
	pyenv uninstall -f $(VENV_NAME)
	pyenv virtualenv $(PYTHON_VERSION) $(VENV_NAME)
	pyenv local $(VENV_NAME)

create-venv: .create-venv setup

.clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

.clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr reports/
	rm -fr .pytest_cache/
	rm -f coverage.xml

clean: .clean-build .clean-pyc .clean-test ## remove all build, test, coverage and Python artifacts

release: clean
	python setup.py sdist dist_wheel

upload: release
	twine upload dist/*

all: setup test

default_target:  test