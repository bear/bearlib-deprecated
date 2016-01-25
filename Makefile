.PHONY: help clean

ifeq ($(wildcard .codecov-token),)
  TOKEN = source .codecov-token
else
	TOKEN =
endif

guard-%:
	@ if [ "${${*}}" == "" ]; then \
	  echo "Environment variable $* not set"; \
	fi

help:
	@echo "This project assumes that an active Python virtualenv is present."
	@echo "The following make targets are available:"
	@echo "  update      update python dependencies"
	@echo "  clean       remove unwanted files"
	@echo "  lint        flake8 lint check"
	@echo "  test        run unit tests"
	@echo "  integration run integration tests"
	@echo "  check       check if project is ready for packaging"
	@echo "  upload      upload project to PyPI"
	@echo "  dist        build source distribution"
	@echo "  all         refresh and run all tests and generate coverage reports"

update: guard-PYENV_VIRTUALENV_INIT
	pip install -U pip
	pip install -Ur requirements.txt

update-all: guard-PYENV_VIRTUALENV_INIT update
	pip install -Ur requirements-test.txt

clean:
	rm -fr build
	rm -fr dist
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;

lint: clean
	flake8 --exclude=env . > violations.flake8.txt

test: lint
	python setup.py test

coverage: clean lint
	coverage run --source=bearlib setup.py test
	coverage html
	coverage report

ci: clean lint coverage
	@CODECOV_TOKEN=$(CODECOV_TOKEN) && codecov

check: ci
	check-manifest
	python setup.py check

upload: check
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: check
	python setup.py sdist

all: clean update-all lint integration coverage
