# -*- coding: utf-8 -*-
"""
:copyright: (c) 2012-2020 by Mike Taylor
:license: CC0 1.0 Universal, see LICENSE for more details.

Events class to allow event handlers
to be called for named events.

Events can be discovered via a handler path
or explicitely registered.

Nothing fancy, just needed a way to get python code to be run
from some of the IndieWeb helper Flask tools, see the
[Kaku]() project for an example of how it is used.

A handler is a .py file that contains at a minimum a 'setup' method.

The name of the .py file will become the 'eventClass' and used
to store the handler. Event names will get mapped to defined
methods within the handler's .py file.

For example.py:
    # example.py handler - it's eventClass will be 'example'
    def setup():
        pass
    # eventName 'foo'
    def foo(*args):
        pass
"""

import os
import sys
import importlib
from importlib import resources


_ourPath = os.getcwd()
_ourName = os.path.splitext(os.path.basename(sys.argv[0]))[0]


class Events():
    def __init__(self, handlersPath=_ourPath):
        self.handlers = {}
        self.handlersPath = os.path.abspath(os.path.expanduser(handlersPath))
        self.loadHandlers()

    def loadHandlers(self):
        files = resources.contents('./tests/test_event_handlers')
        plugins = [f[:-3] for f in files if f.endswith(".py") and f[0] != "_"]
        print(plugins)
        for plugin in plugins:
            print(f'{plugin}')
            module = importlib.import_module(f"'test_event_handlers'.{plugin}")
            print(module)
            if hasattr(module, 'setup'):
                self.handlers[f"'test_event_handlers'.{plugin}"] = module
        print(self.handlers)

    def handle(self, eventClass, eventName, *args):
        eventClass = eventClass.lower()
        if eventClass in self.handlers:
            module = self.handlers[eventClass]
            if hasattr(module, eventName):
                return getattr(module, eventName)(*args)
        return None
