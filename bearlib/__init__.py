#!/usr/bin/env python

"""
bearlib

:copyright: (c) 2012 by Mike Taylor
:license: BSD, see LICENSE for more details.

"""

VERSION = (0, 5, 3, "alpha")

__author__    = 'bear (Mike Taylor)'
__contact__   = 'bear@bear.im'
__copyright__ = 'Copyright 2012, Mike Taylor'
__license__   = 'BSD 2-Clause'
__site__      = 'https://github.com/bear/bearlib'
__version__   = u'.'.join(map(str, VERSION[0:3])) + u''.join(VERSION[3:])


import os
import sys
import pwd
import grp
import json
import types
import signal
import atexit
import logging

from optparse import OptionParser


_ourPath = os.getcwd()
_ourName = os.path.splitext(os.path.basename(sys.argv[0]))[0]

log = logging.getLogger('bearlib')
log.addHandler(logging.NullHandler())

def shutdownLogging():
    logging.shutdown()

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

    atexit.register(shutdownLogging)


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


def pidWrite(pidFile):
    os.umask(077) # set umask for pid

    with open(pidFile, "w") as f:
        f.write(str(os.getpid()))

def pidRead(pidFile):
    try:
        with open(pidFile, 'r') as f:
            return int(f.read())
    except IOError:
        return -1

def pidClear(pidFile):
    if not isRunning(pidFile):
        if os.path.exists(pidFile):
            os.remove(pidFile)

def isRunning(pidFile):
    pid = pidRead(pidFile)

    if pid == -1:
        return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            log.warn('pid %d for %s found.' % (pid, pidFile))
            return False

def shutdownHandler(signal, frame):
    log.info('shutdown requested')
    sys.exit(0)

def daemonize(config):
    if not hasattr(config, 'pidfile'):
        raise Exception('pidfile is a required configuration item')
    if not hasattr(config, 'uid'):
        raise Exception('uid is a required configuration item')
    if not hasattr(config, 'gid'):
        raise Exception('gid is a required configuration item')

    if isRunning(config.pidfile):
        log.error('Our PID is still active. Exiting')
        sys.exit(1)
    else:
        if os.fork() == 0:
            os.setsid()

            signal.signal(signal.SIGHUP, signal.SIG_IGN)

            pid = os.fork()

            if pid != 0:
                os._exit(0)
            else:
                pidClear(config.pidfile)
                pidWrite(config.pidfile)
        else:
            os._exit(0)

    signal.signal(signal.SIGINT,  shutdownHandler)
    signal.signal(signal.SIGTERM, shutdownHandler)

    if os.getuid() != 0:
        return

    uid = pwd.getpwnam(config.uid).pw_uid
    gid = grp.getgrnam(config.gid).gr_gid

    os.setgroups([])

    os.setgid(gid)
    os.setuid(uid)

    os.umask(077)

def escXML(text, escape_quotes=False):
    if type(text) != types.UnicodeType:
        if type(text) == types.IntType:
            s = str(text)
        else:
            s = text
        s = list(unicode(s, 'utf-8', 'ignore'))
    else:
        s = list(text)

    cc      = 0
    matches = ('&', '<', '"', '>')

    for c in s:
        if c in matches:
            if c == '&':
                s[cc] = u'&amp;'
            elif c == '<':
                s[cc] = u'&lt;'
            elif c == '>':
                s[cc] = u'&gt;'
            elif escape_quotes:
                s[cc] = u'&quot;'
        cc += 1
    return ''.join(s)

def relativeDelta(td):
    s = ''
    if td.days < 0:
        t = "%s ago"
    else:
        t = "in %s"

    days    = abs(td.days)
    seconds = abs(td.seconds)
    minutes = seconds / 60
    hours   = minutes / 60
    weeks   = days / 7
    months  = days / 30
    years   = days / 365

    if days == 0:
        if seconds < 20:
            s = 'just now'
        if seconds < 60:
            s = '%d seconds' % seconds
            s = t % s
        if seconds < 120:
            s = t % 'a minute'
        if seconds < 3600:
            s = '%d minutes' % minutes
            s = t % s
        if seconds < 7200:
            s = t % 'an hour'
        if seconds < 86400:
            s = '%d hours' % hours
            s = t % s
    else:
        if days == 1:
            if td.days < 0:
                s = 'yesterday'
            else:
                s = 'tomorrow'
        elif days < 7:
            s = '%d days' % days
            s = t % s
        elif days < 31:
            s = '%d weeks' % weeks
            s = t % s
        elif days < 365:
            s = '%d months' % months
            s = t % s
        else:
            s = '%d years' % years
            s = t % s

    return s
