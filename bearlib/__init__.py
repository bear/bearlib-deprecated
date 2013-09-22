#!/usr/bin/env python

"""
bearlib

:copyright: (c) 2012 by Mike Taylor
:license: BSD, see LICENSE for more details.

"""

VERSION = (0, 5, 2, "alpha")

__author__    = 'bear (Mike Taylor)'
__contact__   = 'bear@bear.im'
__copyright__ = 'Copyright 2012, Mike Taylor'
__license__   = 'BSD 2-Clause'
__site__      = 'https://github.com/bear/bearlib'
__version__   = u'.'.join(map(str, VERSION[0:3])) + u''.join(VERSION[3:])

import os
import os.path
import sys
import json
import types
import logging

from optparse import OptionParser

_ourPath = os.getcwd()
_ourName = os.path.splitext(os.path.basename(sys.argv[0]))[0]

log = logging.getLogger('bearlib')
log.addHandler(logging.NullHandler())


def bLogs(logname, echo=True, debug=False, chatty=False, loglevel=logging.INFO, logpath=None, fileHandler=None):
    """ Initialize logging
    """

    log = logging.getLogger(logname)

    if fileHandler is None:
        if logname is None:
            logFilename = _ourName
        else:
            logFilename = logname

        if '.log' not in logFilename:
            logFilename = '%s.log' % logFilename

        if logpath is not None:
            logFilename = os.path.join(logpath, logFilename)

        _handler   = logging.FileHandler(logFilename)
        _formatter = logging.Formatter('%(asctime)s %(levelname)-7s %(message)s')

        _handler.setFormatter(_formatter)
        log.addHandler(_handler)
        # logging.fileHandler = _handler
    else:
        log.addHandler(fileHandler)
        # logging.fileHandler = fileHandler

    if echo:
        echoHandler = logging.StreamHandler()
        if chatty:
            echoFormatter = logging.Formatter('%(asctime)s %(levelname)-7s %(processName)s[%(process)d]: %(message)s')
        else:
            echoFormatter = logging.Formatter('%(asctime)s %(levelname)-7s %(message)s')
        echoHandler.setFormatter(echoFormatter)
        log.addHandler(echoHandler)

    if debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(loglevel)

class bConfig(object):
    def __init__(self, config=None, filename=None, defaults=None):
        """ Parse command line parameters and populate the options object
        """
        self.appPath  = _ourPath
        self.filename = filename
        self._config  = { 'configFile':  ('-c', '--config',  self.filename,       'Configuration Filename (optionally w/path'),
                          'debug':       ('-d', '--debug',   False,               'Enable Debug'),
                          'echo':        ('-e', '--echo',    False,               'Enable log echo to the console'),
                          'logpath':     ('-l', '--logpath', '',                  'Path where log file is to be written'),
                          'logfile':     ('',   '--logfile', '%s.log' % _ourName, 'log filename'),
                          'verbose':     ('-v', '--verbose', False,               'show extra output from remote commands'),
                        }

        if config is not None and type(config) is types.DictType:
            for key in config:
                self._config[key] = config[key]

        if defaults is not None and type(defaults) is types.DictType:
            self._defaults = defaults
        else:
            self._defaults = {}

        self.load()

    def findConfigFile(self, paths=None, envVar=None):
        searchPaths = []

        if paths is not None:
            for path in paths:
                searchPaths.append(path)

        for path in (_ourPath, os.path.expanduser('~')):
            searchPaths.append(path)
        
        if envVar is not None and envVar in os.environ:
            path = os.environ[envVar]
            searchPaths.append(path)

        for path in searchPaths:
            s = os.path.join(path, self.filename)
            if os.path.isfile(s):
                self.filename = s

    def addConfig(self, key, shortCmd='', longCmd='', defaultValue=None, helpText=''):
        if len(shortCmd) + len(longCmd) == 0:
            raise Exception('You must provide either a shortCmd or a longCmd value - both cannot be empty')
        elif key is None and type(key) is types.StringType:
            raise Exception('The configuration key must be a string')
        else:
            self._config[key] = (shortCmd, longCmd, defaultValue, helpText)

    def load(self, configPaths=None, configEnvVar=None):
        parser = OptionParser()

        for key in self._config:
            shortCmd, longCmd, defaultValue, helpText = self._config[key]

            if key in self._defaults:
                defaultValue = self._defaults[key]

            if type(defaultValue) is types.BooleanType:
                parser.add_option(shortCmd, longCmd, dest=key, action='store_true', default=defaultValue, help=helpText)
            else:
                parser.add_option(shortCmd, longCmd, dest=key, default=defaultValue, help=helpText)

        (self.options, self.args) = parser.parse_args()

        self.filename = getattr(self.options, 'configFile', self.filename)

        if self.filename is not None:
            self.findConfigFile(configPaths, configEnvVar)
            config = self.loadJson(self.filename)

            for key in config:
                setattr(self.options, key, config[key])

    def loadJson(self, filename):
        """ Read, parse and return given Json config file
        """
        jsonConfig = {}
        if os.path.isfile(filename):
            try:
                jsonConfig = json.loads(' '.join(open(filename, 'r').readlines()))
            except:
                raise Exception('error during loading of config file [%s]' % filename)
        return jsonConfig
