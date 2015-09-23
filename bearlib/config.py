# -*- coding: utf-8 -*-
"""
:copyright: (c) 2012-2015 by Mike Taylor
:license: MIT, see LICENSE for more details.

Config class that can be accessed using attributes.
Has helper methods to load from etcd and json.

Can be initialized using a dictionary.
"""

import os, sys
import json
try:
    import etcd
    _etcd = True
except:
    _etcd = False

from optparse import OptionParser

_ourPath = os.getcwd()
_ourName = os.path.splitext(os.path.basename(sys.argv[0]))[0]


def findConfigFile(filename, paths=None, envVar=None):
    searchPaths = []
    result      = []

    if paths is not None:
        for path in paths:
            searchPaths.append(path)

    for path in (_ourPath, os.path.expanduser('~')):
        searchPaths.append(path)
    
    if envVar is not None and envVar in os.environ:
        path = os.environ[envVar]
        searchPaths.append(path)

    for path in searchPaths:
        s = os.path.join(path, filename)
        if os.path.isfile(s):
            result.append(s)

    return result

# derived from https://stackoverflow.com/a/3031270
class Config(dict):
    marker = object()
    def __init__(self, value=None):
        if value is None:
            pass
        elif isinstance(value, dict):
            self.fromDict(value)
        else:
            raise TypeError, 'expected dict'

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, Config):
            value = Config(value)
        elif isinstance(value, list):
            items = []
            for item in value:
                if isinstance(item, dict) and not isinstance(value, Config):
                    items.append(Config(item))
                else:
                    items.append(item)
            value = items
        dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        found = self.get(key, Config.marker)
        if found is Config.marker:
            found = Config()
            dict.__setitem__(self, key, found)
        return found

    __setattr__ = __setitem__
    __getattr__ = __getitem__

    def fromDict(self, d):
        if isinstance(d, dict):
            for key in d:
                self.__setitem__(key, d[key])

    def _readEtcd(self, etcdClient, base, parent=None):
        result = {}
        if parent is None:
            n = len(base)
        else:
            n = len(parent) + 1

        items = etcdClient.read(base, recursive=False)
        for leaf in items.leaves:
            key = leaf.key[n:]
            if leaf.dir:
                value = self._readEtcd(etcdClient, leaf.key, leaf.key)
            else:
                value = leaf.value
            result[key] = value

        return result

    def fromEtcd(self, host='127.0.0.1', port=4001, base='/'):
        if _etcd:
            e = etcd.Client(host=host, port=port, allow_redirect=False, allow_reconnect=False)
            r = self._readEtcd(e, base)
            self.fromDict(r)
        else:
            raise Exception('python-etcd is not available')

    def fromJson(self, configFilename):
        filename = os.path.expanduser(configFilename)
        filename = os.path.abspath(filename)

        if os.path.exists(filename):
            with open(filename, 'r') as h:
                r = json.load(h)
                self.fromDict(r)


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
            jsonConfig = json.loads(' '.join(open(filename, 'r').readlines()))
        return jsonConfig


