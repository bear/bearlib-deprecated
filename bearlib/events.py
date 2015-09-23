# -*- coding: utf-8 -*-
"""
:copyright: (c) 2012-2015 by Mike Taylor
:license: MIT, see LICENSE for more details.

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

import os, sys
import imp

_ourPath = os.getcwd()
_ourName = os.path.splitext(os.path.basename(sys.argv[0]))[0]

class Events(object):
    def __init__(self, handlersPath=_ourPath):
        self.handlers     = {}
        self.handlersPath = os.path.abspath(os.path.expanduser(handlersPath))
        self.loadHandlers()

    def loadHandlers(self):
        for (dirpath, dirnames, filenames) in os.walk(self.handlersPath):
            for filename in filenames:
                moduleName, moduleExt = os.path.splitext(os.path.basename(filename))
                if moduleExt == '.py':
                    module = imp.load_source(moduleName, os.path.join(self.handlersPath, filename))
                    if hasattr(module, 'setup'):
                        self.handlers[moduleName.lower()] = module

    def handle(self, eventClass, eventName, *args):
        eventClass = eventClass.lower()
        if eventClass in self.handlers:
            module = self.handlers[eventClass]
            try:
                if hasattr(module, eventName):
                    return getattr(module, eventName)(*args)
            except Exception, e:
                raise Exception('error during call %s.%s(%s)' % (eventClass, eventName, ','.join(args)))
