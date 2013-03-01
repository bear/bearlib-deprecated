init:
	pip install distribute
	pip install nose
	pip install docutils
	pip install -r requirements.txt
	pip install -e .

refresh:
	pip install --upgrade -e .

test:
	nosetests tests

upload: check
	python setup.py sdist upload

clean:
	python setup.py clean

distclean: clean dist

dist: check
	python setup.py sdist

check:
	python setup.py check