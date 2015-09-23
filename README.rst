bearlib

A simple collection of helper routines that I use in a lot of projects.

.. image:: https://pypip.in/wheel/bearlib/badge.png
    :target: https://pypi.python.org/pypi/bearlib/
    :alt: Wheel Status


I used to just copy the directory into each project...

yes, a build/release person was breaking *all* the rules - *sigh*

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
Right now I'm going to use a very simple "plugin" style for event hanlders where any .py file found in a directory is imported as a module.

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
