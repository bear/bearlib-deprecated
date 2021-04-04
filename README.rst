bearlib

.. image:: https://circleci.com/gh/bear/bearlib.svg?style=svg
    :target: https://circleci.com/gh/bear/bearlib
    :alt: Build Status
.. image:: https://requires.io/github/bear/bearlib/requirements.svg?branch=master
    :target: https://requires.io/github/bear/bearlib/requirements/?branch=master
    :alt: Requirements Status
.. image:: https://img.shields.io/pypi/wheel/bearlib.svg
    :target: https://pypi.python.org/pypi/bearlib/
    :alt: Wheel Status
.. image:: https://codecov.io/github/bear/bearlib/coverage.svg?branch=master
    :target: https://codecov.io/github/bear/bearlib?branch=master
    :alt: CodeCov Report

A simple collection of helper routines that I use in a lot of projects.

NOTE: As of version 0.10 this is a Python 3 only module

Config
======

A dictionary based config class::

    c = Config({ 'a': 1, 'b': 2, 'c': {'d': 1}}
    print("c.a =", c.a)
    print("c.c.d" =", c.c.d)

generates::

    c.a = 1
    c.c.d = 1

It also has three helper methods::

    fromDict(dictionary)
    fromJson(filename)
    fromEtcd(host='127.0.0.1', port=4001, base='/')

fromDict() walks thru the keys of the given dictionary recursively and adds them
to the object. Any key found that has a list or dictionary value is handled with
instances of Config created as needed.

fromJson() uses json.load() to process the given filename and then calls fromDict()
to store the values.

fromEtcd() walks the directory tree at the base location in the etcd server, builds
a dictionary and then passes that to fromDict() for storage.

Events
======
Right now I'm going to use a very simple "plugin" style for event handlers where any .py file found in a directory is imported as a module.

This will, I think, let me use the event plugins via the command line, but also via WebHooks because I can create a Flask listener for WebHook urls and then call the defined handler for a given event.

Install
=======
from PyPI::

    pip install bearlib

from git::

    cd /base/of/your/virtualenv
    pip install -e git+https://github.com/bear/bearlib.git#egg=bearlib

to update the from-git install:

    cd /base/of/your/virtualenv
    pip install --upgrade -e git+https://github.com/bear/bearlib.git#egg=bearlib

Tests
=====
From the source directory::

    make test
