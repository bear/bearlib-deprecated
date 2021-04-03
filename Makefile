.PHONY: help clean

help:
	@echo "  env         install all production dependencies"
	@echo "  clean       remove unwanted stuff"
	@echo "  lint        check style with pycodestyle"
	@echo "  test        run tests"
	@echo "  coverage    run codecov"

env:
	pipenv install --dev
	pipenv install black --dev --pre
	pipenv install "-e ."

info:
	@pipenv run python --version
	@pipenv check
	@pipenv graph

clean:
	rm -rf build
	rm -rf dist
	rm -f violations.flake8.txt
	pipenv clean
	pipenv install

lint: clean
	pipenv run flake8 --tee --output-file=violations.flake8.txt

test: lint
	pipenv install "-e ."
	pipenv run pytest

coverage: clean
	pipenv run coverage run -m pytest
	pipenv run coverage report
	pipenv run coverage html
	pipenv run codecov

check: clean
	pipenv run check-manifest -v

dist: check
	pipenv run python -m build

upload: dist
	pipenv run python -m twine upload dist/*
