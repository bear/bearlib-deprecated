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
	@echo "  clean       remove unwanted files"
	@echo "  lint        flake8 lint check"
	@echo "  test        run unit tests"
	@echo "  integration run integration tests"
	@echo "  check       check if project is ready for packaging"
	@echo "  upload      upload project to PyPI"
	@echo "  dist        build source distribution"
	@echo "  all         refresh and run all tests and generate coverage reports"

clean:
	rm -fr build
	rm -fr dist
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;

lint: clean
	pipenv run flake8 --exclude=env . > violations.flake8.txt

test: lint
	pipenv run python setup.py test --addopts "--ignore=venv"

coverage: clean lint
	pipenv run coverage run --source=bearlib setup.py test --addopts "--ignore=venv"
	pipenv run coverage html
	pipenv run coverage report

ci: clean lint coverage
	@CODECOV_TOKEN=$(CODECOV_TOKEN) && pipenv run codecov

check: ci
	pipenv run check-manifest
	pipenv run python setup.py check

upload: check
	pipenv run python setup.py sdist upload
	pipenv run python setup.py bdist_wheel upload

dist: check
	pipenv run python setup.py sdist

all: clean update-all lint integration coverage
